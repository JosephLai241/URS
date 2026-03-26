//! Submission comment endpoint URL builders.

use url::Url;

use super::OAUTH_BASE;

/// Builds URLs for submission comment endpoints.
#[derive(Debug)]
pub struct CommentsEndpoint;

impl CommentsEndpoint {
    /// Builds a URL for fetching comments on a submission.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name
    /// * `submission_id` - The submission ID (without `t3_` prefix)
    /// * `limit` - Maximum number of top-level comments
    /// * `depth` - Maximum comment tree depth (None for unlimited)
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn submission(
        subreddit: &str,
        submission_id: &str,
        limit: Option<u32>,
        depth: Option<u32>,
    ) -> Url {
        let path = format!("/r/{subreddit}/comments/{submission_id}");
        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);

        let mut query = url.query_pairs_mut();
        query.append_pair("raw_json", "1");

        if let Some(limit) = limit {
            query.append_pair("limit", &limit.to_string());
        }

        if let Some(depth) = depth {
            query.append_pair("depth", &depth.to_string());
        }

        drop(query);

        url
    }

    /// Builds a URL for the `morechildren` endpoint.
    ///
    /// This expands "more comments" placeholders returned by the comments API.
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn more_children() -> Url {
        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path("/api/morechildren");

        url
    }

    /// Builds a URL for fetching a specific comment thread.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name
    /// * `submission_id` - The submission ID (without `t3_` prefix)
    /// * `comment_id` - The comment ID (without `t1_` prefix)
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn comment_thread(subreddit: &str, submission_id: &str, comment_id: &str) -> Url {
        let path = format!("/r/{subreddit}/comments/{submission_id}/comment/{comment_id}");

        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);
        url.query_pairs_mut().append_pair("raw_json", "1");

        url
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn comments_endpoint_submission() {
        let url = CommentsEndpoint::submission("rust", "abc123", Some(100), Some(5));

        assert_eq!(url.path(), "/r/rust/comments/abc123");
        assert_eq!(url.host_str(), Some("oauth.reddit.com"));

        let query = url.query().unwrap();

        assert!(query.contains("limit=100"));
        assert!(query.contains("depth=5"));
    }

    #[test]
    fn comments_endpoint_more_children() {
        let url = CommentsEndpoint::more_children();

        assert_eq!(url.path(), "/api/morechildren");
        assert_eq!(url.host_str(), Some("oauth.reddit.com"));
    }

    #[test]
    fn comments_endpoint_comment_thread() {
        let url = CommentsEndpoint::comment_thread("rust", "abc123", "def456");
        assert_eq!(url.path(), "/r/rust/comments/abc123/comment/def456");
    }
}
