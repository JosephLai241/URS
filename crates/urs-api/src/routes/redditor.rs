//! Redditor (user) API routes.
//!
//! Provides endpoints for fetching user profiles, submissions, comments, and all interaction
//! categories.

use axum::Router;
use axum::extract::{Path, Query, State};
use axum::response::IntoResponse;
use axum::routing::get;
use tracing::instrument;
use urs_core::scrapers::RedditorScraper;

use crate::error::ApiError;
use crate::extractors::PaginationParams;
use crate::response::ApiResponse;
use crate::state::AppState;

/// Builds the Redditor router.
///
/// # Routes
///
/// - `GET /:username` — User profile info
/// - `GET /:username/comments` — User's comments
/// - `GET /:username/interactions` — All interaction categories
/// - `GET /:username/submissions` — User's submissions
pub fn router() -> Router<AppState> {
    Router::new()
        .route("/{username}", get(about))
        .route("/{username}/comments", get(comments))
        .route("/{username}/interactions", get(interactions))
        .route("/{username}/submissions", get(submissions))
}

/// `GET /api/redditors/{username}`
///
/// Returns the user's profile information.
#[instrument(skip(state))]
async fn about(
    State(state): State<AppState>,
    Path(username): Path<String>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = RedditorScraper::new(state.client());
    let redditor = scraper.about(&username).await?;

    Ok(ApiResponse::new(redditor))
}

/// `GET /api/redditors/{username}/submissions`
///
/// Returns the user's submissions.
#[instrument(skip(state))]
async fn submissions(
    State(state): State<AppState>,
    Path(username): Path<String>,
    Query(params): Query<PaginationParams>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = RedditorScraper::new(state.client());
    let posts = scraper.submissions(&username, params.limit()).await?;
    let count = posts.len();

    Ok(ApiResponse::with_count(posts, count))
}

/// `GET /api/redditors/{username}/comments`
///
/// Returns the user's comments.
#[instrument(skip(state))]
async fn comments(
    State(state): State<AppState>,
    Path(username): Path<String>,
    Query(params): Query<PaginationParams>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = RedditorScraper::new(state.client());
    let user_comments = scraper.comments(&username, params.limit()).await?;
    let count = user_comments.len();

    Ok(ApiResponse::with_count(user_comments, count))
}

/// `GET /api/redditors/{username}/interactions`
///
/// Returns all interaction categories for the user (submissions, comments, upvoted, etc.).
#[instrument(skip(state))]
async fn interactions(
    State(state): State<AppState>,
    Path(username): Path<String>,
    Query(params): Query<PaginationParams>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = RedditorScraper::new(state.client());
    let data = scraper.all_interactions(&username, params.limit()).await?;

    Ok(ApiResponse::new(data))
}
