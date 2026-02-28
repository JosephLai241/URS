//! HTTP client wrapper for the Reddit OAuth API.
//!
//! This module provides a high-level HTTP client that handles OAuth2 authentication, rate
//! limiting, automatic retries, and token refresh for the Reddit API.

use std::sync::Arc;
use std::time::Duration;

use reqwest::header::{HeaderMap, HeaderValue, USER_AGENT};
use tokio::sync::RwLock;
use tracing::{debug, warn};
use url::Url;

use super::rate_limit::RateLimiter;
use crate::auth::{Credentials, TokenManager};
use crate::error::{Error, Result};

/// Maximum number of retry attempts for failed requests.
const MAX_RETRIES: u32 = 3;

/// Initial delay for exponential backoff on retries.
const INITIAL_RETRY_DELAY: Duration = Duration::from_secs(1);

/// A Reddit API client using OAuth2 authentication.
///
/// All requests are sent to `https://oauth.reddit.com` with bearer token authentication. The
/// client handles rate limiting and automatic token refresh on expiry.
///
/// # Example
///
/// ```no_run
/// use urs_core::auth::Credentials;
/// use urs_core::client::RedditClient;
///
/// # async fn example() -> urs_core::Result<()> {
/// let credentials = Credentials::from_env()?;
/// let client = RedditClient::new(credentials).await?;
///
/// // All requests are automatically authenticated
/// let url = url::Url::parse("https://oauth.reddit.com/r/rust/hot")?;
/// let data = client.get(&url).await?;
/// # Ok(())
/// # }
/// ```
#[derive(Debug)]
pub struct RedditClient {
    /// The OAuth2 token manager.
    token_manager: Arc<TokenManager>,
    /// The underlying HTTP client.
    http: reqwest::Client,
    /// The rate limiter tracking API usage.
    rate_limiter: Arc<RwLock<RateLimiter>>,
}

impl RedditClient {
    /// Creates a new authenticated Reddit client.
    ///
    /// This authenticates with the Reddit API using the provided credentials and obtains an
    /// initial access token.
    ///
    /// # Arguments
    ///
    /// * `credentials` - The OAuth2 credentials for authentication
    ///
    /// # Errors
    ///
    /// Returns an error if authentication fails.
    pub async fn new(credentials: Credentials) -> Result<Self> {
        let user_agent = credentials.user_agent().to_string();

        let mut headers = HeaderMap::new();
        headers.insert(
            USER_AGENT,
            HeaderValue::from_str(&user_agent).unwrap_or_else(|_| {
                let username = credentials.username();

                HeaderValue::from_str(&format!(
                    "{}:com.{username}.urs:v{} (by /u/{username})",
                    std::env::consts::OS,
                    env!("CARGO_PKG_VERSION"),
                ))
                .expect("OS const produces valid header!")
            }),
        );

        let http = reqwest::Client::builder()
            .timeout(Duration::from_secs(30))
            .default_headers(headers)
            .build()
            .expect("Failed to create HTTP client!");

        let token_manager = Arc::new(TokenManager::new(credentials));
        token_manager.authenticate().await?;

        Ok(Self {
            token_manager,
            http,
            rate_limiter: Arc::new(RwLock::new(RateLimiter::new())),
        })
    }

    /// Performs an authenticated GET request to the Reddit API.
    ///
    /// This method handles rate limiting, retries, and automatic token refresh on 401 response.
    ///
    /// # Arguments
    ///
    /// * `url` - The full URL to request (should be on `oauth.reddit.com`)
    ///
    /// # Errors
    ///
    /// Returns an error if the request fails after all retry attempts.
    pub async fn get(&self, url: &Url) -> Result<serde_json::Value> {
        self.request_with_retry(url, None).await
    }

    /// Performs an authenticated POST request to the Reddit API.
    ///
    /// # Arguments
    ///
    /// * `url` - The full URL to request
    /// * `form` - The form data to send in the request body
    ///
    /// # Errors
    ///
    /// Returns an error if the request fails after all retry attempts.
    pub async fn post(&self, url: &Url, form: &[(&str, &str)]) -> Result<serde_json::Value> {
        self.request_with_retry(url, Some(form)).await
    }

