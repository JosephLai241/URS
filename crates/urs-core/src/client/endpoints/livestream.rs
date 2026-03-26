//! Livestream polling endpoint URL builders.
//!
//! These endpoints support the `before` parameter for cursor-based polling, returning only items
//! newer than the given fullname.

use url::Url;

use super::OAUTH_BASE;

/// Builds URLs for livestream polling endpoints.
///
/// These endpoints support the `before` parameter for cursor-based polling, returning only items
/// newer than the given fullname.
#[derive(Debug)]
pub struct LivestreamEndpoint;

impl LivestreamEndpoint {
    /// Builds a URL for polling new submissions in a Subreddit.
    ///
    /// Uses `/r/{subreddit}/new` sorted by newest first. The `before` parameter acts as a cursor:
    /// only items newer than the given fullname are returned.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `before` - Fullname cursor (e.g. `t3_abc123`) to fetch only newer items
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn subreddit_submissions(subreddit: &str, before: Option<&str>) -> Url {
        let path = format!("/r/{subreddit}/new");
        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);

        let mut query = url.query_pairs_mut();
        query.append_pair("limit", "100");
        query.append_pair("raw_json", "1");

        if let Some(before) = before {
            query.append_pair("before", before);
        }

        drop(query);

        url
    }

    /// Builds a URL for polling new comments in a Subreddit.
    ///
    /// Uses `/r/{subreddit}/comments` which returns a flat listing of the most recent comments
    /// across all submissions. The `before` parameter acts as a cursor.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `before` - Fullname cursor (e.g. `t1_abc123`) to fetch only newer items
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn subreddit_comments(subreddit: &str, before: Option<&str>) -> Url {
        let path = format!("/r/{subreddit}/comments");
        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);

        let mut query = url.query_pairs_mut();
        query.append_pair("limit", "100");
        query.append_pair("raw_json", "1");

        if let Some(before) = before {
            query.append_pair("before", before);
        }

        drop(query);

        url
    }

    /// Builds a URL for polling new submissions by a Redditor.
    ///
    /// Uses `/user/{username}/submitted` sorted by new. The `before` parameter acts as a cursor.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username (without u/ prefix)
    /// * `before` - Fullname cursor (e.g. `t3_abc123`) to fetch only newer items
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn redditor_submissions(username: &str, before: Option<&str>) -> Url {
        let path = format!("/user/{username}/submitted");
        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);

        let mut query = url.query_pairs_mut();
        query.append_pair("sort", "new");
        query.append_pair("limit", "100");
        query.append_pair("raw_json", "1");

        if let Some(before) = before {
            query.append_pair("before", before);
        }

        drop(query);

        url
    }

    /// Builds a URL for polling new comments by a Redditor.
    ///
    /// Uses `/user/{username}/comments` sorted by new. The `before` parameter acts as a cursor.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username (without u/ prefix)
    /// * `before` - Fullname cursor (e.g. `t1_abc123`) to fetch only newer items
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn redditor_comments(username: &str, before: Option<&str>) -> Url {
        let path = format!("/user/{username}/comments");
        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);

        let mut query = url.query_pairs_mut();
        query.append_pair("sort", "new");
        query.append_pair("limit", "100");
        query.append_pair("raw_json", "1");

        if let Some(before) = before {
            query.append_pair("before", before);
        }

        drop(query);

        url
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn livestream_subreddit_submissions_no_cursor() {
        let url = LivestreamEndpoint::subreddit_submissions("rust", None);

        assert_eq!(url.path(), "/r/rust/new");
        assert_eq!(url.host_str(), Some("oauth.reddit.com"));

        let query = url.query().unwrap();

        assert!(query.contains("limit=100"));
        assert!(!query.contains("before"));
    }

    #[test]
    fn livestream_subreddit_submissions_with_cursor() {
        let url = LivestreamEndpoint::subreddit_submissions("rust", Some("t3_abc123"));

        let query = url.query().unwrap();

        assert!(query.contains("before=t3_abc123"));
    }

    #[test]
    fn livestream_subreddit_comments_no_cursor() {
        let url = LivestreamEndpoint::subreddit_comments("rust", None);

        assert_eq!(url.path(), "/r/rust/comments");

        let query = url.query().unwrap();

        assert!(query.contains("limit=100"));
        assert!(!query.contains("before"));
    }

    #[test]
    fn livestream_subreddit_comments_with_cursor() {
        let url = LivestreamEndpoint::subreddit_comments("rust", Some("t1_xyz"));

        assert!(url.query().unwrap().contains("before=t1_xyz"));
    }

    #[test]
    fn livestream_redditor_submissions() {
        let url = LivestreamEndpoint::redditor_submissions("spez", None);

        assert_eq!(url.path(), "/user/spez/submitted");

        let query = url.query().unwrap();

        assert!(query.contains("sort=new"));
        assert!(query.contains("limit=100"));
    }

    #[test]
    fn livestream_redditor_submissions_with_cursor() {
        let url = LivestreamEndpoint::redditor_submissions("spez", Some("t3_abc"));

        assert!(url.query().unwrap().contains("before=t3_abc"));
    }

    #[test]
    fn livestream_redditor_comments() {
        let url = LivestreamEndpoint::redditor_comments("spez", None);

        assert_eq!(url.path(), "/user/spez/comments");

        let query = url.query().unwrap();

        assert!(query.contains("sort=new"));
        assert!(query.contains("limit=100"));
    }

    #[test]
    fn livestream_redditor_comments_with_cursor() {
        let url = LivestreamEndpoint::redditor_comments("spez", Some("t1_def"));

        assert!(url.query().unwrap().contains("before=t1_def"));
    }
}
