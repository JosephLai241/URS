//! REST API layer for the Universal Reddit Scraper.
//!
//! This crate exposes an Axum [`Router`] that wraps `urs-core` scrapers in HTTP endpoints. The
//! consuming binary (e.g., `urs-cli`) creates a [`RedditClient`], calls [`build_router()`], and
//! serves the result with `axum::serve`.
//!
//! # Quick Start
//!
//! ```no_run
//! use urs_core::auth::Credentials;
//! use urs_core::client::RedditClient;
//!
//! # async fn example() -> Result<(), Box<dyn std::error::Error>> {
//! let client = RedditClient::new(Credentials::from_env()?).await?;
//! let app = urs_api::build_router(client, None);
//!
//! let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
//! axum::serve(listener, app).await?;
//! # Ok(())
//! # }
//! ```
//!
//! # Authentication
//!
//! Pass an API token to [`build_router()`] to require bearer token authentication on all endpoints
//! except `/api/health`. If `None` is passed, the API runs without authentication and logs a
//! warning at startup.
//!
//! # Endpoints
//!
//! | Prefix | Description |
//! |--------|-------------|
//! | `/api/subreddits` | Subreddit listings and info |
//! | `/api/redditors` | User profiles and activity |
//! | `/api/comments` | Submission comment trees |
//! | `/api/livestream` | Real-time SSE streams |
//! | `/api/health` | Health check with rate limit info |

pub mod error;
pub mod extractors;
mod middleware;
pub mod response;
mod routes;
pub mod state;

use axum::Router;
use tracing::warn;
use urs_core::client::RedditClient;

use state::AppState;

/// Builds the API router.
///
/// If `api_token` is `Some`, all endpoints (except `/api/health`) require an
/// `Authorization: Bearer <token>` header. If `None`, the API runs without authentication.
///
/// The caller is responsible for resolving the token from whatever source is appropriate
/// (config file, environment variable, etc.).
///
/// # Arguments
///
/// * `client` - An authenticated Reddit client
/// * `api_token` - Optional bearer token for API authentication
///
/// # Example
///
/// ```no_run
/// use urs_core::auth::Credentials;
/// use urs_core::client::RedditClient;
///
/// # async fn example() -> Result<(), Box<dyn std::error::Error>> {
/// let client = RedditClient::new(Credentials::from_env()?).await?;
/// let app = urs_api::build_router(client, Some("my-secret-token".to_string()));
/// # Ok(())
/// # }
/// ```
pub fn build_router(client: RedditClient, api_token: Option<String>) -> Router {
    let state = AppState::new(client);

    if api_token.is_none() {
        warn!("API is running without authentication");
        warn!(
            "Set up an API token with the 'urs config generate-api-token' command or set the URS_API_TOKEN environment variable to enable authentication"
        );
    }

    let app = routes::router();
    let app = middleware::apply(app, api_token);

    app.with_state(state)
}
