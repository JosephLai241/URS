//! Comment parsing and collection from Reddit API responses.
//!
//! This module handles the transformation of raw Reddit API JSON responses into structured
//! [`Comment`] and [`MoreComments`] types. It uses a stack-based DFS to traverse nested
//! comment trees without risking stack overflow on deeply nested threads.

use tracing::{debug, warn};

use crate::error::Result;
use crate::models::api::{CommentData, MoreCommentsData, RepliesField};
use crate::models::{Comment, MoreComments};

/// Converts listing children to JSON values, logging any conversion failures.
pub(super) fn children_to_values<T: serde::Serialize>(children: Vec<T>) -> Vec<serde_json::Value> {
    children
        .into_iter()
        .filter_map(|thing| match serde_json::to_value(thing) {
            Ok(value) => Some(value),
            Err(err) => {
                warn!("Failed to convert comment thing to JSON value: {err}");
                None
            }
        })
        .collect()
}

/// Iteratively collects comments and "more" stubs from the API response.
///
/// Uses a stack-based DFS to avoid stack overflow on deeply nested threads. Each comment's
/// replies are pushed onto the stack for processing, while the comment itself and any "more
/// comments" stubs are collected into their respective output vectors.
///
/// # Arguments
///
/// * `children` - The top-level children from a Reddit comments listing
/// * `comments` - Output vector to collect parsed comments into
/// * `more_stubs` - Output vector to collect "more comments" stubs into
///
/// # Errors
///
/// Returns an error if comment data fails to deserialize.
pub(super) fn collect_comments(
    children: &[serde_json::Value],
    comments: &mut Vec<Comment>,
    more_stubs: &mut Vec<MoreComments>,
) -> Result<()> {
    let mut stack: Vec<Vec<serde_json::Value>> = vec![children.to_vec()];

    while let Some(current_children) = stack.pop() {
        for child in &current_children {
            let kind = child.get("kind").and_then(|k| k.as_str()).unwrap_or("");

            match kind {
                "t1" => {
                    if let Some(data) = child.get("data") {
                        let comment_data: CommentData = serde_json::from_value(data.clone())?;

                        if let RepliesField::Listing(replies_listing) = &comment_data.replies {
                            let reply_values: Vec<serde_json::Value> = replies_listing
                                .data
                                .children
                                .iter()
                                .map(|c| serde_json::to_value(c).unwrap_or_default())
                                .collect();

                            if !reply_values.is_empty() {
                                stack.push(reply_values);
                            }
                        }

                        comments.push(Comment::from(comment_data));
                    }
                }
                "more" => {
                    if let Some(data) = child.get("data") {
                        if let Ok(more_data) =
                            serde_json::from_value::<MoreCommentsData>(data.clone())
                        {
                            if !more_data.children.is_empty() || more_data.count > 0 {
                                more_stubs.push(MoreComments::from(more_data));
                            }
                        }
                    }
                }
                _ => {
                    debug!(kind = kind, "Unknown child kind in comments");
                }
            }
        }
    }

    Ok(())
}
