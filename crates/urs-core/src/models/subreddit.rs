//! Subreddit model.
//!
//! This module defines the `Subreddit` type representing Subreddit information
//! and `SubredditRules` for Subreddit posting rules.

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

/// A Reddit Subreddit.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Subreddit {
    /// The number of users currently online.
    #[serde(default)]
    pub accounts_active: Option<u64>,
    /// The Subreddit banner URL.
    pub banner_img: Option<String>,
    /// UTC timestamp when the Subreddit was created.
    pub created_utc: f64,
    /// The full description (sidebar).
    pub description: String,
    /// The Subreddit name (without r/ prefix).
    pub display_name: String,
    /// The Subreddit icon URL.
    pub icon_img: Option<String>,
    /// Whether the Subreddit is NSFW.
    #[serde(rename = "over18")]
    pub nsfw: bool,
    /// The public description.
    pub public_description: String,
    /// The submission type allowed (any, link, self).
    #[serde(default)]
    pub submission_type: Option<String>,
    /// The number of subscribers.
    pub subscribers: u64,
    /// The Subreddit type (public, private, restricted, etc.).
    pub subreddit_type: String,
    /// The Subreddit title.
    pub title: String,
    /// Any additional fields not explicitly modeled.
    #[serde(flatten)]
    pub extra: BTreeMap<String, serde_json::Value>,
}

/// Subreddit posting rules.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SubredditRules {
    /// The list of rules.
    pub rules: Vec<Rule>,
    /// Site-wide rules that apply.
    #[serde(default)]
    pub site_rules: Vec<String>,
}

/// A single Subreddit rule.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Rule {
    /// UTC timestamp when the rule was created.
    pub created_utc: f64,
    /// The rule description.
    pub description: String,
    /// The rule description as HTML.
    pub description_html: Option<String>,
    /// The rule kind (link, comment, all).
    pub kind: String,
    /// Priority/order of the rule.
    pub priority: i32,
    /// Short name/title of the rule.
    pub short_name: String,
    /// The violation reason text.
    pub violation_reason: String,
}

impl Subreddit {
    /// Returns the full Subreddit path (i.e. "r/rust").
    #[must_use]
    pub fn path(&self) -> String {
        format!("r/{}", self.display_name)
    }

    /// Returns the full URL to this Subreddit.
    #[must_use]
    pub fn url(&self) -> String {
        format!("https://www.reddit.com/r/{}/", self.display_name)
    }

    /// Returns `true` if this is a public Subreddit.
    #[must_use]
    pub fn is_public(&self) -> bool {
        self.subreddit_type == "public"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_subreddit() -> Subreddit {
        Subreddit {
            accounts_active: Some(1500),
            banner_img: None,
            created_utc: 1_234_567_890.0,
            description: "Full sidebar description".to_string(),
            display_name: "rust".to_string(),
            icon_img: None,
            nsfw: false,
            public_description: "A place for all things related to Rust".to_string(),
            submission_type: Some("any".to_string()),
            subscribers: 250_000,
            subreddit_type: "public".to_string(),
            title: "The Rust Programming Language".to_string(),
            extra: BTreeMap::new(),
        }
    }

    #[test]
    fn subreddit_path() {
        let sub = sample_subreddit();
        assert_eq!(sub.path(), "r/rust");
    }

    #[test]
    fn subreddit_url() {
        let sub = sample_subreddit();
        assert_eq!(sub.url(), "https://www.reddit.com/r/rust/");
    }

    #[test]
    fn subreddit_is_public() {
        let sub = sample_subreddit();
        assert!(sub.is_public());

        let mut private_sub = sample_subreddit();
        private_sub.subreddit_type = "private".to_string();
        assert!(!private_sub.is_public());
    }
}
