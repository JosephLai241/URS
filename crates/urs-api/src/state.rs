//! Application state shared across all API handlers.
//!
//! The [`AppState`] wraps a [`RedditClient`] in an `Arc` so it can be shared across Axum handlers.
//! Since `RedditClient` already uses `Arc` internally for its token manager and rate limiter, this
//! adds minimal overhead.

use std::sync::Arc;

use urs_core::client::RedditClient;

/// Shared application state for the API.
///
/// Wraps the [`RedditClient`] in an `Arc` so it can be cheaply cloned across handler tasks.
///
/// # Example
///
/// ```
/// use urs_core::client::RedditClient;
/// use urs_api::state::AppState;
///
/// # fn example(client: RedditClient) {
/// let state = AppState::new(client);
/// # }
/// ```
#[derive(Debug, Clone)]
pub struct AppState {
    /// The shared Reddit client.
    client: Arc<RedditClient>,
}

impl AppState {
    /// Creates a new `AppState` wrapping the given client.
    ///
    /// # Arguments
    ///
    /// * `client` - The authenticated Reddit client to share across handlers
    #[must_use]
    pub fn new(client: RedditClient) -> Self {
        Self {
            client: Arc::new(client),
        }
    }

    /// Returns a reference to the shared Reddit client.
    #[must_use]
    pub fn client(&self) -> &RedditClient {
        &self.client
    }

    /// Returns a clone of the `Arc<RedditClient>` for use in contexts that need ownership
    /// (e.g., spawning `'static` tasks or SSE streams).
    #[must_use]
    pub fn client_arc(&self) -> Arc<RedditClient> {
        Arc::clone(&self.client)
    }
}
