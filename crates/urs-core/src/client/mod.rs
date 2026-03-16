//! Reddit API client implementation with `OAuth2` authentication.
//!
//! This module provides a Reddit API client that uses `OAuth2` bearer tokens for authenticated
//! access to `https://oauth.reddit.com`. This enables higher rate limits (60 requests/minute) and
//! access to authenticated endpoints.
//!
//! # Example
//!
//! ```no_run
//! use urs_core::auth::Credentials;
//! use urs_core::client::RedditClient;
//! use urs_core::scrapers::SubredditScraper;
//!
//! # async fn example() -> urs_core::Result<()> {
//! let credentials = Credentials::from_env()?;
//! let client = RedditClient::new(credentials).await?;
//! let scraper = SubredditScraper::new(&client);
//!
//! let posts = scraper.hot("rust", 25).await?;
//! # Ok(())
//! # }
//! ```

pub mod endpoints;
mod http;
mod rate_limit;

pub use http::RedditClient;
pub use rate_limit::RateLimitInfo;
