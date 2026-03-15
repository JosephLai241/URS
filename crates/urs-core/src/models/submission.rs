//! Submission (post/link) model.
//!
//! This module defines the `Submission` type representing a Reddit post.

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

use super::api::{EditedField, SubmissionData};

/// A Reddit submission (post/link).
///
/// This struct contains all the commonly used fields from a Reddit submission, with additional
/// fields captured in `extra`.
#[allow(clippy::struct_excessive_bools)]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Submission {
    /// The submission author's username.
    pub author: String,
    /// UTC timestamp when the submission was created.
    pub created_utc: f64,
    /// Whether the submission is distinguished (i.e. by a moderator).
    pub distinguished: Option<String>,
    /// Whether/when the submission was edited.
    pub edited: EditedField,
    /// The submission's ID (without prefix).
    pub id: String,
    /// Whether this is original content.
    pub is_original_content: bool,
    /// Whether this is a self post.
    pub is_self: bool,
    /// The link flair text.
    pub link_flair_text: Option<String>,
    /// Whether the submission is locked.
    pub locked: bool,
    /// The fullname of this submission (i.e. `t3_abc123`).
    pub name: String,
    /// Whether the submission is NSFW.
    pub nsfw: bool,
    /// The number of comments.
    pub num_comments: u32,
    /// The permalink (relative URL).
    pub permalink: String,
    /// The score (upvotes - downvotes).
    pub score: i32,
    /// The self text (for self posts).
    pub selftext: Option<String>,
    /// Whether the submission contains spoilers.
    pub spoiler: bool,
    /// Whether the submission is stickied.
    pub stickied: bool,
    /// The Subreddit name (without r/ prefix).
    pub subreddit: String,
    /// The submission title.
    pub title: String,
    /// The upvote ratio (0.0 to 1.0).
    pub upvote_ratio: f64,
    /// The URL (for link posts) or full permalink (for self posts).
    pub url: String,
    /// Any additional fields not explicitly modeled.
    #[serde(flatten)]
    pub extra: BTreeMap<String, serde_json::Value>,
}

impl From<SubmissionData> for Submission {
    fn from(data: SubmissionData) -> Self {
        Self {
            author: data.author,
            created_utc: data.created_utc,
            distinguished: data.distinguished,
            edited: data.edited,
            id: data.id,
            is_original_content: data.is_original_content,
            is_self: data.is_self,
            link_flair_text: data.link_flair_text,
            locked: data.locked,
            name: data.name,
            nsfw: data.nsfw,
            num_comments: data.num_comments,
            permalink: data.permalink,
            score: data.score,
            selftext: data.selftext,
            spoiler: data.spoiler,
            stickied: data.stickied,
            subreddit: data.subreddit,
            title: data.title,
            upvote_ratio: data.upvote_ratio,
            url: data.url,
            extra: data.extra,
        }
    }
}

impl Submission {
    /// Returns the full URL to this submission on Reddit.
    #[must_use]
    pub fn full_url(&self) -> String {
        format!("https://www.reddit.com{}", self.permalink)
    }

    /// Returns `true` if this submission has been edited.
    #[must_use]
    pub const fn is_edited(&self) -> bool {
        self.edited.is_edited()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_submission() -> Submission {
        Submission {
            author: "testuser".to_string(),
            created_utc: 1_234_567_890.0,
            distinguished: None,
            edited: EditedField::Bool(false),
            id: "abc123".to_string(),
            is_original_content: false,
            is_self: true,
            link_flair_text: None,
            locked: false,
            name: "t3_abc123".to_string(),
            nsfw: false,
            num_comments: 42,
            permalink: "/r/rust/comments/abc123/test_post/".to_string(),
            score: 100,
            selftext: Some("This is a test post".to_string()),
            spoiler: false,
            stickied: false,
            subreddit: "rust".to_string(),
            title: "Test Post".to_string(),
            upvote_ratio: 0.95,
            url: "https://www.reddit.com/r/rust/comments/abc123/test_post/".to_string(),
            extra: BTreeMap::new(),
        }
    }

    #[test]
    fn submission_full_url() {
        let submission = sample_submission();
        assert_eq!(
            submission.full_url(),
            "https://www.reddit.com/r/rust/comments/abc123/test_post/"
        );
    }

    #[test]
    fn submission_is_edited_false() {
        let submission = sample_submission();
        assert!(!submission.is_edited());
    }

    #[test]
    fn submission_is_edited_true() {
        let mut submission = sample_submission();
        submission.edited = EditedField::Timestamp(1_234_567_900.0);

        assert!(submission.is_edited());
    }
}
