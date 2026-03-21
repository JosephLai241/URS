//! Middleware and shared utility routes.
//!
//! Provides the health check endpoint, CORS configuration, and tracing middleware.

use axum::Router;
use axum::extract::State;
use axum::response::IntoResponse;
use axum::routing::get;
use serde::Serialize;
use tower_http::cors::CorsLayer;
use tower_http::trace::TraceLayer;
use tracing::instrument;

use crate::state::AppState;

/// Health check response body.
#[derive(Debug, Serialize)]
struct HealthResponse {
    /// Current rate limit information, if available.
    #[serde(skip_serializing_if = "Option::is_none")]
    rate_limit: Option<RateLimitResponse>,
    /// Always `"ok"` when the server is running.
    status: &'static str,
}

/// Rate limit information included in the health response.
#[derive(Debug, Serialize)]
struct RateLimitResponse {
    /// Approximate requests remaining in the current window.
    remaining: f64,
    /// Seconds until the rate limit window resets.
    reset: u64,
    /// Approximate requests used in the current window.
    used: u32,
}

/// Adds middleware layers and the health endpoint to the router.
///
/// This adds:
/// - `TraceLayer` for request/response logging
/// - `CorsLayer` with permissive defaults
/// - `GET /api/health` endpoint
pub fn apply(router: Router<AppState>) -> Router<AppState> {
    router
        .route("/api/health", get(health))
        .layer(TraceLayer::new_for_http())
        .layer(CorsLayer::permissive())
}

/// `GET /api/health`
///
/// Returns a health check response with current rate limit information.
#[instrument(skip(state))]
async fn health(State(state): State<AppState>) -> impl IntoResponse {
    let rate_limit = state
        .client()
        .rate_limit_info()
        .await
        .map(|info| RateLimitResponse {
            remaining: info.remaining,
            reset: info.reset,
            used: info.used,
        });

    axum::Json(HealthResponse {
        rate_limit,
        status: "ok",
    })
}
