//! Scrape handlers for the browse web server.
//!
//! Provides the scrape form route, background scrape execution handlers for subreddit, comments,
//! and redditor scrapes, livestream scraping, and a persistent SSE endpoint for streaming progress
//! updates to the sidebar.

mod handlers;
mod helpers;
mod livestream;
mod progress;
mod runners;

pub use handlers::{scrape_comments, scrape_form, scrape_redditor, scrape_subreddit};
pub use livestream::{
    livestream_events_sse, livestream_live_view, scrape_livestream, stop_livestream,
};
pub use progress::{refresh_rate_limit, scrape_progress_sse};
