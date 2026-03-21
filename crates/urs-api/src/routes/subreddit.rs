//! Subreddit API routes.
//!
//! Provides endpoints for fetching Subreddit information, listings sorted by various criteria,
//! and searching within a Subreddit.

use axum::Router;
use axum::extract::{Path, Query, State};
use axum::response::IntoResponse;
use axum::routing::get;
use tracing::instrument;
use urs_core::scrapers::SubredditScraper;

use crate::error::ApiError;
use crate::extractors::{PaginationParams, SearchParams, TimeFilterParams};
use crate::response::ApiResponse;
use crate::state::AppState;

/// Builds the Subreddit router.
///
/// # Routes
///
/// - `GET /:name` — Subreddit about info
/// - `GET /:name/hot` — Hot posts
/// - `GET /:name/new` — New posts
/// - `GET /:name/top` — Top posts (with time filter)
/// - `GET /:name/controversial` — Controversial posts (with time filter)
/// - `GET /:name/rising` — Rising posts
/// - `GET /:name/search` — Search within Subreddit
/// - `GET /:name/rules` — Subreddit rules
pub fn router() -> Router<AppState> {
    Router::new()
        .route("/{name}", get(about))
        .route("/{name}/controversial", get(controversial))
        .route("/{name}/hot", get(hot))
        .route("/{name}/new", get(new))
        .route("/{name}/rising", get(rising))
        .route("/{name}/rules", get(rules))
        .route("/{name}/search", get(search))
        .route("/{name}/top", get(top))
}

/// `GET /api/subreddits/{name}`
///
/// Returns Subreddit metadata (description, subscribers, etc.).
#[instrument(skip(state))]
async fn about(
    State(state): State<AppState>,
    Path(name): Path<String>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = SubredditScraper::new(state.client());
    let subreddit = scraper.about(&name).await?;

    Ok(ApiResponse::new(subreddit))
}

/// `GET /api/subreddits/{name}/hot`
///
/// Returns hot posts from the Subreddit.
#[instrument(skip(state))]
async fn hot(
    State(state): State<AppState>,
    Path(name): Path<String>,
    Query(params): Query<PaginationParams>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = SubredditScraper::new(state.client());
    let posts = scraper.hot(&name, params.limit()).await?;
    let count = posts.len();

    Ok(ApiResponse::with_count(posts, count))
}

/// `GET /api/subreddits/{name}/new`
///
/// Returns newest posts from the Subreddit.
#[instrument(skip(state))]
async fn new(
    State(state): State<AppState>,
    Path(name): Path<String>,
    Query(params): Query<PaginationParams>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = SubredditScraper::new(state.client());
    let posts = scraper.new_posts(&name, params.limit()).await?;
    let count = posts.len();

    Ok(ApiResponse::with_count(posts, count))
}

/// `GET /api/subreddits/{name}/top`
///
/// Returns top posts from the Subreddit, filtered by time period.
#[instrument(skip(state))]
async fn top(
    State(state): State<AppState>,
    Path(name): Path<String>,
    Query(params): Query<TimeFilterParams>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = SubredditScraper::new(state.client());
    let posts = scraper
        .top(&name, params.time_filter(), params.limit())
        .await?;
    let count = posts.len();

    Ok(ApiResponse::with_count(posts, count))
}

/// `GET /api/subreddits/{name}/controversial`
///
/// Returns controversial posts from the Subreddit, filtered by time period.
#[instrument(skip(state))]
async fn controversial(
    State(state): State<AppState>,
    Path(name): Path<String>,
    Query(params): Query<TimeFilterParams>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = SubredditScraper::new(state.client());
    let posts = scraper
        .controversial(&name, params.time_filter(), params.limit())
        .await?;
    let count = posts.len();

    Ok(ApiResponse::with_count(posts, count))
}

/// `GET /api/subreddits/{name}/rising`
///
/// Returns rising posts from the Subreddit.
#[instrument(skip(state))]
async fn rising(
    State(state): State<AppState>,
    Path(name): Path<String>,
    Query(params): Query<PaginationParams>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = SubredditScraper::new(state.client());
    let posts = scraper.rising(&name, params.limit()).await?;
    let count = posts.len();

    Ok(ApiResponse::with_count(posts, count))
}

/// `GET /api/subreddits/{name}/search`
///
/// Searches for posts within the Subreddit. The `q` query parameter is required.
#[instrument(skip(state))]
async fn search(
    State(state): State<AppState>,
    Path(name): Path<String>,
    Query(params): Query<SearchParams>,
) -> Result<impl IntoResponse, ApiError> {
    let query = params
        .q
        .as_deref()
        .filter(|q| !q.is_empty())
        .ok_or_else(|| {
            urs_core::Error::InvalidArgument("Missing required query parameter: q".to_string())
        })?;

    let scraper = SubredditScraper::new(state.client());
    let posts = scraper
        .search(&name, query, params.time_filter(), params.limit())
        .await?;
    let count = posts.len();

    Ok(ApiResponse::with_count(posts, count))
}

/// `GET /api/subreddits/{name}/rules`
///
/// Returns the Subreddit's rules.
#[instrument(skip(state))]
async fn rules(
    State(state): State<AppState>,
    Path(name): Path<String>,
) -> Result<impl IntoResponse, ApiError> {
    let scraper = SubredditScraper::new(state.client());
    let rules = scraper.rules(&name).await?;

    Ok(ApiResponse::new(rules))
}
