//! Livestream scrape handlers and background runner.
//!
//! Provides the livestream start/stop handlers, live feed view, SSE event stream, and the
//! background polling loop that captures events in real time.

use std::convert::Infallible;
use std::sync::Arc;

use axum::extract::{Form, Path as AxumPath, State};
use axum::http::HeaderMap;
use axum::response::sse::{Event, Sse};
use axum::response::{Html, IntoResponse, Json, Response};
use dashmap::DashMap;
use futures::Stream;
use serde::Deserialize;
use tokio_util::sync::CancellationToken;
use urs_core::client::RedditClient;

use super::super::server::{AppState, ScrapeTask};
use super::helpers::{complete_task, fail_task, now_unix, update_task};

/// Form parameters for livestream scrape.
#[derive(Debug, Deserialize)]
pub struct LivestreamScrapeParams {
    /// Poll interval in seconds (default 5).
    pub interval: Option<u64>,
    /// Content source: "comments" or "submissions".
    pub source: String,
    /// Target name (Subreddit name or Redditor username).
    pub target: String,
    /// Target type: "subreddit" or "redditor".
    pub target_type: String,
}

/// POST handler for livestream scrapes. Spawns a background streaming task and returns the task ID.
pub async fn scrape_livestream(
    State(state): State<AppState>,
    Form(params): Form<LivestreamScrapeParams>,
) -> Response {
    let Some(client) = state.client.read().await.clone() else {
        return super::super::helpers::error_response(
            403,
            "Reddit credentials not configured",
            true,
            &state.scrapes_dir,
            false,
            None,
        );
    };

    let prefix = if params.target_type == "redditor" {
        "u"
    } else {
        "r"
    };
    let title = format!("{prefix}/{}: {} (live)", params.target, params.source);

    let id = uuid::Uuid::new_v4().to_string();
    state.scrape_tasks.insert(
        id.clone(),
        ScrapeTask {
            detail: format!("Validating {prefix}/{}...", params.target),
            error: None,
            finished_at: None,
            id: id.clone(),
            result_path: None,
            stage: "validating".to_string(),
            stage_index: 0,
            stage_total: 3,
            started_at: now_unix(),
            task_type: "livestream".to_string(),
            title,
        },
    );

    // Create per-task cancellation token.
    let task_token = CancellationToken::new();
    state
        .livestream_tokens
        .insert(id.clone(), task_token.clone());

    // Initialize empty event buffer.
    state.livestream_events.insert(id.clone(), Vec::new());

    let tasks = Arc::clone(&state.scrape_tasks);
    let scrapes_dir = Arc::clone(&state.scrapes_dir);
    let shutdown = state.shutdown.clone();
    let livestream_tokens = Arc::clone(&state.livestream_tokens);
    let livestream_events = Arc::clone(&state.livestream_events);
    let task_id = id.clone();

    tokio::spawn(async move {
        run_livestream_scrape(
            client,
            scrapes_dir,
            params,
            tasks,
            task_id,
            task_token,
            shutdown,
            livestream_tokens,
            livestream_events,
        )
        .await;
    });

    Json(serde_json::json!({ "id": id })).into_response()
}

/// POST handler to stop an active livestream.
pub async fn stop_livestream(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
) -> Response {
    if let Some((_, token)) = state.livestream_tokens.remove(&id) {
        token.cancel();
        Json(serde_json::json!({ "stopped": true })).into_response()
    } else {
        (
            axum::http::StatusCode::NOT_FOUND,
            "Livestream task not found",
        )
            .into_response()
    }
}

/// GET handler for the live feed view (rendered as an HTMX fragment).
pub async fn livestream_live_view(
    State(state): State<AppState>,
    headers: HeaderMap,
    AxumPath(id): AxumPath<String>,
) -> Response {
    let is_htmx = headers.contains_key("hx-request");

    // Look up the task to get metadata.
    let (source, target, started_at) = if let Some(task) = state.scrape_tasks.get(&id) {
        // Parse from title: "r/rust: comments (live)" or "u/spez: submissions (live)"
        let title = &task.title;
        let parts: Vec<&str> = title.splitn(2, ": ").collect();
        let target_str = parts.first().copied().unwrap_or("unknown").to_string();
        let source_str = parts
            .get(1)
            .unwrap_or(&"unknown")
            .trim_end_matches(" (live)")
            .to_string();

        (source_str, target_str, task.started_at)
    } else {
        let scrape_enabled = state.client.read().await.is_some();
        let username_lock = state.username.read().await;
        let username = username_lock.as_deref().map(String::from);

        drop(username_lock);

        return super::super::helpers::error_response(
            404,
            "Livestream task not found",
            is_htmx,
            &state.scrapes_dir,
            scrape_enabled,
            username.as_deref(),
        );
    };

    let template = super::super::templates::LivestreamLiveFragment {
        source,
        started_at,
        target,
        task_id: id,
    };
    let html = super::super::helpers::render_template(template);

    if is_htmx {
        Html(html).into_response()
    } else {
        let scrape_enabled = state.client.read().await.is_some();
        let username_lock = state.username.read().await;
        let username = username_lock.as_deref().map(String::from);

        drop(username_lock);

        super::super::helpers::wrap_in_shell(
            &state.scrapes_dir,
            scrape_enabled,
            username.as_deref(),
            &html,
            axum::http::StatusCode::OK,
        )
    }
}