    /// Performs a request with automatic retries and token refresh.
    async fn request_with_retry(
        &self,
        url: &Url,
        form: Option<&[(&str, &str)]>,
    ) -> Result<serde_json::Value> {
        let mut last_error = None;
        let mut delay = INITIAL_RETRY_DELAY;

        for attempt in 1..=MAX_RETRIES {
            // Wait if rate limited.
            self.rate_limiter.read().await.wait_if_needed().await;

            match self.execute_request(url, form).await {
                Ok(response) => return Ok(response),
                Err(error) => {
                    if Self::should_retry(&error) && attempt < MAX_RETRIES {
                        warn!(
                            attempt = attempt,
                            max_retries = MAX_RETRIES,
                            error = %error,
                            "Request failed, retrying..."
                        );

                        tokio::time::sleep(delay).await;

                        // Exponential backoff.
                        delay *= 2;
                    } else {
                        last_error = Some(error);

                        break;
                    }
                }
            }
        }

        // TODO: Revise this expect message.
        Err(last_error.expect("At least one error occurred."))
    }

    /// Executes a single request with authentication.
    async fn execute_request(
        &self,
        url: &Url,
        form: Option<&[(&str, &str)]>,
    ) -> Result<serde_json::Value> {
        let token = self.token_manager.access_token().await?;

        debug!(url = %url, method = if form.is_some() { "POST" } else { "GET" }, "Executing request");

        let builder = form.map_or_else(
            || self.http.get(url.as_str()),
            |form_data| self.http.post(url.as_str()).form(form_data),
        );

        let response = builder.bearer_auth(&token).send().await?;

        // Update rate limiter with response headers.
        let mut rate_limiter = self.rate_limiter.write().await;
        rate_limiter.update(response.headers());
        drop(rate_limiter);

        let status = response.status();
        debug!(status = %status, "Received response");

        match status.as_u16() {
            200..=299 => {
                let json: serde_json::Value = response.json().await?;
                Ok(json)
            }
            401 => {
                // Token expired — refresh and let retry handle it.
                warn!("Received 401, refreshing token...");
                self.token_manager.authenticate().await?;

                Err(Error::TokenExpired)
            }
            403 => {
                let body = response.text().await.unwrap_or_default();
                Err(Error::Forbidden(body))
            }
            404 => {
                let body = response.text().await.unwrap_or_default();
                Err(Error::NotFound(body))
            }
            429 => {
                // Rate limited — extract reset time if available.
                let reset_seconds = self
                    .rate_limiter
                    .read()
                    .await
                    .info()
                    .map(|info| info.reset)
                    .unwrap_or(60);

                Err(Error::RateLimited { reset_seconds })
            }
            _ => {
                let body = response.text().await.unwrap_or_default();
                Err(Error::UnexpectedResponse(format!(
                    "Status {status}: {body}"
                )))
            }
        }
    }

    /// Determines if a request should be retried based on the error.
    fn should_retry(error: &Error) -> bool {
        matches!(
            error,
            Error::RateLimited { .. } | Error::Http(_) | Error::TokenExpired
        )
    }

    /// Returns the current rate limit information.
    ///
    /// Returns `None` if no requests have been made yet.
    pub async fn rate_limit_info(&self) -> Option<super::rate_limit::RateLimitInfo> {
        self.rate_limiter.read().await.info()
    }

    /// Returns a reference to the token manager.
    #[must_use]
    pub fn token_manager(&self) -> &TokenManager {
        &self.token_manager
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn should_retry_rate_limited() {
        assert!(RedditClient::should_retry(&Error::RateLimited {
            reset_seconds: 60
        }));
    }

    #[test]
    fn should_retry_token_expired() {
        assert!(RedditClient::should_retry(&Error::TokenExpired));
    }

    #[test]
    fn should_not_retry_not_found() {
        assert!(!RedditClient::should_retry(&Error::NotFound(
            "test".to_string()
        )));
    }

    #[test]
    fn should_not_retry_forbidden() {
        assert!(!RedditClient::should_retry(&Error::Forbidden(
            "test".to_string()
        )));
    }

    #[test]
    fn should_not_retry_auth() {
        assert!(!RedditClient::should_retry(&Error::Auth(
            "bad creds".to_string()
        )));
    }
}
