//! Reddit API credential configuration.
//!
//! Contains the [`CredentialsConfig`] struct for storing `OAuth2` credentials needed to authenticate
//! with the Reddit API.

use serde::{Deserialize, Serialize};

/// Reddit `OAuth2` API credentials.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct CredentialsConfig {
    /// The `OAuth2` client ID.
    pub client_id: Option<String>,
    /// The `OAuth2` client secret.
    pub client_secret: Option<String>,
    /// The Reddit account password.
    pub password: Option<String>,
    /// The Reddit account username.
    pub username: Option<String>,
}

impl CredentialsConfig {
    /// Returns `true` if all required credentials are set.
    #[must_use]
    pub const fn is_complete(&self) -> bool {
        self.client_id.is_some()
            && self.client_secret.is_some()
            && self.password.is_some()
            && self.username.is_some()
    }
}
