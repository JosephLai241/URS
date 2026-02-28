//! Comment model and tree structure.
//!
//! This module defines the `Comment` type and the `CommentTree` structure for representing
//! threaded comment hierarchies.

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

use super::api::{CommentData, EditedField, MoreCommentsData};

/// A Reddit comment.
///
/// This struct contains all the commonly used fields from a Reddit comment.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Comment {
    /// The comment author's username.
    pub author: String,
    /// The comment body as Markdown.
    pub body: String,
    /// The comment body as HTML.
    pub body_html: String,
    /// UTC timestamp when the comment was created.
    pub created_utc: f64,
    /// Whether the comment is distinguished.
    pub distinguished: Option<String>,
    /// Whether/when the comment was edited.
    pub edited: EditedField,
    /// The comment's ID (without prefix).
    pub id: String,
    /// Whether the comment author is the submission author.
    pub is_submitter: bool,
    /// The fullname of the submission this comment belongs to.
    pub link_id: String,
    /// The fullname of the parent (submission or comment).
    pub parent_id: String,
    /// The comment score.
    pub score: i32,
    /// Whether the comment is stickied.
    pub stickied: bool,
    /// Any additional fields not explicitly modeled.
    #[serde(flatten)]
    pub extra: BTreeMap<String, serde_json::Value>,
    /// Nested replies (for structured/tree output).
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub replies: Vec<Comment>,
}

impl From<CommentData> for Comment {
    fn from(data: CommentData) -> Self {
        Self {
            author: data.author,
            body: data.body,
            body_html: data.body_html,
            created_utc: data.created_utc,
            distinguished: data.distinguished,
            edited: data.edited,
            id: data.id,
            is_submitter: data.is_submitter,
            link_id: data.link_id,
            parent_id: data.parent_id,
            score: data.score,
            stickied: data.stickied,
            extra: data.extra.into_iter().collect(),
            replies: Vec::new(),
        }
    }
}

impl Comment {
    /// Returns `true` if this comment has been edited.
    #[must_use]
    pub fn is_edited(&self) -> bool {
        self.edited.is_edited()
    }

    /// Returns the parent ID without the type prefix.
    ///
    /// For example, "t1_abc123" becomes "abc123".
    #[must_use]
    pub fn parent_id_short(&self) -> &str {
        self.parent_id.split('_').last().unwrap_or(&self.parent_id)
    }

    /// Returns `true` if this is a top-level comment (parent is a submission).
    #[must_use]
    pub fn is_top_level(&self) -> bool {
        self.parent_id.starts_with("t3_")
    }
}

/// A "more comments" placeholder that can be expanded.
///
/// Reddit returns these when there are too many comments to return in one request. With Oauth2
/// authentication, these can be expanded via `POST /api/morechildren`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MoreComments {
    /// The IDs of comments that can be loaded.
    pub children: Vec<String>,
    /// The count of additional comments.
    pub count: u32,
    /// The depth in the comment tree.
    pub depth: u32,
    /// The ID of this "more" object.
    pub id: String,
    /// The fullname of this "more" object.
    pub name: String,
    /// The parent ID.
    pub parent_id: String,
}

impl From<MoreCommentsData> for MoreComments {
    fn from(data: MoreCommentsData) -> Self {
        Self {
            children: data.children,
            count: data.count,
            depth: data.depth,
            id: data.id,
            name: data.name,
            parent_id: data.parent_id,
        }
    }
}

/// A comment tree structure for representing threaded comments.
///
/// Provides efficient insertion and traversal of comment hierarchies.
#[derive(Debug, Clone, Default)]
pub struct CommentTree {
    /// Top-level comments (direct replies to the submission).
    comments: Vec<Comment>,
    /// The submission ID this tree belongs to.
    submission_id: String,
}

impl CommentTree {
    /// Creates a new comment tree for the given submission.
    ///
    /// # Arguments
    ///
    /// * `submission_id` - The submission ID (without t3_ prefix)
    #[must_use]
    pub fn new(submission_id: impl Into<String>) -> Self {
        Self {
            comments: Vec::new(),
            submission_id: submission_id.into(),
        }
    }

    /// Returns the submission ID.
    #[must_use]
    pub fn submission_id(&self) -> &str {
        &self.submission_id
    }

    /// Returns the top-level comments.
    #[must_use]
    pub fn comments(&self) -> &[Comment] {
        &self.comments
    }

    /// Consumes the tree and returns the comments.
    #[must_use]
    pub fn into_comments(self) -> Vec<Comment> {
        self.comments
    }

    /// Inserts a comment into the tree at the correct position.
    ///
    /// The comment is placed under its parent based on the `parent_id` field.
    pub fn insert(&mut self, comment: Comment) {
        let parent_short = comment.parent_id_short().to_string();

        // If parent is the submission, add as top-level comment.
        if parent_short == self.submission_id {
            self.comments.push(comment);
            return;
        }

        // Otherwise, find the parent comment and insert as a reply.
        if !Self::insert_into_children(&mut self.comments, &parent_short, comment.clone()) {
            // If we couldn't find the parent, add as top-level. This can happen if comments arrive
            // out of order.
            self.comments.push(comment);
        }
    }

