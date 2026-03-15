//! Livestreaming scrapers for monitoring real-time Reddit activity.
//!
//! This module provides functionality to poll Subreddits and Redditors for new comments or
//! submissions in real-time. It uses cursor-based polling with the Reddit API's `before` parameter
//! to efficiently fetch only new items since the last poll.
//!
//! # Example
//!
//! ```no_run
//! use urs_core::client::RedditClient;
//! use urs_core::scrapers::{LivestreamSource, LivestreamTarget, Livestreamer};
//!
//! # async fn example(client: &RedditClient) -> urs_core::Result<()> {
//! let mut streamer = Livestreamer::new(
//!     client,
//!     LivestreamTarget::Subreddit("rust".to_string()),
//!     LivestreamSource::Comments,
//! );
//!
//! loop {
//!     let events = streamer.poll().await?;
//!     for event in &events {
//!         match event {
//!             urs_core::scrapers::LivestreamEvent::Comment(c) => {
//!                 println!("{}: {}", c.author, c.body);
//!             }
//!             urs_core::scrapers::LivestreamEvent::Submission(s) => {
//!                 println!("{}: {}", s.author, s.title);
//!             }
//!         }
//!     }
//!     tokio::time::sleep(std::time::Duration::from_secs(5)).await;
//! }
//! # }
//! ```

use serde::Serialize;
use tracing::{debug, info};

use crate::client::RedditClient;
use crate::client::endpoints::LivestreamEndpoint;
use crate::error::Result;
use crate::models::api::{CommentData, Listing, SubmissionData};
use crate::models::{Comment, Submission};

/// The target to monitor for new activity.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum LivestreamTarget {
    /// Monitor a Subreddit for new activity.
    Subreddit(String),
    /// Monitor a Redditor for new activity.
    Redditor(String),
}

impl std::fmt::Display for LivestreamTarget {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Subreddit(name) => write!(f, "r/{name}"),
            Self::Redditor(name) => write!(f, "u/{name}"),
        }
    }
}

/// The type of content to stream.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum LivestreamSource {
    /// Stream new comments (default).
    #[default]
    Comments,
    /// Stream new submissions.
    Submissions,
}

impl std::fmt::Display for LivestreamSource {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Comments => write!(f, "comments"),
            Self::Submissions => write!(f, "submissions"),
        }
    }
}

/// An event emitted by the livestreamer when new content is detected.
#[derive(Debug, Clone, Serialize)]
#[serde(tag = "type", content = "data", rename_all = "lowercase")]
pub enum LivestreamEvent {
    /// A new comment was posted.
    Comment(Comment),
    /// A new submission was posted.
    Submission(Submission),
}

/// Polls a Subreddit or Redditor for new comments or submissions.
///
/// Uses cursor-based pagination with the Reddit API's `before` parameter to efficiently fetch only
/// items that have appeared since the last poll. On the first poll, fetches the most recent batch
/// and stores the newest item's fullname as the cursor for subsequent polls.
///
/// # Usage
///
/// Call [`poll()`](Self::poll) in a loop with a delay between calls (e.g. 5 seconds). Each call
/// returns only items that are new since the previous call.
///
/// # Example
///
/// ```no_run
/// use urs_core::client::RedditClient;
/// use urs_core::scrapers::{LivestreamSource, LivestreamTarget, Livestreamer};
///
/// # async fn example(client: &RedditClient) -> urs_core::Result<()> {
/// let mut streamer = Livestreamer::new(
///     client,
///     LivestreamTarget::Subreddit("rust".to_string()),
///     LivestreamSource::Submissions,
/// );
///
/// // First poll seeds the cursor with the latest items.
/// let initial = streamer.poll().await?;
/// println!("Initial batch: {} items", initial.len());
///
/// // Subsequent polls return only new items.
/// loop {
///     tokio::time::sleep(std::time::Duration::from_secs(5)).await;
///     let new_items = streamer.poll().await?;
///     for item in &new_items {
///         match item {
///             urs_core::scrapers::LivestreamEvent::Comment(c) => {
///                 println!("[comment] {}: {}", c.author, c.body);
///             }
///             urs_core::scrapers::LivestreamEvent::Submission(s) => {
///                 println!("[submission] {}: {}", s.author, s.title);
///             }
///         }
///     }
/// }
/// # }
/// ```
#[derive(Debug)]
pub struct Livestreamer<'a> {
    /// The Reddit client for making authenticated API requests.
    client: &'a RedditClient,
    /// What to monitor (Subreddit or Redditor).
    target: LivestreamTarget,
    /// What content to stream (comments or submissions).
    source: LivestreamSource,
    /// The fullname of the newest item seen, used as the `before` cursor.
    cursor: Option<String>,
}

impl<'a> Livestreamer<'a> {
    /// Creates a new livestreamer.
    ///
    /// # Arguments
    ///
    /// * `client` - The authenticated Reddit client
    /// * `target` - The Subreddit or Redditor to monitor
    /// * `source` - Whether to stream comments or submissions
    #[must_use]
    pub const fn new(
        client: &'a RedditClient,
        target: LivestreamTarget,
        source: LivestreamSource,
    ) -> Self {
        Self {
            client,
            target,
            source,
            cursor: None,
        }
    }

