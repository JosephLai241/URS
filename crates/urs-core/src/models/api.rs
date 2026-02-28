//! Raw Reddit API response types.
//!
//! These types represent the structure of Reddit's API responses before they are transformed into
//! our domain models.

use std::collections::{BTreeMap, HashMap};

use serde::{Deserialize, Serialize};

/// A Reddit API "thing" wrapper.
///
/// Reddit wraps most objects in a `{ kind, data }` structure where `kind` indicates the type of
/// object (i.e. "t1" for comment, "t3" for link/submission).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Thing<T> {
    /// The kind of thing:
    /// - t1 = comment
    /// - t2 = account
    /// - t3 = link
    /// - t4 = message
    /// - t5 = Subreddit
    /// - t6 = award
    pub kind: String,
    /// The actual data for this thing.
    pub data: T,
}

/// A listing response from Reddit.
///
/// Listings are paginated collections of things, used for subreddit posts, user content, comments,
/// etc.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Listing<T> {
    /// The kind (always "Listing").
    pub kind: String,
    /// The listing data containing the items and pagination info.
    pub data: ListingData<T>,
}

/// The data portion of a listing.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListingData<T> {
    /// The fullname of the thing that follows after this page (for pagination).
    pub after: Option<String>,
    /// The fullname of the thing that follows before this page.
    pub before: Option<String>,
    /// The number of items in this listing.
    #[serde(default)]
    pub dist: Option<u32>,
    /// The modhash (deprecated, usually null).
    pub modhash: Option<String>,
    /// The geo filter (usually null).
    pub geo_filter: Option<String>,
    /// The actual items in this listing.
    pub children: Vec<Thing<T>>,
}

/// Raw thing data that can be any Reddit object type.
///
/// This is used when the exact type isn't known at compile time,
/// such as in comment listings that may contain both comments and "more" stubs.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum ThingData {
    /// A submission/link.
    Submission(Box<SubmissionData>),
    /// A comment.
    Comment(Box<CommentData>),
    /// A "more comments" placeholder.
    More(MoreCommentsData),
    /// Unknown data (captured as raw JSON).
    Unknown(serde_json::Value),
}

/// Raw submission data from the Reddit API.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SubmissionData {
    /// The submission author's username.
    pub author: String,
    /// The author's flair text.
    pub author_flair_text: Option<String>,
    /// UTC timestamp when the submission was created.
    pub created_utc: f64,
    /// Whether the submission is distinguished (i.e. by a moderator).
    pub distinguished: Option<String>,
    /// Whether/when the submission was edited (`false` or UTC timestamp).
    #[serde(default)]
    pub edited: EditedField,
    /// The submission's ID (without prefix).
    pub id: String,
    /// Whether this is original content.
    #[serde(default)]
    pub is_original_content: bool,
    /// Whether this is a self post.
    #[serde(default)]
    pub is_self: bool,
    /// The link flair text.
    pub link_flair_text: Option<String>,
    /// Whether the submission is locked.
    #[serde(default)]
    pub locked: bool,
    /// The fullname of this submission (i.e. "t3_abc123").
    pub name: String,
    /// Whether the submission is NSFW.
    #[serde(rename = "over_18")]
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
    #[serde(default)]
    pub spoiler: bool,
    /// Whether the submission is stickied.
    #[serde(default)]
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
    pub extra: HashMap<String, serde_json::Value>,
}

/// Raw comment data from the Reddit API.
///
/// Many fields use `#[serde(default)]` because Reddit returns `null` for deleted and removed
/// comments. This ensures they deserialize successfully with placeholder values rather than
/// failing.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CommentData {
    /// The comment author's username.
    ///
    /// Set to `"[deleted]"` by Reddit when the author has deleted their account or comment.
    #[serde(default = "CommentData::default_deleted")]
    pub author: String,
    /// The comment body as Markdown.
    ///
    /// Set to `"[deleted]"` or `"[removed]"` by Reddit for deleted/removed comments.
    #[serde(default = "CommentData::default_deleted")]
    pub body: String,
    /// The comment body as HTML.
    #[serde(default)]
    pub body_html: String,
    /// UTC timestamp when the comment was created.
    #[serde(default)]
    pub created_utc: f64,
    /// Whether the comment is distinguished.
    pub distinguished: Option<String>,
    /// Whether/when the comment was edited.
    #[serde(default)]
    pub edited: EditedField,
    /// The comment's ID (without prefix).
    pub id: String,
    /// Whether the comment author is the submission author.
    #[serde(default)]
    pub is_submitter: bool,
    /// The fullname of the submission this comment belongs to.
    #[serde(default)]
    pub link_id: String,
    /// The fullname of the parent (submission or comment).
    #[serde(default)]
    pub parent_id: String,
    /// The comment score.
    #[serde(default)]
    pub score: i32,
    /// Whether the comment is stickied.
    #[serde(default)]
    pub stickied: bool,
    /// Nested replies (can be empty string, null, or a Listing).
    #[serde(default)]
    pub replies: RepliesField,
    /// Any additional fields not explicitly modeled.
    #[serde(flatten)]
    pub extra: BTreeMap<String, serde_json::Value>,
}

