//! Middleware and shared utility routes.
//!
//! Provides the health check endpoint, bearer token authentication, CORS configuration, and
//! tracing middleware.

use axum::Router;
use axum::extract::{Request, State};
use axum::http::StatusCode;
use axum::middleware::{self, Next};
use axum::response::{IntoResponse, Response};
use axum::routing::get;
use serde::Serialize;
use tower_http::cors::CorsLayer;
use tower_http::trace::TraceLayer;
use tracing::{instrument, warn};

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
/// - Bearer token authentication (if `api_token` is `Some`)
/// - `TraceLayer` for request/response logging
/// - `CorsLayer` with permissive defaults
/// - `GET /api/health` endpoint (unauthenticated)
pub fn apply(router: Router<AppState>, api_token: Option<String>) -> Router<AppState> {
    // Health endpoint is outside the auth layer so it's always accessible.
    let health_route = Router::new().route("/api/health", get(health));

    let protected = if let Some(token) = api_token {
        router.layer(middleware::from_fn(move |req, next| {
            let token = token.clone();
            auth(token, req, next)
        }))
    } else {
        router
    };

    protected
        .merge(health_route)
        .layer(TraceLayer::new_for_http())
        .layer(CorsLayer::permissive())
}

/// Bearer token authentication middleware.
///
/// Checks the `Authorization` header for a valid `Bearer <token>` value. Returns 401 if the
/// header is missing or the token doesn't match.
async fn auth(expected_token: String, req: Request, next: Next) -> Response {
    let auth_header = req
        .headers()
        .get("Authorization")
        .and_then(|v| v.to_str().ok());

    match auth_header.and_then(|h| h.strip_prefix("Bearer ")) {
        Some(token) if token == expected_token => next.run(req).await,
        Some(_) => {
            warn!("Invalid bearer token");
            (
                StatusCode::UNAUTHORIZED,
                axum::Json(serde_json::json!({ "error": "Invalid token" })),
            )
                .into_response()
        }
        None => (
            StatusCode::UNAUTHORIZED,
            axum::Json(serde_json::json!({ "error": "Missing Authorization header" })),
        )
            .into_response(),
    }
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
