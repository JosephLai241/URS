//! Reddit scrapers for fetching data.
//!
//! This module provides scrapers for different Reddit entities:
//! - Subreddit posts (hot, new, top, controversial, rising, search)
//! - Redditor profiles and activity (including private categories)
//! - Submission comments with "more comments" expansion

mod comments;
mod redditor;
mod subreddit;

pub use comments::CommentsScraper;
pub use redditor::RedditorScraper;
pub use subreddit::SubredditScraper;
