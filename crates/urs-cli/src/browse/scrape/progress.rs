//! SSE progress streaming and rate limit refresh.
//!
//! Provides the persistent SSE endpoint that streams scrape task updates to the browser sidebar,
//! and the manual rate limit refresh handler.

use std::collections::{HashMap, HashSet};
use std::convert::Infallible;
use std::sync::Arc;

use axum::extract::State;
use axum::response::sse::{Event, Sse};
use axum::response::{IntoResponse, Json, Response};
use futures::Stream;
use url::Url;

use super::super::server::{AppState, ScrapeTask};

/// Serializable task snapshot sent over SSE.
#[derive(serde::Serialize)]
struct TaskSnapshot {
    detail: String,
    error: Option<String>,
    id: String,
    result_path: Option<String>,
    stage: String,
    stage_index: u8,
    stage_total: u8,
    started_at: f64,
    task_type: String,
    title: String,
}

impl From<&ScrapeTask> for TaskSnapshot {
    fn from(task: &ScrapeTask) -> Self {
        Self {
            detail: task.detail.clone(),
            error: task.error.clone(),
            id: task.id.clone(),
            result_path: task.result_path.clone(),
            stage: task.stage.clone(),
            stage_index: task.stage_index,
            stage_total: task.stage_total,
            started_at: task.started_at,
            task_type: task.task_type.clone(),
            title: task.title.clone(),
        }
    }
}

/// SSE endpoint that streams progress updates for all active scrape tasks.
///
/// On connect, emits a `snapshot` event with all current tasks. Then polls every 500ms for changes
/// and emits `update` events for tasks whose state changed, or `remove` events for cleaned-up
/// tasks.
pub async fn scrape_progress_sse(
    State(state): State<AppState>,
) -> Sse<impl Stream<Item = Result<Event, Infallible>>> {
    let tasks = Arc::clone(&state.scrape_tasks);
    let shutdown = state.shutdown.clone();
    let client = state.client.read().await.clone();

    let stream = async_stream::stream! {
        // Take an initial snapshot. Track stage, stage_index, and detail to detect changes.
        let mut last_seen: HashMap<String, (String, u8, String)> = HashMap::new();
        let mut known_ids: HashSet<String> = HashSet::new();

        // Track last emitted rate limit to avoid redundant events.
        let mut last_rate_limit: Option<(u32, u64)> = None;

        // Emit initial snapshot.
        let all: Vec<TaskSnapshot> = tasks
            .iter()
            .map(|entry| {
                let task = entry.value();
                last_seen.insert(task.id.clone(), (task.stage.clone(), task.stage_index, task.detail.clone()));
                known_ids.insert(task.id.clone());
                TaskSnapshot::from(task)
            })
            .collect();

        if let Ok(json) = serde_json::to_string(&serde_json::json!({ "tasks": all })) {
            yield Ok(Event::default().event("snapshot").data(json));
        }

        // Emit initial rate limit if available.
        if let Some(ref c) = client {
            if let Some(info) = c.rate_limit_info().await {
                last_rate_limit = Some((info.used, info.reset));

                if let Ok(json) = serde_json::to_string(&info) {
                    yield Ok(Event::default().event("ratelimit").data(json));
                }
            }
        }

        let mut interval = tokio::time::interval(std::time::Duration::from_millis(500));

        loop {
            tokio::select! {
                () = shutdown.cancelled() => break,
                _ = interval.tick() => {}
            }

            // Emit rate limit updates when values change.
            if let Some(ref c) = client {
                if let Some(info) = c.rate_limit_info().await {
                    let current = (info.used, info.reset);
                    let changed = last_rate_limit.is_none_or(|prev| prev != current);

                    if changed {
                        last_rate_limit = Some(current);

                        if let Ok(json) = serde_json::to_string(&info) {
                            yield Ok(Event::default().event("ratelimit").data(json));
                        }
                    }
                }
            }

            // Check for updated or new tasks.
            let mut current_ids: std::collections::HashSet<String> = std::collections::HashSet::new();

            for entry in tasks.iter() {
                let task = entry.value();
                current_ids.insert(task.id.clone());

                let changed = last_seen
                    .get(&task.id)
                    .is_none_or(|(s, i, d)| s != &task.stage || *i != task.stage_index || d != &task.detail);

                if changed {
                    last_seen.insert(task.id.clone(), (task.stage.clone(), task.stage_index, task.detail.clone()));
                    let snapshot = TaskSnapshot::from(task);

                    if let Ok(json) = serde_json::to_string(&snapshot) {
                        yield Ok(Event::default().event("update").data(json));
                    }
                }
            }

            // Check for removed tasks.
            let removed: Vec<String> = known_ids.difference(&current_ids).cloned().collect();
            for id in &removed {
                last_seen.remove(id);

                if let Ok(json) = serde_json::to_string(&serde_json::json!({ "id": id })) {
                    yield Ok(Event::default().event("remove").data(json));
                }
            }

            known_ids = current_ids;
        }
    };

    Sse::new(stream)
}

/// POST handler for manual rate limit refresh.
///
/// Makes a lightweight `GET /api/v1/me` request (same as `urs check`) to trigger a rate limit
/// header update, then returns the fresh `RateLimitInfo` as JSON.
pub async fn refresh_rate_limit(State(state): State<AppState>) -> Response {
    let Some(client) = state.client.read().await.clone() else {
        return (
            axum::http::StatusCode::SERVICE_UNAVAILABLE,
            "Reddit credentials not configured",
        )
            .into_response();
    };

    let me_url = Url::parse("https://oauth.reddit.com/api/v1/me").expect("hardcoded URL is valid");

    if let Err(e) = client.get(&me_url).await {
        tracing::warn!(error = %e, "Failed to refresh rate limit");
        return (
            axum::http::StatusCode::BAD_GATEWAY,
            format!("Failed to fetch rate limit: {e}"),
        )
            .into_response();
    }

    client.rate_limit_info().await.map_or_else(
        || Json(serde_json::json!(null)).into_response(),
        |info| Json(info).into_response(),
    )
}
