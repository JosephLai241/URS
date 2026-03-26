//! Scraper for submission comments with "more comments" expansion.
//!
//! This module provides [`CommentsScraper`], which fetches comments from Reddit submissions
//! and builds comment trees. It handles pagination through Reddit's "more comments" stubs,
//! including both batched child expansion and deep thread fetching.

mod parser;

use tracing::{debug, info, warn};

use crate::client::RedditClient;
use crate::client::endpoints::CommentsEndpoint;
use crate::error::{Error, Result};
use crate::models::Submission;
use crate::models::api::{
    CommentData, Listing, MoreChildrenResponse, MoreCommentsData, SubmissionData,
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

    /// Validates that a submission URL points to an accessible submission.
    ///
    /// Makes a lightweight request (zero comments, zero depth) to verify the submission exists
    /// and is accessible.
    ///
    /// # Arguments
    ///
    /// * `url` - The full URL to the submission
    ///
    /// # Errors
    ///
    /// Returns an error if the URL is invalid, the submission does not exist, or the API
    /// request fails.
    pub async fn validate_url(&self, url: &str) -> Result<()> {
        let (subreddit, submission_id) = Self::parse_submission_url(url)?;
        let endpoint = CommentsEndpoint::submission(&subreddit, &submission_id, Some(0), Some(0));
        self.client.get(&endpoint).await?;

        Ok(())
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
    /// # Returns
    ///
    /// A tuple of `(submission, comments, total_count)`. The submission is the parent post's
    /// metadata. The total count reflects the number of comments before tree structuring, so
    /// callers don't need to re-traverse the tree to count.
    ///
    /// # Errors
    ///
    /// Returns an error if the URL is invalid or the API request fails.
    pub async fn from_url(
        &self,
        url: &str,
        limit: Option<usize>,
        structured: bool,
    ) -> Result<(Submission, Vec<Comment>, usize)> {
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
    /// # Returns
    ///
    /// A tuple of `(submission, comments, total_count)`. The submission is the parent post's
    /// metadata. The total count reflects the number of comments before tree structuring, so
    /// callers don't need to re-traverse the tree to count.
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
    ) -> Result<(Submission, Vec<Comment>, usize)> {
        info!(
            subreddit = subreddit,
            submission_id = submission_id,
            limit = ?limit,
            structured = structured,
            "Fetching comments"
        );

        let (submission, mut comments, more_stubs) =
            self.fetch_initial(subreddit, submission_id).await?;

        self.expand_all_stubs(subreddit, submission_id, more_stubs, &mut comments)
            .await;

        if let Some(limit) = limit {
            comments.truncate(limit);
        }

        let total = comments.len();
        info!(count = total, "Comments fetch complete");

        if structured {
            let mut tree = CommentTree::new(submission_id);

            for comment in comments {
                tree.insert(comment);
            }

            Ok((submission, tree.into_comments(), total))
        } else {
            Ok((submission, comments, total))
        }
    }

    /// Fetches the initial submission metadata and top-level comments from the API.
    ///
    /// Returns the submission, parsed comments, and any "more comments" stubs that need further
    /// expansion.
    async fn fetch_initial(
        &self,
        subreddit: &str,
        submission_id: &str,
    ) -> Result<(Submission, Vec<Comment>, Vec<MoreComments>)> {
        // Request the maximum number of comments upfront (Reddit caps at 500).
        let url = CommentsEndpoint::submission(subreddit, submission_id, Some(500), None);
        let response = self.client.get(&url).await?;

        let listings: Vec<serde_json::Value> = serde_json::from_value(response)?;
        if listings.len() < 2 {
            return Err(Error::UnexpectedResponse(
                "Expected array with submission and comments".to_string(),
            ));
        }

        // Parse the submission metadata from listings[0].
        let submission_listing: Listing<serde_json::Value> =
            serde_json::from_value(listings[0].clone())?;
        let submission_thing = submission_listing
            .data
            .children
            .into_iter()
            .next()
            .ok_or_else(|| Error::UnexpectedResponse("No submission in listings[0]".to_string()))?;
        let submission_data: SubmissionData = serde_json::from_value(submission_thing.data)?;
        let submission = Submission::from(submission_data);

        debug!(
            title = %submission.title,
            author = %submission.author,
            score = submission.score,
            "Parsed submission metadata"
        );

        let comments_listing: Listing<serde_json::Value> =
            serde_json::from_value(listings[1].clone())?;

        let mut comments: Vec<Comment> = Vec::new();
        let mut more_stubs: Vec<MoreComments> = Vec::new();

        let children_values = parser::children_to_values(comments_listing.data.children);
        parser::collect_comments(&children_values, &mut comments, &mut more_stubs)?;

        debug!(
            initial_comments = comments.len(),
            more_stubs = more_stubs.len(),
            "Collected initial comments"
        );

        Ok((submission, comments, more_stubs))
    }

    /// Iteratively expands all "more comments" stubs.
    ///
    /// Expanding one batch of stubs may yield new stubs that need further expansion, so this loops
    /// until no pending stubs remain.
    async fn expand_all_stubs(
        &self,
        subreddit: &str,
        submission_id: &str,
        initial_stubs: Vec<MoreComments>,
        comments: &mut Vec<Comment>,
    ) {
        let link_id = format!("t3_{submission_id}");
        let mut pending_stubs = initial_stubs;

        while !pending_stubs.is_empty() {
            let mut next_stubs: Vec<MoreComments> = Vec::new();

            for stub in &pending_stubs {
                if stub.children.is_empty() {
                    // "Continue this thread" stub. Fetch the deep thread by requesting the parent
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

        let children_values = parser::children_to_values(comments_listing.data.children);

        let mut comments = Vec::new();
        let mut more_stubs = Vec::new();
        parser::collect_comments(&children_values, &mut comments, &mut more_stubs)?;

        Ok((comments, more_stubs))
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

        // Expects segments that look like this: ["r", "subreddit", "comments", "id", ...].
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
