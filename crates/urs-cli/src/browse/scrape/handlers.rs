//! POST handlers for batch scrape operations.
//!
//! Each handler validates credentials, creates a task entry in the shared `DashMap`, spawns a
//! background runner, and returns the task ID as JSON.

use std::sync::Arc;

use axum::extract::{Form, State};
use axum::http::HeaderMap;
use axum::response::{Html, IntoResponse, Json, Response};

use super::super::helpers::{error_response, render_template};
use super::super::server::{AppState, ScrapeTask};
use super::super::templates::ScrapeFormFragment;
use super::helpers::{
    CommentsScrapeParams, RedditorScrapeParams, SubredditScrapeParams, extract_title_from_url,
    now_unix,
};
use super::runners::{run_comments_scrape, run_redditor_scrape, run_subreddit_scrape};

/// Renders the scrape form page.
pub async fn scrape_form(State(state): State<AppState>, headers: HeaderMap) -> Response {
    let is_htmx = headers.contains_key("hx-request");

    let scrape_enabled = state.client.read().await.is_some();
    let username_lock = state.username.read().await;
    let username = username_lock.as_deref().map(String::from);

    drop(username_lock);

    let template = ScrapeFormFragment { scrape_enabled };
    let html = render_template(template);

    if is_htmx {
        Html(html).into_response()
    } else {
        super::super::helpers::wrap_in_shell(
            &state.scrapes_dir,
            scrape_enabled,
            username.as_deref(),
            &html,
            axum::http::StatusCode::OK,
        )
    }
}

/// POST handler for Subreddit scrapes. Spawns a background task and returns the task ID.
pub async fn scrape_subreddit(
    State(state): State<AppState>,
    Form(params): Form<SubredditScrapeParams>,
) -> Response {
    let Some(client) = state.client.read().await.clone() else {
        return error_response(
            403,
            "Reddit credentials not configured",
            true,
            &state.scrapes_dir,
            false,
            None,
        );
    };

    let category_label = params.category.clone();
    let subreddit_label = params.subreddit.clone();
    let title = format!("r/{subreddit_label} \u{2014} {category_label}");

    let id = uuid::Uuid::new_v4().to_string();
    state.scrape_tasks.insert(
        id.clone(),
        ScrapeTask {
            detail: format!("Validating r/{subreddit_label}..."),
            error: None,
            finished_at: None,
            id: id.clone(),
            result_path: None,
            stage: "validating".to_string(),
            stage_index: 0,
            stage_total: 4,
            started_at: now_unix(),
            task_type: "batch".to_string(),
            title,
        },
    );

    let tasks = Arc::clone(&state.scrape_tasks);
    let scrapes_dir = Arc::clone(&state.scrapes_dir);
    let task_id = id.clone();

    tokio::spawn(async move {
        run_subreddit_scrape(client, scrapes_dir, params, tasks, task_id).await;
    });

    Json(serde_json::json!({ "id": id })).into_response()
}

/// POST handler for comments scrapes. Spawns a background task and returns the task ID.
pub async fn scrape_comments(
    State(state): State<AppState>,
    Form(params): Form<CommentsScrapeParams>,
) -> Response {
    let Some(client) = state.client.read().await.clone() else {
        return error_response(
            403,
            "Reddit credentials not configured",
            true,
            &state.scrapes_dir,
            false,
            None,
        );
    };

    let title = format!("Comments \u{2014} {}", extract_title_from_url(&params.url));

    let id = uuid::Uuid::new_v4().to_string();
    state.scrape_tasks.insert(
        id.clone(),
        ScrapeTask {
            detail: "Validating submission URL...".to_string(),
            error: None,
            finished_at: None,
            id: id.clone(),
            result_path: None,
            stage: "validating".to_string(),
            stage_index: 0,
            stage_total: 4,
            started_at: now_unix(),
            task_type: "batch".to_string(),
            title,
        },
    );

    let tasks = Arc::clone(&state.scrape_tasks);
    let scrapes_dir = Arc::clone(&state.scrapes_dir);
    let task_id = id.clone();

    tokio::spawn(async move {
        run_comments_scrape(client, scrapes_dir, params, tasks, task_id).await;
    });

    Json(serde_json::json!({ "id": id })).into_response()
}

/// POST handler for Redditor scrapes. Spawns a background task and returns the task ID.
pub async fn scrape_redditor(
    State(state): State<AppState>,
    Form(params): Form<RedditorScrapeParams>,
) -> Response {
    let Some(client) = state.client.read().await.clone() else {
        return error_response(
            403,
            "Reddit credentials not configured",
            true,
            &state.scrapes_dir,
            false,
            None,
        );
    };

    let username_label = params.username.clone();
    let title = format!("u/{username_label}");

    let id = uuid::Uuid::new_v4().to_string();
    state.scrape_tasks.insert(
        id.clone(),
        ScrapeTask {
            detail: format!("Validating u/{username_label}..."),
            error: None,
            finished_at: None,
            id: id.clone(),
            result_path: None,
            stage: "validating".to_string(),
            stage_index: 0,
            stage_total: 4,
            started_at: now_unix(),
            task_type: "batch".to_string(),
            title,
        },
    );

    let tasks = Arc::clone(&state.scrape_tasks);
    let scrapes_dir = Arc::clone(&state.scrapes_dir);
    let task_id = id.clone();

    tokio::spawn(async move {
        run_redditor_scrape(client, scrapes_dir, params, tasks, task_id).await;
    });

    Json(serde_json::json!({ "id": id })).into_response()
}
