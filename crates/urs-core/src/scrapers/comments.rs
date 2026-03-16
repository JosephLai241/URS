//! This module provides functionality to scrape submission comments.

use tracing::{debug, info, warn};

use crate::client::RedditClient;
use crate::client::endpoints::CommentsEndpoint;
use crate::error::{Error, Result};
use crate::models::api::{
    CommentData, Listing, MoreChildrenResponse, MoreCommentsData, RepliesField,
};
use crate::models::{Comment, CommentTree, MoreComments};

/// Maximum number of child IDs per morechildren request.
///
/// Reddit's API limits the `children` parameter to ~100 IDs per request. We batch in chunks of
/// this size.
const MORE_CHILDREN_BATCH_SIZE: usize = 100;

/// Scraper for submission comments with "more comments" expansion.
///
/// Provides methods to fetch comments from submissions and build comment trees.
#[derive(Debug)]
pub struct CommentsScraper<'a> {
    /// The Reddit client for making authenticated API requests.
    client: &'a RedditClient,
}

impl<'a> CommentsScraper<'a> {
    /// Creates a new comments scraper.
    ///
    /// # Arguments
    ///
    /// * `client` - The authenticated Reddit client to use for requests
    #[must_use]
    pub const fn new(client: &'a RedditClient) -> Self {
        Self { client }
    }

    /// Fetches comments from a submission URL.
    ///
    /// This is a convenience method that parses the URL to extract the Subreddit and submission
    /// ID.
    ///
    /// # Arguments
    ///
    /// * `url` - The full URL to the submission
    /// * `limit` - Maximum number of comments (`None` for all available)
    /// * `structured` - If true, returns threaded tree; if false, returns flat list
    ///
    /// # Errors
    ///
    /// Returns an error if the URL is invalid or the API request fails.
    pub async fn from_url(
        &self,
        url: &str,
        limit: Option<usize>,
        structured: bool,
    ) -> Result<Vec<Comment>> {
        let (subreddit, submission_id) = Self::parse_submission_url(url)?;
        self.fetch(&subreddit, &submission_id, limit, structured)
            .await
    }

    /// Fetches comments from a submission.
    ///
    /// With `OAuth2` authentication, "more comments" placeholders are automatically expanded to
    /// retrieve the full comment tree.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `submission_id` - The submission ID (without t3_ prefix)
    /// * `limit` - Maximum number of comments (None for all available)
    /// * `structured` - If `true`, returns threaded tree; if `false`, returns flat list
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails or the response is malformed.
    pub async fn fetch(
        &self,
        subreddit: &str,
        submission_id: &str,
        limit: Option<usize>,
        structured: bool,
    ) -> Result<Vec<Comment>> {
        info!(
            subreddit = subreddit,
            submission_id = submission_id,
            limit = ?limit,
            structured = structured,
            "Fetching comments"
        );

        // Request the maximum number of comments upfront (Reddit caps at 500).
        // This reduces the number of "more" stubs we need to expand later.
        let url = CommentsEndpoint::submission(subreddit, submission_id, Some(500), None);
        let response = self.client.get(&url).await?;

        let listings: Vec<serde_json::Value> = serde_json::from_value(response)?;
        if listings.len() < 2 {
            return Err(Error::UnexpectedResponse(
                "Expected array with submission and comments".to_string(),
            ));
        }

        let comments_listing: Listing<serde_json::Value> =
            serde_json::from_value(listings[1].clone())?;

        let mut comments: Vec<Comment> = Vec::new();
        let mut more_stubs: Vec<MoreComments> = Vec::new();

        let children_values = Self::children_to_values(comments_listing.data.children);

        Self::collect_comments(&children_values, &mut comments, &mut more_stubs)?;

        debug!(
            initial_comments = comments.len(),
            more_stubs = more_stubs.len(),
            "Collected initial comments"
        );

        // Expand "more comments" stubs via POST /api/morechildren.
        // This runs iteratively: expanding one batch of stubs may yield new "more" stubs that need
        // further expansion.
        let link_id = format!("t3_{submission_id}");
        let mut pending_stubs = more_stubs;

        while !pending_stubs.is_empty() {
            let mut next_stubs: Vec<MoreComments> = Vec::new();

            for stub in &pending_stubs {
                if stub.children.is_empty() {
                    // "Continue this thread" stub — fetch the deep thread by requesting the parent
                    // comment's permalink.
                    let parent_id = stub
                        .parent_id
                        .strip_prefix("t1_")
                        .unwrap_or(&stub.parent_id);
                    debug!(
                        parent_id = parent_id,
                        count = stub.count,
                        "Fetching deep thread"
                    );

                    match self
                        .fetch_deep_thread(subreddit, submission_id, parent_id)
                        .await
                    {
                        Ok((deep_comments, deep_stubs)) => {
                            debug!(expanded = deep_comments.len(), "Fetched deep thread");

                            comments.extend(deep_comments);
                            next_stubs.extend(deep_stubs);
                        }
                        Err(e) => {
                            warn!(error = %e, parent_id = parent_id, "Failed to fetch deep thread");
                        }
                    }

                    continue;
                }

                debug!(
                    stub_id = %stub.id,
                    child_count = stub.children.len(),
                    reported_count = stub.count,
                    "Expanding more comments stub"
                );

                let expanded = self.expand_more_children(&link_id, &stub.children).await;

                match expanded {
                    Ok((new_comments, nested_stubs)) => {
                        debug!(
                            expanded = new_comments.len(),
                            nested_stubs = nested_stubs.len(),
                            "Expanded more comments"
                        );

                        comments.extend(new_comments);
                        next_stubs.extend(nested_stubs);
                    }
                    Err(e) => {
                        warn!(error = %e, stub_id = %stub.id, "Failed to expand more comments");
                    }
                }
            }

            pending_stubs = next_stubs;
        }

        if let Some(limit) = limit {
            comments.truncate(limit);
        }

        info!(count = comments.len(), "Comments fetch complete");

        if structured {
            let mut tree = CommentTree::new(submission_id);

            for comment in comments {
                tree.insert(comment);
            }

            Ok(tree.into_comments())
        } else {
            Ok(comments)
        }
    }

