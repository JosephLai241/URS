//! Redditor endpoint URL builders.

use url::Url;

use super::OAUTH_BASE;

/// Builds URLs for Redditor endpoints.
#[derive(Debug)]
pub struct RedditorEndpoint;

impl RedditorEndpoint {
    /// Builds a URL for fetching user profile information.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username (without u/ prefix)
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn about(username: &str) -> Url {
        let path = format!("/user/{username}/about");

        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);
        url.query_pairs_mut().append_pair("raw_json", "1");

        url
    }

    /// Builds a URL for fetching a user's submissions.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username
    /// * `limit` - Maximum number of submissions to return
    /// * `after` - Pagination cursor for the next page
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn submitted(username: &str, limit: u32, after: Option<&str>) -> Url {
        Self::user_listing(username, "submitted", limit, after)
    }

    /// Builds a URL for fetching a user's comments.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username
    /// * `limit` - Maximum number of comments to return
    /// * `after` - Pagination cursor for the next page
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn comments(username: &str, limit: u32, after: Option<&str>) -> Url {
        Self::user_listing(username, "comments", limit, after)
    }

    /// Builds a URL for fetching a private user category.
    ///
    /// These categories (downvoted, upvoted, saved, hidden, gilded/given) are only accessible for
    /// the authenticated user.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username
    /// * `category` - The interaction category name
    /// * `limit` - Maximum number of items to return
    /// * `after` - Pagination cursor for the next page
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn private_category(
        username: &str,
        category: &str,
        limit: u32,
        after: Option<&str>,
    ) -> Url {
        Self::user_listing(username, category, limit, after)
    }

    /// Builds a URL for fetching Subreddits moderated by a user.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn moderated_subreddits(username: &str) -> Url {
        let path = format!("/user/{username}/moderated_subreddits");

        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);
        url.query_pairs_mut().append_pair("raw_json", "1");

        url
    }

    /// Builds a URL for fetching a user's multireddits.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn multireddits(username: &str) -> Url {
        let path = format!("/api/multi/user/{username}");

        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);
        url.query_pairs_mut().append_pair("raw_json", "1");

        url
    }

    /// Internal helper for building user listing URLs.
    fn user_listing(username: &str, listing_type: &str, limit: u32, after: Option<&str>) -> Url {
        let path = format!("/user/{username}/{listing_type}");
        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);

        let mut query = url.query_pairs_mut();
        query.append_pair("limit", &limit.to_string());
        query.append_pair("raw_json", "1");

        if let Some(after) = after {
            query.append_pair("after", after);
        }

        drop(query);

        url
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn redditor_endpoint_about() {
        let url = RedditorEndpoint::about("spez");

        assert_eq!(url.path(), "/user/spez/about");
        assert_eq!(url.host_str(), Some("oauth.reddit.com"));
    }

    #[test]
    fn redditor_endpoint_submitted() {
        let url = RedditorEndpoint::submitted("spez", 25, None);

        assert_eq!(url.path(), "/user/spez/submitted");
        assert!(url.query().unwrap().contains("limit=25"));
    }

    #[test]
    fn redditor_endpoint_comments() {
        let url = RedditorEndpoint::comments("spez", 50, Some("t1_abc123"));

        assert_eq!(url.path(), "/user/spez/comments");
        assert!(url.query().unwrap().contains("after=t1_abc123"));
    }

    #[test]
    fn redditor_endpoint_private_category() {
        let url = RedditorEndpoint::private_category("spez", "downvoted", 100, None);

        assert_eq!(url.path(), "/user/spez/downvoted");
        assert!(url.query().unwrap().contains("limit=100"));
    }

    #[test]
    fn redditor_endpoint_moderated_subreddits() {
        let url = RedditorEndpoint::moderated_subreddits("spez");

        assert_eq!(url.path(), "/user/spez/moderated_subreddits");
        assert_eq!(url.host_str(), Some("oauth.reddit.com"));
    }

    #[test]
    fn redditor_endpoint_multireddits() {
        let url = RedditorEndpoint::multireddits("spez");

        assert_eq!(url.path(), "/api/multi/user/spez");
        assert_eq!(url.host_str(), Some("oauth.reddit.com"));
    }

    #[test]
    fn redditor_endpoint_private_category_with_pagination() {
        let url = RedditorEndpoint::private_category("spez", "saved", 25, Some("t3_abc123"));

        assert_eq!(url.path(), "/user/spez/saved");
        assert!(url.query().unwrap().contains("after=t3_abc123"));
    }
}