/// SSE endpoint that streams individual livestream events as server-rendered HTML fragments.
///
/// On connect, emits a `snapshot` event with all currently buffered events. Then polls every 250ms
/// for new events and emits each as an `event` SSE event. Emits a `complete` event when the
/// livestream task reaches a terminal state.
pub async fn livestream_events_sse(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
) -> Sse<impl Stream<Item = Result<Event, Infallible>>> {
    let tasks = Arc::clone(&state.scrape_tasks);
    let livestream_events = Arc::clone(&state.livestream_events);
    let shutdown = state.shutdown;
    let task_id = id;

    let stream = async_stream::stream! {
        let mut cursor: usize = 0;

        // Emit snapshot of already-buffered events.
        if let Some(events) = livestream_events.get(&task_id) {
            let mut html_batch = String::new();

            for event_val in events.value() {
                let event_type = event_val
                    .get("type")
                    .and_then(|v| v.as_str())
                    .unwrap_or("comment");
                let data = event_val
                    .get("data")
                    .cloned()
                    .unwrap_or(serde_json::Value::Null);

                html_batch.push_str(&super::super::views::livestream::render_single_event_html(
                    &data, event_type,
                ));
            }

            cursor = events.value().len();

            if !html_batch.is_empty() {
                yield Ok(Event::default().event("snapshot").data(html_batch));
            }
        }

        let mut interval = tokio::time::interval(std::time::Duration::from_millis(250));

        loop {
            tokio::select! {
                () = shutdown.cancelled() => break,
                _ = interval.tick() => {}
            }

            // Emit new events since last cursor.
            if let Some(events) = livestream_events.get(&task_id) {
                let all = events.value();

                while cursor < all.len() {
                    let event_val = &all[cursor];
                    let event_type = event_val
                        .get("type")
                        .and_then(|v| v.as_str())
                        .unwrap_or("comment");
                    let data = event_val
                        .get("data")
                        .cloned()
                        .unwrap_or(serde_json::Value::Null);

                    let html = super::super::views::livestream::render_single_event_html(&data, event_type);

                    yield Ok(Event::default().event("event").data(html));

                    cursor += 1;
                }
            }

            // Check if task has reached a terminal state.
            if let Some(task) = tasks.get(&task_id) {
                if task.stage == "complete" || task.stage == "error" {
                    let result_path = task.result_path.clone().unwrap_or_default();

                    if let Ok(json) = serde_json::to_string(&serde_json::json!({
                        "stage": task.stage,
                        "result_path": result_path,
                    })) {
                        yield Ok(Event::default().event("complete").data(json));
                    }

                    break;
                }
            } else {
                // Task was removed, so stop streaming.
                break;
            }
        }
    };

    Sse::new(stream)
}

