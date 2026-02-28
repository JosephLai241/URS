//! Error types for the URS core library.
//!
//! This module defines all error types that can occur during Reddit API
//! interactions, including authentication, rate limiting, and network errors.

use thiserror::Error;

/// The main error type for all URS operations.
///
/// This enum encompasses all possible errors that can occur when interacting
/// with the Reddit API, from network issues to parsing failures.
#[derive(Debug, Error)]
pub enum Error {
    /// Authentication failed (invalid credentials, revoked token, etc.).
    #[error("Authentication error: {0}")]
    Auth(String),

    /// Access to the resource is forbidden.
    ///
    /// This typically occurs when trying to access private user data
    /// or subreddits that require special permissions.
    #[error("Forbidden: {0}")]
    Forbidden(String),

    /// An HTTP request failed.
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),

    /// An invalid argument was provided.
    #[error("Invalid argument: {0}")]
    InvalidArgument(String),

    /// Failed to parse a URL.
    #[error("Invalid URL: {0}")]
    InvalidUrl(#[from] url::ParseError),

    /// Failed to read or write to the filesystem.
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    /// Failed to serialize or deserialize JSON.
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),

    /// The requested resource was not found.
    #[error("Not found: {0}")]
    NotFound(String),

    /// Rate limit exceeded for the Reddit API.
    #[error("Rate limit exceeded, reset in {reset_seconds} seconds")]
    RateLimited {
        /// Seconds until the rate limit resets.
        reset_seconds: u64,
    },

    /// The OAuth2 access token has expired and needs to be refreshed.
    #[error("Access token expired")]
    TokenExpired,

    /// The Reddit API returned an unexpected response.
    #[error("Unexpected API response: {0}")]
    UnexpectedResponse(String),
}

/// A specialized Result type for URS operations.
pub type Result<T> = std::result::Result<T, Error>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn error_display_auth() {
        let err = Error::Auth("invalid credentials".to_string());
        assert_eq!(err.to_string(), "Authentication error: invalid credentials");
    }

    #[test]
    fn error_display_token_expired() {
        let err = Error::TokenExpired;
        assert_eq!(err.to_string(), "Access token expired");
    }

    #[test]
    fn error_display_rate_limited() {
        let err = Error::RateLimited { reset_seconds: 60 };
        assert_eq!(err.to_string(), "Rate limit exceeded, reset in 60 seconds");
    }

    #[test]
    fn error_display_not_found() {
        let err = Error::NotFound("user spez".to_string());
        assert_eq!(err.to_string(), "Not found: user spez");
    }

    #[test]
    fn error_display_forbidden() {
        let err = Error::Forbidden("private subreddit".to_string());
        assert_eq!(err.to_string(), "Forbidden: private subreddit");
    }
}
