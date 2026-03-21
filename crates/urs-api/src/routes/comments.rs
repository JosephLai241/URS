//! Comment fetching API routes.
//!
//! Provides endpoints for fetching submission comments by URL or by Subreddit/submission ID.

use axum::Router;
use axum::extract::{Path, Query, State};
use axum::response::IntoResponse;
use axum::routing::get;
use serde::Serialize;
use tracing::instrument;
use urs_core::models::{Comment, Submission};
use urs_core::scrapers::CommentsScraper;

use crate::error::ApiError;
use crate::extractors::CommentsQueryParams;
use crate::response::ApiResponse;
use crate::state::AppState;

/// Response body for comment endpoints.
#[derive(Debug, Serialize)]
struct CommentsResponse {
    /// The comments (flat or threaded depending on the `structured` parameter).
    comments: Vec<Comment>,
    /// The parent submission metadata.
    submission: Submission,
    /// Total number of comments fetched.
    total: usize,
}

/// Builds the comments router.
///
/// # Routes
///
/// - `GET /` — Fetch comments by submission URL (`?url=...`)
/// - `GET /:subreddit/:submission_id` — Fetch comments by Subreddit and submission ID
pub fn router() -> Router<AppState> {
    Router::new()
        .route("/", get(by_url))
        .route("/{subreddit}/{submission_id}", get(by_id))
}

/// `GET /api/comments?url=...`
///
/// Fetches comments from a submission URL. The `url` query parameter is required.
#[instrument(skip(state))]
async fn by_url(
    State(state): State<AppState>,
    Query(params): Query<CommentsQueryParams>,
) -> Result<impl IntoResponse, ApiError> {
    let url = params
        .url
        .as_deref()
        .filter(|u| !u.is_empty())
        .ok_or_else(|| {
            urs_core::Error::InvalidArgument("Missing required query parameter: url".to_string())
        })?;

    let scraper = CommentsScraper::new(state.client());
    let (submission, comments, total) = scraper
        .from_url(url, params.limit(), params.structured())
        .await?;

    Ok(ApiResponse::new(CommentsResponse {
        comments,
        submission,
        total,
    }))
}

/// `GET /api/comments/{subreddit}/{submission_id}`
///
/// Fetches comments by Subreddit name and submission ID.
#[instrument(skip(state))]
async fn by_id(
    State(state): State<AppState>,
    Path((subreddit, submission_id)): Path<(String, String)>,
    Query(params): Query<CommentsQueryParams>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = CommentsScraper::new(state.client());
    let (submission, comments, total) = scraper
        .fetch(
            &subreddit,
            &submission_id,
            params.limit(),
            params.structured(),
        )
        .await?;

    Ok(ApiResponse::new(CommentsResponse {
        comments,
        submission,
        total,
    }))
}