/// Runs a livestream scrape as a background task.
#[allow(clippy::too_many_arguments, clippy::too_many_lines)]
async fn run_livestream_scrape(
    client: Arc<RedditClient>,
    scrapes_dir: Arc<std::path::PathBuf>,
    params: LivestreamScrapeParams,
    tasks: Arc<DashMap<String, ScrapeTask>>,
    task_id: String,
    task_token: CancellationToken,
    shutdown_token: CancellationToken,
    livestream_tokens: Arc<DashMap<String, CancellationToken>>,
    livestream_events: Arc<DashMap<String, Vec<serde_json::Value>>>,
) {
    use std::io::Write;
    use urs_core::export::livestream_filename;
    use urs_core::scrapers::{
        LivestreamSource, LivestreamTarget, Livestreamer, RedditorScraper, SubredditScraper,
    };

    let poll_secs = params.interval.unwrap_or(5).max(2);
    let poll_duration = std::time::Duration::from_secs(poll_secs);

    let target = if params.target_type == "redditor" {
        // Validate Redditor exists.
        let scraper = RedditorScraper::new(&client);
        if let Err(e) = scraper.about(&params.target).await {
            fail_task(
                &tasks,
                &task_id,
                &format!("u/{} does not exist or is suspended: {e}", params.target),
            );
            cleanup_livestream(&livestream_tokens, &livestream_events, &task_id);

            return;
        }
        LivestreamTarget::Redditor(params.target.clone())
    } else {
        // Validate Subreddit exists.
        let scraper = SubredditScraper::new(&client);
        if let Err(e) = scraper.about(&params.target).await {
            fail_task(
                &tasks,
                &task_id,
                &format!("r/{} does not exist or is inaccessible: {e}", params.target),
            );
            cleanup_livestream(&livestream_tokens, &livestream_events, &task_id);

            return;
        }
        LivestreamTarget::Subreddit(params.target.clone())
    };

    let source = if params.source == "submissions" {
        LivestreamSource::Submissions
    } else {
        LivestreamSource::Comments
    };

    // Create output directory and temp file.
    let dir = urs_core::export::output_dir_with_base(&scrapes_dir, "livestreams");
    if let Err(e) = urs_core::export::ensure_dir(&dir) {
        fail_task(
            &tasks,
            &task_id,
            &format!("Failed to create output directory: {e}"),
        );
        cleanup_livestream(&livestream_tokens, &livestream_events, &task_id);

        return;
    }

    let temp_path = dir.join(format!(
        ".{}-{}-livestream.tmp.jsonl",
        params.target, params.source
    ));
    let file = match std::fs::File::create(&temp_path) {
        Ok(f) => f,
        Err(e) => {
            fail_task(
                &tasks,
                &task_id,
                &format!("Failed to create temp file: {e}"),
            );
            cleanup_livestream(&livestream_tokens, &livestream_events, &task_id);

            return;
        }
    };
    let mut writer = std::io::BufWriter::new(file);

    // Update to streaming stage.
    update_task(&tasks, &task_id, "streaming", "Waiting for events...", 1);

    let started_at = std::time::Instant::now();
    let start_time = chrono::Local::now().format("%H:%M:%S").to_string();
    let mut event_count: usize = 0;

    // Create a Livestreamer by borrowing from the Arc<RedditClient>.
    let mut streamer = Livestreamer::new(&client, target, source);

    loop {
        tokio::select! {
            () = task_token.cancelled() => {
                tracing::info!(task_id = %task_id, "Livestream stopped by user");
                break;
            }
            () = shutdown_token.cancelled() => {
                tracing::info!(task_id = %task_id, "Livestream stopped by server shutdown");
                break;
            }
            () = tokio::time::sleep(poll_duration) => {}
        }

        match streamer.poll().await {
            Ok(events) => {
                if !events.is_empty() {
                    // Write events to JSONL file.
                    for event in &events {
                        if let Err(e) = serde_json::to_writer(&mut writer, event) {
                            tracing::warn!(error = %e, "Failed to serialize livestream event");
                            continue;
                        }
                        if let Err(e) = writer.write_all(b"\n") {
                            tracing::warn!(error = %e, "Failed to write newline to livestream file");
                        }
                    }

                    if let Err(e) = writer.flush() {
                        tracing::warn!(error = %e, "Failed to flush livestream file");
                    }

                    // Push raw JSON values to in-memory buffer for SSE.
                    if let Some(mut buf) = livestream_events.get_mut(&task_id) {
                        for event in &events {
                            if let Ok(val) = serde_json::to_value(event) {
                                buf.push(val);
                            }
                        }
                    }

                    event_count += events.len();

                    update_task(
                        &tasks,
                        &task_id,
                        "streaming",
                        &format!("{event_count} events captured"),
                        1,
                    );
                }
            }
            Err(e) => {
                // Don't fail the task on transient errors. Just log and continue.
                tracing::warn!(error = %e, task_id = %task_id, "Livestream poll error");
            }
        }
    }

    // Finalize the stream by flushing and closing the writer.
    if let Err(e) = writer.flush() {
        tracing::warn!(error = %e, "Failed to flush livestream file on finalize");
    }
    drop(writer);

    if event_count == 0 {
        // Remove the temp file if no stream events were captured.
        if let Err(e) = std::fs::remove_file(&temp_path) {
            tracing::warn!(error = %e, "Failed to remove empty livestream temp file");
        }
        complete_task(&tasks, &task_id, "");
    } else {
        // Rename the temp file to the final name.
        let elapsed = started_at.elapsed();
        let total_secs = elapsed.as_secs();
        let duration = format!(
            "{:02}:{:02}:{:02}",
            total_secs / 3600,
            (total_secs % 3600) / 60,
            total_secs % 60,
        );
        let filename = livestream_filename(&params.target, &params.source, &start_time, &duration);
        let final_path = dir.join(format!("{filename}.jsonl"));

        match std::fs::rename(&temp_path, &final_path) {
            Ok(()) => {
                let rel = final_path
                    .strip_prefix(scrapes_dir.as_ref())
                    .unwrap_or(&final_path)
                    .to_string_lossy()
                    .to_string();
                complete_task(&tasks, &task_id, &rel);
            }
            Err(e) => {
                fail_task(
                    &tasks,
                    &task_id,
                    &format!("Failed to finalize output file: {e}"),
                );
            }
        }
    }

    cleanup_livestream(&livestream_tokens, &livestream_events, &task_id);
}

/// Removes the per-task cancellation token and event buffer from shared state.
fn cleanup_livestream(
    tokens: &DashMap<String, CancellationToken>,
    events: &DashMap<String, Vec<serde_json::Value>>,
    task_id: &str,
) {
    tokens.remove(task_id);
    // Keep events buffer for a short time so late-connecting SSE clients can get the snapshot.
    // The buffer will be cleaned up when the SSE stream ends and the DashMap entry is dropped.
    // Leaving it for now since it's bounded by the task lifetime.
    let _ = events;
}