impl CommentData {
    /// Default value for fields on deleted/removed comments.
    fn default_deleted() -> String {
        "[deleted]".to_string()
    }
}

/// Data for a "more comments" placeholder.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MoreCommentsData {
    /// The IDs of comments that can be loaded.
    pub children: Vec<String>,
    /// The count of additional comments.
    pub count: u32,
    /// The ID of this "more" object.
    pub id: String,
    /// The fullname of this "more" object.
    pub name: String,
    /// The parent ID.
    pub parent_id: String,
    /// The depth in the comment tree.
    pub depth: u32,
}

/// The `edited` field can be `false` or a UTC timestamp.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum EditedField {
    /// Not edited.
    Bool(bool),
    /// Edited at this UTC timestamp.
    Timestamp(f64),
}

impl Default for EditedField {
    fn default() -> Self {
        Self::Bool(false)
    }
}

impl EditedField {
    /// Returns `true` if the item has been edited.
    #[must_use]
    pub fn is_edited(&self) -> bool {
        match self {
            Self::Bool(b) => *b,
            Self::Timestamp(_) => true,
        }
    }

    /// Returns the edit timestamp if available.
    #[must_use]
    pub fn timestamp(&self) -> Option<f64> {
        match self {
            Self::Bool(_) => None,
            Self::Timestamp(ts) => Some(*ts),
        }
    }
}

/// The `replies` field can be an empty string, null, or a Listing.
///
/// Reddit's API is inconsistent with this field — it may return `""`, `null`, `false`, or a full
/// Listing object. We try the most specific variant first and fall back to ignoring unrecognized
/// values.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum RepliesField {
    /// A listing of reply comments.
    Listing(Box<Listing<CommentData>>),
    /// Empty string (Reddit sometimes returns this).
    EmptyString(String),
    /// Any other value (`null`, `false`, etc.) — treated as no replies.
    Other(serde_json::Value),
}

impl Default for RepliesField {
    fn default() -> Self {
        Self::Other(serde_json::Value::Null)
    }
}

impl RepliesField {
    /// Returns the replies as a vector of comment data, or empty if none.
    #[must_use]
    pub fn into_vec(self) -> Vec<Thing<CommentData>> {
        match self {
            Self::Listing(listing) => listing.data.children,
            Self::EmptyString(_) | Self::Other(_) => vec![],
        }
    }
}

/// Response from the `/api/morechildren` endpoint.
///
/// This wraps the JSON response which has the structure:
/// `{ "json": { "data": { "things": [...] } } }`
#[derive(Debug, Clone, Deserialize)]
pub struct MoreChildrenResponse {
    /// The JSON wrapper.
    pub json: MoreChildrenJson,
}

/// Inner JSON wrapper for morechildren response.
#[derive(Debug, Clone, Deserialize)]
pub struct MoreChildrenJson {
    /// The data containing the expanded comments.
    pub data: MoreChildrenJsonData,
}

/// Data portion of the morechildren response.
#[derive(Debug, Clone, Deserialize)]
pub struct MoreChildrenJsonData {
    /// The expanded comment/more things.
    pub things: Vec<Thing<serde_json::Value>>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn edited_field_bool_false() {
        let edited: EditedField = serde_json::from_str("false").unwrap();

        assert!(!edited.is_edited());
        assert!(edited.timestamp().is_none());
    }

    #[test]
    fn edited_field_timestamp() {
        let edited: EditedField = serde_json::from_str("1234567890.0").unwrap();

        assert!(edited.is_edited());
        assert!((edited.timestamp().unwrap() - 1_234_567_890.0).abs() < f64::EPSILON);
    }

    #[test]
    fn replies_field_empty_string() {
        let replies: RepliesField = serde_json::from_str(r#""""#).unwrap();
        assert!(replies.into_vec().is_empty());
    }
}
