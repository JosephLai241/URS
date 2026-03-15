//! `Universal Reddit Scraper` core library.
//!
//! This crate provides the core functionality for scraping Reddit data using `OAuth2`
//! authentication.
//!
//! # Features
//!
//! - Rate limiting that respects Reddit's API limits
//! - Subreddit scraping (hot, new, top, controversial, rising, search)
//! - Redditor profile scraping (including private categories for authenticated user)
//! - Comment tree fetching with full expansion
//! - Livestreaming of new comments/submissions from Subreddits and Redditors
//! - Export to JSON and CSV formats
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
//! for post in posts {
//!     println!("{}: {}", post.author, post.title);
//! }
//! # Ok(())
//! # }
//! ```

pub mod analytics;
pub mod auth;
pub mod client;
pub mod error;
pub mod export;
pub mod models;
pub mod scrapers;

pub use error::{Error, Result};
