//! `OAuth2` authentication for the Reddit API.
//!
//! This module implements the `OAuth2` "script" app flow for Reddit's API. It handles credential
//! management, token acquisition, and automatic token refresh on expiry.
//!
//! # Authentication Flow
//!
//! 1. POST to `https://www.reddit.com/api/v1/access_token` with basic auth
//!    (`client_id:client_secret`) and form body (`grant_type=password&username=...&password=...`)
//! 2. Receive a bearer token valid for 3600 seconds
//! 3. Use the bearer token for all subsequent requests to `https://oauth.reddit.com`
//! 4. Automatically refresh the token when it expires

use std::time::{Duration, Instant};

use serde::Deserialize;
use tokio::sync::RwLock;
use tracing::{debug, info};

use crate::error::{Error, Result};

/// Reddit `OAuth2` token endpoint.
const TOKEN_URL: &str = "https://www.reddit.com/api/v1/access_token";

/// Buffer time before actual expiry to trigger a proactive refresh.
const EXPIRY_BUFFER: Duration = Duration::from_secs(60);

/// `OAuth2` credentials for a Reddit "script" app.
///
/// These credentials are obtained by creating a "script" app at
/// <https://www.reddit.com/prefs/apps/>.
///
/// # Environment Variables
///
/// The [`Credentials::from_env`] method reads these variables:
/// - `URS_CLIENT_ID` — the app's client ID (14-character string)
/// - `URS_CLIENT_SECRET` — the app's secret key
/// - `URS_REDDIT_USERNAME` — the Reddit account username
/// - `URS_REDDIT_PASSWORD` — the Reddit account password
/// - `URS_USER_AGENT` — optional custom user agent string
///   (format: `<platform>:<app ID>:<version> (by /u/<username>)`)
#[derive(Debug, Clone)]
pub struct Credentials {
    /// The `OAuth2` client ID.
    client_id: String,
    /// The `OAuth2` client secret.
    client_secret: String,
    /// The Reddit account username.
    username: String,
    /// The Reddit account password.
    password: String,
    /// The User-Agent header to send with requests.
    user_agent: String,
}

impl Credentials {
    /// Creates new credentials from explicit values.
    ///
    /// # Arguments
    ///
    /// * `client_id` - The `OAuth2` client ID
    /// * `client_secret` - The `OAuth2` client secret
    /// * `username` - The Reddit account username
    /// * `password` - The Reddit account password
    /// * `user_agent` - The User-Agent header for requests
    #[must_use]
    pub fn new(
        client_id: impl Into<String>,
        client_secret: impl Into<String>,
        username: impl Into<String>,
        password: impl Into<String>,
        user_agent: impl Into<String>,
    ) -> Self {
        Self {
            client_id: client_id.into(),
            client_secret: client_secret.into(),
            username: username.into(),
            password: password.into(),
            user_agent: user_agent.into(),
        }
    }

    /// Creates credentials from environment variables.
    ///
    /// Reads `URS_CLIENT_ID`, `URS_CLIENT_SECRET`, `URS_REDDIT_USERNAME`, `URS_REDDIT_PASSWORD`,
    /// and optionally `URS_USER_AGENT` from the environment.
    ///
    /// # Errors
    ///
    /// Returns an error if any required environment variable is missing.
    pub fn from_env() -> Result<Self> {
        let client_id = Self::require_env("URS_CLIENT_ID")?;
        let client_secret = Self::require_env("URS_CLIENT_SECRET")?;
        let username = Self::require_env("URS_REDDIT_USERNAME")?;
        let password = Self::require_env("URS_REDDIT_PASSWORD")?;
        let user_agent = std::env::var("URS_USER_AGENT").unwrap_or_else(|_| {
            format!(
                "{}:com.{username}.urs:v{} (by /u/{username})",
                std::env::consts::OS,
                env!("CARGO_PKG_VERSION"),
            )
        });

        Ok(Self {
            client_id,
            client_secret,
            username,
            password,
            user_agent,
        })
    }

    /// Returns the user agent string.
    #[must_use]
    pub fn user_agent(&self) -> &str {
        &self.user_agent
    }

    /// Returns the client ID.
    #[must_use]
    pub fn client_id(&self) -> &str {
        &self.client_id
    }

    /// Returns the client secret.
    #[must_use]
    pub fn client_secret(&self) -> &str {
        &self.client_secret
    }

    /// Returns the Reddit username.
    #[must_use]
    pub fn username(&self) -> &str {
        &self.username
    }

    /// Reads a required environment variable.
    fn require_env(name: &str) -> Result<String> {
        std::env::var(name)
            .map_err(|_| Error::Auth(format!("Missing environment variable: {name}")))
    }
}

/// An `OAuth2` access token with expiry tracking.
#[derive(Debug, Clone)]
struct Token {
    /// The bearer access token.
    access_token: String,
    /// When this token expires.
    expires_at: Instant,
}

impl Token {
    /// Returns `true` if this token has expired or is about to expire.
    fn is_expired(&self) -> bool {
        let threshold = self
            .expires_at
            .checked_sub(EXPIRY_BUFFER)
            .unwrap_or(self.expires_at);

        Instant::now() >= threshold
    }
}

/// Response from Reddit's `OAuth2` token endpoint.
#[derive(Debug, Deserialize)]
struct TokenResponse {
    /// The bearer access token.
    access_token: String,
    /// Token type (always "bearer").
    #[allow(dead_code)]
    token_type: String,
    /// Time in seconds until the token expires.
    expires_in: u64,
    /// Granted scopes.
    #[allow(dead_code)]
    scope: String,
}