    /// Expands "more comments" by posting to `/api/morechildren`.
    ///
    /// Handles batching since the API limits the number of child IDs per request.
    ///
    /// Returns both the expanded comments and any nested "more" stubs that were discovered and
    /// need further expansion.
    async fn expand_more_children(
        &self,
        link_id: &str,
        children: &[String],
    ) -> Result<(Vec<Comment>, Vec<MoreComments>)> {
        let mut all_comments = Vec::new();
        let mut nested_stubs = Vec::new();

        for chunk in children.chunks(MORE_CHILDREN_BATCH_SIZE) {
            let children_str = chunk.join(",");
            let url = CommentsEndpoint::more_children();

            let response = self
                .client
                .post(
                    &url,
                    &[
                        ("link_id", link_id),
                        ("children", &children_str),
                        ("api_type", "json"),
                    ],
                )
                .await?;

            let mc_response: MoreChildrenResponse = serde_json::from_value(response)?;

            for thing in mc_response.json.data.things {
                match thing.kind.as_str() {
                    "t1" => match serde_json::from_value::<CommentData>(thing.data) {
                        Ok(comment_data) => {
                            all_comments.push(Comment::from(comment_data));
                        }
                        Err(e) => {
                            warn!(error = %e, "Failed to parse comment data");
                        }
                    },
                    "more" => {
                        if let Ok(more_data) =
                            serde_json::from_value::<MoreCommentsData>(thing.data)
                        {
                            if !more_data.children.is_empty() || more_data.count > 0 {
                                nested_stubs.push(MoreComments::from(more_data));
                            }
                        }
                    }
                    _ => {}
                }
            }
        }

        Ok((all_comments, nested_stubs))
    }

    /// Fetches a deep comment thread by requesting a comment's permalink.
    ///
    /// This handles "continue this thread" stubs where Reddit indicates there are deeper replies
    /// but doesn't provide their IDs. We fetch the thread rooted at the parent comment to discover
    /// those replies.
    async fn fetch_deep_thread(
        &self,
        subreddit: &str,
        submission_id: &str,
        comment_id: &str,
    ) -> Result<(Vec<Comment>, Vec<MoreComments>)> {
        let url = CommentsEndpoint::comment_thread(subreddit, submission_id, comment_id);
        let response = self.client.get(&url).await?;

        let listings: Vec<serde_json::Value> = serde_json::from_value(response)?;
        if listings.len() < 2 {
            return Ok((vec![], vec![]));
        }

        let comments_listing: Listing<serde_json::Value> =
            serde_json::from_value(listings[1].clone())?;

        let children_values = Self::children_to_values(comments_listing.data.children);

        let mut comments = Vec::new();
        let mut more_stubs = Vec::new();
        Self::collect_comments(&children_values, &mut comments, &mut more_stubs)?;

        Ok((comments, more_stubs))
    }

    /// Converts listing children to JSON values, logging any conversion failures.
    fn children_to_values<T: serde::Serialize>(children: Vec<T>) -> Vec<serde_json::Value> {
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
    /// Uses a stack-based DFS to avoid stack overflow on deeply nested threads.
    fn collect_comments(
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

    /// Parses a Reddit submission URL to extract Subreddit and submission ID.
    ///
    /// Supports URLs like:
    /// - `https://www.reddit.com/r/rust/comments/abc123/title/`
    /// - `https://reddit.com/r/rust/comments/abc123/`
    /// - `https://old.reddit.com/r/rust/comments/abc123/title/`
    fn parse_submission_url(url: &str) -> Result<(String, String)> {
        let url = url::Url::parse(url)?;

        let path_segments: Vec<&str> = url
            .path_segments()
            .map(Iterator::collect)
            .unwrap_or_default();

        // Expects segments that look like this: ["r", "subreddit", "comments", "id", ...]
        if path_segments.len() < 4 {
            return Err(Error::InvalidArgument(format!(
                "Invalid submission URL: {url}"
            )));
        }

        if path_segments[0] != "r" || path_segments[2] != "comments" {
            return Err(Error::InvalidArgument(format!(
                "Invalid submission URL format: {url}"
            )));
        }

        let subreddit = path_segments[1].to_string();
        let submission_id = path_segments[3].to_string();

        Ok((subreddit, submission_id))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_submission_url_standard() {
        let url = "https://www.reddit.com/r/rust/comments/abc123/post_title/";
        let (sub, id) = CommentsScraper::parse_submission_url(url).unwrap();

        assert_eq!(sub, "rust");
        assert_eq!(id, "abc123");
    }

    #[test]
    fn parse_submission_url_no_title() {
        let url = "https://reddit.com/r/askreddit/comments/xyz789/";
        let (sub, id) = CommentsScraper::parse_submission_url(url).unwrap();

        assert_eq!(sub, "askreddit");
        assert_eq!(id, "xyz789");
    }

    #[test]
    fn parse_submission_url_old_reddit() {
        let url = "https://old.reddit.com/r/programming/comments/def456/title/";
        let (sub, id) = CommentsScraper::parse_submission_url(url).unwrap();

        assert_eq!(sub, "programming");
        assert_eq!(id, "def456");
    }

    #[test]
    fn parse_submission_url_invalid() {
        let url = "https://www.reddit.com/r/rust/";
        assert!(CommentsScraper::parse_submission_url(url).is_err());
    }
}
