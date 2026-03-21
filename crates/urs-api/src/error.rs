//! API error types and HTTP response mapping.
//!
//! This module wraps [`urs_core::Error`] into [`ApiError`], which implements Axum's
//! [`IntoResponse`] trait to produce appropriate HTTP status codes and JSON error bodies.

use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use serde::Serialize;
use tracing::warn;

/// An API error that maps [`urs_core::Error`] variants to HTTP status codes.
///
/// Each variant of the underlying core error is mapped to an appropriate HTTP status:
///
/// | Core Error | HTTP Status |
/// |------------|-------------|
/// | `NotFound` | 404 |
/// | `Forbidden` | 403 |
/// | `RateLimited` | 429 |
/// | `InvalidArgument` / `InvalidUrl` | 400 |
/// | `Auth` / `TokenExpired` / `Http` / `UnexpectedResponse` | 502 |
/// | `Io` / `Json` / `Image` | 500 |
#[derive(Debug)]
pub struct ApiError(urs_core::Error);

impl From<urs_core::Error> for ApiError {
    fn from(err: urs_core::Error) -> Self {
        Self(err)
    }
}

/// JSON body returned for error responses.
#[derive(Debug, Serialize)]
struct ErrorBody {
    /// Human-readable error message.
    error: String,
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        warn!(error = %self.0, "API error");

        let (status, message) = match &self.0 {
            urs_core::Error::NotFound(msg) => (StatusCode::NOT_FOUND, msg.clone()),
            urs_core::Error::Forbidden(msg) => (StatusCode::FORBIDDEN, msg.clone()),
            urs_core::Error::RateLimited { reset_seconds } => {
                let mut response = (
                    StatusCode::TOO_MANY_REQUESTS,
                    axum::Json(ErrorBody {
                        error: format!("Rate limited, retry after {reset_seconds} seconds"),
                    }),
                )
                    .into_response();

                response.headers_mut().insert(
                    "Retry-After",
                    reset_seconds
                        .to_string()
                        .parse()
                        .expect("numeric string is valid header value"),
                );

                return response;
            }
            urs_core::Error::InvalidArgument(msg) => (StatusCode::BAD_REQUEST, msg.clone()),
            urs_core::Error::InvalidUrl(err) => (StatusCode::BAD_REQUEST, err.to_string()),
            urs_core::Error::Auth(msg) | urs_core::Error::UnexpectedResponse(msg) => {
                (StatusCode::BAD_GATEWAY, msg.clone())
            }
            urs_core::Error::TokenExpired => (StatusCode::BAD_GATEWAY, "Token expired".to_string()),
            urs_core::Error::Http(err) => (StatusCode::BAD_GATEWAY, err.to_string()),
            urs_core::Error::Io(err) => (StatusCode::INTERNAL_SERVER_ERROR, err.to_string()),
            urs_core::Error::Json(err) => (StatusCode::INTERNAL_SERVER_ERROR, err.to_string()),
            urs_core::Error::Image(err) => (StatusCode::INTERNAL_SERVER_ERROR, err.to_string()),
        };

        (status, axum::Json(ErrorBody { error: message })).into_response()
    }
}