/// Manages `OAuth2` token lifecycle for the Reddit API.
///
/// Handles initial authentication and automatic token refresh when the access token expires.
/// Thread-safe via interior mutability with `RwLock`.
///
/// # Example
///
/// ```no_run
/// use urs_core::auth::{Credentials, TokenManager};
///
/// # async fn example() -> urs_core::Result<()> {
/// let credentials = Credentials::from_env()?;
/// let manager = TokenManager::new(credentials);
///
/// // Authenticate (fetches initial token)
/// manager.authenticate().await?;
///
/// // Get a valid access token (auto-refreshes if expired)
/// let token = manager.access_token().await?;
/// # Ok(())
/// # }
/// ```
#[derive(Debug)]
pub struct TokenManager {
    /// The `OAuth2` credentials.
    credentials: Credentials,
    /// The HTTP client used for token requests.
    http: reqwest::Client,
    /// The cached access token.
    token: RwLock<Option<Token>>,
}

impl TokenManager {
    /// Creates a new token manager with the given credentials.
    ///
    /// The manager does not authenticate immediately; call [`authenticate`](Self::authenticate)
    /// or [`access_token`](Self::access_token) to trigger the first token request.
    ///
    /// # Panics
    ///
    /// Panics if the HTTP client cannot be created.
    #[must_use]
    pub fn new(credentials: Credentials) -> Self {
        let http = reqwest::Client::builder()
            .timeout(Duration::from_secs(30))
            .build()
            .expect("Failed to create HTTP client");

        Self {
            credentials,
            http,
            token: RwLock::new(None),
        }
    }

    /// Authenticates with Reddit and obtains an access token.
    ///
    /// This makes a POST request to Reddit's token endpoint with the stored credentials. The token
    /// is cached for subsequent use.
    ///
    /// # Errors
    ///
    /// Returns an error if authentication fails (invalid credentials,
    /// network error, etc.).
    pub async fn authenticate(&self) -> Result<()> {
        info!("Authenticating with Reddit OAuth2...");

        let response = self
            .http
            .post(TOKEN_URL)
            .basic_auth(
                &self.credentials.client_id,
                Some(&self.credentials.client_secret),
            )
            .header("User-Agent", &self.credentials.user_agent)
            .form(&[
                ("grant_type", "password"),
                ("username", &self.credentials.username),
                ("password", &self.credentials.password),
            ])
            .send()
            .await
            .map_err(|e| Error::Auth(format!("Token request failed: {e}")))?;

        let status = response.status();
        if !status.is_success() {
            let body = response.text().await.unwrap_or_default();
            return Err(Error::Auth(format!(
                "Authentication failed (HTTP {status}): {body}"
            )));
        }

        let token_response: TokenResponse = response
            .json()
            .await
            .map_err(|e| Error::Auth(format!("Failed to parse token response: {e}")))?;

        debug!(
            expires_in = token_response.expires_in,
            "Obtained access token!"
        );

        let token = Token {
            access_token: token_response.access_token,
            expires_at: Instant::now() + Duration::from_secs(token_response.expires_in),
        };

        *self.token.write().await = Some(token);
        Ok(())
    }

    /// Returns a valid access token, refreshing if expired.
    ///
    /// If no token exists or the current token has expired, this method automatically
    /// re-authenticates before returning the token.
    ///
    /// # Errors
    ///
    /// Returns an error if authentication fails.
    pub async fn access_token(&self) -> Result<String> {
        if let Some(token) = self.get_valid_token().await {
            return Ok(token);
        }

        debug!("Access token expired or missing, refreshing");
        self.authenticate().await?;

        self.get_valid_token()
            .await
            .ok_or_else(|| Error::Auth("Failed to obtain access token!".to_string()))
    }

    /// Returns the cached token if it exists and hasn't expired.
    async fn get_valid_token(&self) -> Option<String> {
        let guard = self.token.read().await;
        guard
            .as_ref()
            .filter(|token| !token.is_expired())
            .map(|token| token.access_token.clone())
    }

    /// Returns the user agent string from the credentials.
    #[must_use]
    pub fn user_agent(&self) -> &str {
        self.credentials.user_agent()
    }

    /// Returns a reference to the credentials.
    #[must_use]
    pub const fn credentials(&self) -> &Credentials {
        &self.credentials
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn credentials_new() {
        let creds = Credentials::new("id", "secret", "user", "pass", "agent");

        assert_eq!(creds.client_id, "id");
        assert_eq!(creds.client_secret, "secret");
        assert_eq!(creds.username, "user");
        assert_eq!(creds.password, "pass");
        assert_eq!(creds.user_agent, "agent");
    }

    #[test]
    fn token_not_expired() {
        let token = Token {
            access_token: "test_token".to_string(),
            expires_at: Instant::now() + Duration::from_secs(3600),
        };

        assert!(!token.is_expired());
    }

    #[test]
    fn token_expired() {
        let token = Token {
            access_token: "test_token".to_string(),
            expires_at: Instant::now() - Duration::from_secs(1),
        };

        assert!(token.is_expired());
    }

    #[test]
    fn token_about_to_expire() {
        let token = Token {
            access_token: "test_token".to_string(),
            // Within EXPIRY_BUFFER.
            expires_at: Instant::now() + Duration::from_secs(30),
        };

        assert!(token.is_expired());
    }

    #[test]
    fn token_manager_creation() {
        let creds = Credentials::new("id", "secret", "user", "pass", "agent");
        let manager = TokenManager::new(creds);

        assert_eq!(manager.user_agent(), "agent");
    }
}
