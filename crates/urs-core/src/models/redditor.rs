//! Redditor (user) model.
//!
//! This module defines the `Redditor` type representing a Reddit user profile and
//! `RedditorInteractions` for all 14 interaction categories.

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

use super::{Comment, Submission};

/// A Reddit user profile.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Redditor {
    /// Total comment karma.
    pub comment_karma: i64,
    /// UTC timestamp when the account was created.
    pub created_utc: f64,
    /// Whether the account has verified email.
    #[serde(default)]
    pub has_verified_email: bool,
    /// The user's icon/avatar URL.
    pub icon_img: Option<String>,
    /// The user's ID.
    pub id: String,
    /// Whether the account has Reddit Premium.
    #[serde(default)]
    pub is_gold: bool,
    /// Whether the account is a moderator.
    #[serde(default)]
    pub is_mod: bool,
    /// Total link karma.
    pub link_karma: i64,
    /// The username.
    pub name: String,
    /// Any additional fields not explicitly modeled.
    #[serde(flatten)]
    pub extra: BTreeMap<String, serde_json::Value>,
}

/// All interaction categories for a Redditor.
///
/// Reddit provides 14 different categories of user interactions, though some (like downvoted,
/// saved, hidden) are only accessible for the authenticated user.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct RedditorInteractions {
    /// User's comments.
    #[serde(default, skip_serializing_if = "InteractionData::is_empty")]
    pub comments: InteractionData<Comment>,
    /// Controversial content.
    #[serde(default, skip_serializing_if = "InteractionData::is_empty")]
    pub controversial: InteractionData<serde_json::Value>,
    /// Downvoted content (only for authenticated user).
    #[serde(
        default,
        skip_serializing_if = "InteractionData::is_empty_or_forbidden"
    )]
    pub downvoted: InteractionData<serde_json::Value>,
    /// Gilded content.
    #[serde(default, skip_serializing_if = "InteractionData::is_empty")]
    pub gilded: InteractionData<serde_json::Value>,
    /// Gildings given by the user.
    #[serde(
        default,
        skip_serializing_if = "InteractionData::is_empty_or_forbidden"
    )]
    pub gildings: InteractionData<serde_json::Value>,
    /// Hidden content (only for authenticated user).
    #[serde(
        default,
        skip_serializing_if = "InteractionData::is_empty_or_forbidden"
    )]
    pub hidden: InteractionData<serde_json::Value>,
    /// Hot content.
    #[serde(default, skip_serializing_if = "InteractionData::is_empty")]
    pub hot: InteractionData<serde_json::Value>,
    /// Basic user information.
    pub information: Option<Redditor>,
    /// Subreddits moderated by the user.
    #[serde(default, skip_serializing_if = "InteractionData::is_empty")]
    pub moderated: InteractionData<serde_json::Value>,
    /// User's multireddits.
    #[serde(default, skip_serializing_if = "InteractionData::is_empty")]
    pub multireddits: InteractionData<serde_json::Value>,
    /// New content.
    #[serde(default, skip_serializing_if = "InteractionData::is_empty")]
    pub new: InteractionData<serde_json::Value>,
    /// Saved content (only for authenticated user).
    #[serde(
        default,
        skip_serializing_if = "InteractionData::is_empty_or_forbidden"
    )]
    pub saved: InteractionData<serde_json::Value>,
    /// User's submissions.
    #[serde(default, skip_serializing_if = "InteractionData::is_empty")]
    pub submissions: InteractionData<Submission>,
    /// Top content.
    #[serde(default, skip_serializing_if = "InteractionData::is_empty")]
    pub top: InteractionData<serde_json::Value>,
    /// Upvoted content (only for authenticated user).
    #[serde(
        default,
        skip_serializing_if = "InteractionData::is_empty_or_forbidden"
    )]
    pub upvoted: InteractionData<serde_json::Value>,
}

/// Data for an interaction category.
///
/// This can hold actual data items or indicate that access was forbidden.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum InteractionData<T> {
    /// The interaction data was successfully retrieved.
    Data(Vec<T>),
    /// Access to this interaction category was forbidden.
    Forbidden,
}

impl<T> Default for InteractionData<T> {
    fn default() -> Self {
        Self::Data(Vec::new())
    }
}

impl<T> InteractionData<T> {
    /// Returns `true` if this contains no data.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        match self {
            Self::Data(items) => items.is_empty(),
            Self::Forbidden => false,
        }
    }

    /// Returns `true` if this is empty or forbidden.
    #[must_use]
    pub fn is_empty_or_forbidden(&self) -> bool {
        match self {
            Self::Data(items) => items.is_empty(),
            Self::Forbidden => true,
        }
    }

    /// Returns the data as a slice, or empty if forbidden.
    #[must_use]
    pub fn as_slice(&self) -> &[T] {
        match self {
            Self::Data(items) => items,
            Self::Forbidden => &[],
        }
    }

    /// Returns `true` if access was forbidden.
    #[must_use]
    pub fn is_forbidden(&self) -> bool {
        matches!(self, Self::Forbidden)
    }
}

impl<T> From<Vec<T>> for InteractionData<T> {
    fn from(items: Vec<T>) -> Self {
        Self::Data(items)
    }
}

impl Redditor {
    /// Returns the account age in days.
    #[must_use]
    pub fn account_age_days(&self) -> f64 {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_secs_f64())
            .unwrap_or(0.0);

        (now - self.created_utc) / 86400.0
    }

    /// Returns the total karma (link + comment).
    #[must_use]
    pub fn total_karma(&self) -> i64 {
        self.link_karma + self.comment_karma
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_redditor() -> Redditor {
        Redditor {
            comment_karma: 5000,
            created_utc: 1_234_567_890.0,
            has_verified_email: true,
            icon_img: Some("https://example.com/icon.png".to_string()),
            id: "abc123".to_string(),
            is_gold: false,
            is_mod: true,
            link_karma: 1000,
            name: "testuser".to_string(),
            extra: BTreeMap::new(),
        }
    }

    #[test]
    fn redditor_total_karma() {
        let user = sample_redditor();
        assert_eq!(user.total_karma(), 6000);
    }

    #[test]
    fn interaction_data_is_empty() {
        let empty: InteractionData<String> = InteractionData::Data(vec![]);
        assert!(empty.is_empty());

        let with_data: InteractionData<String> = InteractionData::Data(vec!["test".to_string()]);
        assert!(!with_data.is_empty());

        let forbidden: InteractionData<String> = InteractionData::Forbidden;
        assert!(!forbidden.is_empty()); // Forbidden is not "empty"
    }

    #[test]
    fn interaction_data_is_forbidden() {
        let data: InteractionData<String> = InteractionData::Data(vec![]);
        assert!(!data.is_forbidden());

        let forbidden: InteractionData<String> = InteractionData::Forbidden;
        assert!(forbidden.is_forbidden());
    }

    #[test]
    fn interaction_data_from_vec() {
        let items = vec!["a".to_string(), "b".to_string()];
        let data: InteractionData<String> = items.into();

        assert_eq!(data.as_slice().len(), 2);
    }
}
