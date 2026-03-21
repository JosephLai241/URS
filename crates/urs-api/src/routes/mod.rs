//! API route modules.
//!
//! Each sub-module provides a router for a specific domain. The [`router()`] function merges them
//! all under the `/api` prefix.

mod comments;
mod livestream;
mod redditor;
mod subreddit;

use axum::Router;

use crate::state::AppState;

/// Builds the combined API router with all route groups nested under `/api`.
///
/// # Route Groups
///
/// - `/api/subreddits/*` — Subreddit endpoints
/// - `/api/redditors/*` — Redditor endpoints
/// - `/api/comments/*` — Comment endpoints
/// - `/api/livestream/*` — SSE livestream endpoints
pub fn router() -> Router<AppState> {
    Router::new()
        .nest("/api/comments", comments::router())
        .nest("/api/livestream", livestream::router())
        .nest("/api/redditors", redditor::router())
        .nest("/api/subreddits", subreddit::router())
}
