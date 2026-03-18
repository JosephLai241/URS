//! Data models for Reddit entities.
//!
//! This module defines the data structures for Reddit submissions, comments, Redditors, and
//! Subreddits Each model captures known fields while also preserving any additional fields Reddit
//! may return via the `extra` field.

pub mod api;
mod comment;
mod redditor;
mod submission;
mod subreddit;

pub use api::{Listing, ListingData, Thing, ThingData};
pub use comment::{Comment, CommentTree, CommentsResult, MoreComments};
pub use redditor::{InteractionData, Redditor, RedditorInteractions};
pub use submission::Submission;
pub use subreddit::{Subreddit, SubredditRules};