    /// Returns the current target being monitored.
    #[must_use]
    pub const fn target(&self) -> &LivestreamTarget {
        &self.target
    }

    /// Returns the current source type being streamed.
    #[must_use]
    pub const fn source(&self) -> &LivestreamSource {
        &self.source
    }

    /// Returns the current cursor (fullname of the newest item seen).
    #[must_use]
    pub fn cursor(&self) -> Option<&str> {
        self.cursor.as_deref()
    }

    /// Polls for new items since the last poll.
    ///
    /// On the first call, fetches the most recent batch and seeds the cursor. Subsequent calls
    /// return only items newer than the cursor.
    ///
    /// Items are returned in chronological order (oldest first) so they can be processed or
    /// displayed in the order they were created.
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn poll(&mut self) -> Result<Vec<LivestreamEvent>> {
        match self.source {
            LivestreamSource::Comments => self.poll_comments().await,
            LivestreamSource::Submissions => self.poll_submissions().await,
        }
    }

    /// Polls for new comments.
    async fn poll_comments(&mut self) -> Result<Vec<LivestreamEvent>> {
        let url = match &self.target {
            LivestreamTarget::Subreddit(name) => {
                LivestreamEndpoint::subreddit_comments(name, self.cursor.as_deref())
            }
            LivestreamTarget::Redditor(name) => {
                LivestreamEndpoint::redditor_comments(name, self.cursor.as_deref())
            }
        };

        debug!(
            target = %self.target,
            source = "comments",
            cursor = ?self.cursor,
            "Polling for new comments"
        );

        let response = self.client.get(&url).await?;
        let listing: Listing<CommentData> = serde_json::from_value(response)?;

        let comments: Vec<Comment> = listing
            .data
            .children
            .into_iter()
            .map(|thing| Comment::from(thing.data))
            .collect();

        if let Some(newest) = comments.first() {
            let new_cursor = format!("t1_{}", newest.id);
            debug!(
                old_cursor = ?self.cursor,
                new_cursor = %new_cursor,
                count = comments.len(),
                "Updated livestream cursor"
            );
            self.cursor = Some(new_cursor);
        }

        info!(
            target = %self.target,
            count = comments.len(),
            "Polled comments"
        );

        // Reverse to return in chronological order (oldest first).
        let events: Vec<LivestreamEvent> = comments
            .into_iter()
            .rev()
            .map(LivestreamEvent::Comment)
            .collect();

        Ok(events)
    }

    /// Polls for new submissions.
    async fn poll_submissions(&mut self) -> Result<Vec<LivestreamEvent>> {
        let url = match &self.target {
            LivestreamTarget::Subreddit(name) => {
                LivestreamEndpoint::subreddit_submissions(name, self.cursor.as_deref())
            }
            LivestreamTarget::Redditor(name) => {
                LivestreamEndpoint::redditor_submissions(name, self.cursor.as_deref())
            }
        };

        debug!(
            target = %self.target,
            source = "submissions",
            cursor = ?self.cursor,
            "Polling for new submissions"
        );

        let response = self.client.get(&url).await?;
        let listing: Listing<SubmissionData> = serde_json::from_value(response)?;

        let submissions: Vec<Submission> = listing
            .data
            .children
            .into_iter()
            .map(|thing| Submission::from(thing.data))
            .collect();

        if let Some(newest) = submissions.first() {
            let new_cursor = format!("t3_{}", newest.id);
            debug!(
                old_cursor = ?self.cursor,
                new_cursor = %new_cursor,
                count = submissions.len(),
                "Updated livestream cursor"
            );
            self.cursor = Some(new_cursor);
        }

        info!(
            target = %self.target,
            count = submissions.len(),
            "Polled submissions"
        );

        // Reverse to return in chronological order (oldest first).
        let events: Vec<LivestreamEvent> = submissions
            .into_iter()
            .rev()
            .map(LivestreamEvent::Submission)
            .collect();

        Ok(events)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn livestream_target_display_subreddit() {
        let target = LivestreamTarget::Subreddit("rust".to_string());

        assert_eq!(target.to_string(), "r/rust");
    }

    #[test]
    fn livestream_target_display_redditor() {
        let target = LivestreamTarget::Redditor("spez".to_string());

        assert_eq!(target.to_string(), "u/spez");
    }

    #[test]
    fn livestream_source_display() {
        assert_eq!(LivestreamSource::Comments.to_string(), "comments");
        assert_eq!(LivestreamSource::Submissions.to_string(), "submissions");
    }

    #[test]
    fn livestream_source_default_is_comments() {
        assert_eq!(LivestreamSource::default(), LivestreamSource::Comments);
    }

    #[test]
    fn livestream_target_equality() {
        let a = LivestreamTarget::Subreddit("rust".to_string());
        let b = LivestreamTarget::Subreddit("rust".to_string());
        let c = LivestreamTarget::Subreddit("python".to_string());
        let d = LivestreamTarget::Redditor("rust".to_string());

        assert_eq!(a, b);
        assert_ne!(a, c);
        assert_ne!(a, d);
    }
}