    /// Searches for the parent comment via iterative DFS and inserts the new comment.
    ///
    /// Returns `true` if the parent was found and the comment was inserted.
    fn insert_into_children(
        comments: &mut [Comment],
        parent_id: &str,
        new_comment: Comment,
    ) -> bool {
        let mut stack: Vec<&mut [Comment]> = vec![comments];

        while let Some(slice) = stack.pop() {
            // Check if any comment in this slice is the parent.
            // We need index-based access here because finding the parent
            // requires a mutable borrow to push the new comment.
            let found = slice.iter().position(|c| c.id == parent_id);
            if let Some(idx) = found {
                slice[idx].replies.push(new_comment);
                return true;
            }

            // Parent not in this slice — push each comment's replies onto the
            // stack. We use `split_first_mut` to get non-overlapping mutable
            // borrows of each element's replies.
            let mut rest = slice;
            while let Some((first, remainder)) = rest.split_first_mut() {
                rest = remainder;
                if !first.replies.is_empty() {
                    stack.push(&mut first.replies);
                }
            }
        }

        false
    }

    /// Returns the total number of comments in the tree (including nested).
    #[must_use]
    pub fn total_count(&self) -> usize {
        Self::count_iterative(&self.comments)
    }

    /// Counts all comments in the tree iteratively.
    fn count_iterative(comments: &[Comment]) -> usize {
        let mut count = 0;
        let mut stack: Vec<&[Comment]> = vec![comments];

        while let Some(slice) = stack.pop() {
            for comment in slice {
                count += 1;

                if !comment.replies.is_empty() {
                    stack.push(&comment.replies);
                }
            }
        }

        count
    }

    /// Flattens the tree into a vector of comments (depth-first order).
    ///
    /// This loses the tree structure but can be useful for processing all comments linearly.
    #[must_use]
    pub fn flatten(&self) -> Vec<&Comment> {
        let mut result = Vec::new();
        Self::flatten_iterative(&self.comments, &mut result);

        result
    }

    /// Flattens comments iteratively via DFS (pre-order traversal).
    fn flatten_iterative<'a>(comments: &'a [Comment], result: &mut Vec<&'a Comment>) {
        // Push top-level comments in reverse so the first comment is processed first.
        let mut stack: Vec<&'a Comment> = comments.iter().rev().collect();

        while let Some(comment) = stack.pop() {
            result.push(comment);
            // Push replies in reverse to maintain DFS order.
            for reply in comment.replies.iter().rev() {
                stack.push(reply);
            }
        }
    }
}

impl Serialize for CommentTree {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        self.comments.serialize(serializer)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_comment(id: &str, parent_id: &str) -> Comment {
        Comment {
            author: "testuser".to_string(),
            body: "Test comment".to_string(),
            body_html: "<p>Test comment</p>".to_string(),
            created_utc: 1_234_567_890.0,
            distinguished: None,
            edited: EditedField::Bool(false),
            id: id.to_string(),
            is_submitter: false,
            link_id: "t3_submission".to_string(),
            parent_id: parent_id.to_string(),
            score: 10,
            stickied: false,
            extra: BTreeMap::new(),
            replies: Vec::new(),
        }
    }

    #[test]
    fn comment_is_top_level() {
        let comment = sample_comment("abc", "t3_submission");
        assert!(comment.is_top_level());

        let reply = sample_comment("def", "t1_abc");
        assert!(!reply.is_top_level());
    }

    #[test]
    fn comment_parent_id_short() {
        let comment = sample_comment("abc", "t1_xyz");
        assert_eq!(comment.parent_id_short(), "xyz");
    }

    #[test]
    fn comment_tree_insert_top_level() {
        let mut tree = CommentTree::new("submission");
        let comment = sample_comment("abc", "t3_submission");

        tree.insert(comment);

        assert_eq!(tree.comments().len(), 1);
        assert_eq!(tree.comments()[0].id, "abc");
    }

    #[test]
    fn comment_tree_insert_nested() {
        let mut tree = CommentTree::new("submission");

        let parent = sample_comment("parent", "t3_submission");
        tree.insert(parent);

        let reply = sample_comment("reply", "t1_parent");
        tree.insert(reply);

        assert_eq!(tree.comments().len(), 1);
        assert_eq!(tree.comments()[0].replies.len(), 1);
        assert_eq!(tree.comments()[0].replies[0].id, "reply");
    }

    #[test]
    fn comment_tree_total_count() {
        let mut tree = CommentTree::new("submission");

        tree.insert(sample_comment("a", "t3_submission"));
        tree.insert(sample_comment("b", "t1_a"));
        tree.insert(sample_comment("c", "t1_a"));
        tree.insert(sample_comment("d", "t1_b"));

        assert_eq!(tree.total_count(), 4);
    }

    #[test]
    fn comment_tree_flatten() {
        let mut tree = CommentTree::new("submission");

        tree.insert(sample_comment("a", "t3_submission"));
        tree.insert(sample_comment("b", "t1_a"));

        let flat = tree.flatten();

        assert_eq!(flat.len(), 2);
        assert_eq!(flat[0].id, "a");
        assert_eq!(flat[1].id, "b");
    }
}
