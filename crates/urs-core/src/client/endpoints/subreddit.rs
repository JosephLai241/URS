//! Subreddit endpoint URL builders.

use url::Url;

use super::{OAUTH_BASE, SubredditSort, TimeFilter};

/// Builds URLs for Subreddit endpoints.
#[derive(Debug)]
pub struct SubredditEndpoint;

impl SubredditEndpoint {
    /// Builds a URL for fetching Subreddit posts.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `sort` - The sorting method
    /// * `time` - The time filter (only used for top/controversial)
    /// * `limit` - Maximum number of posts to return (1-100)
    /// * `after` - Pagination cursor for the next page
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn listing(
        subreddit: &str,
        sort: SubredditSort,
        time: Option<TimeFilter>,
        limit: u32,
        after: Option<&str>,
    ) -> Url {
        let path = format!("/r/{subreddit}/{}", sort.as_str());
        let mut url = Url::parse(OAUTH_BASE).expect("Base URL is valid");
        url.set_path(&path);

        let mut query = url.query_pairs_mut();
        query.append_pair("limit", &limit.to_string());
        query.append_pair("raw_json", "1");

        if sort.requires_time_filter() {
            let time = time.unwrap_or_default();
            query.append_pair("t", time.as_str());
        }

        if let Some(after) = after {
            query.append_pair("after", after);
        }

        drop(query);

        url
    }

    /// Builds a URL for searching a Subreddit.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `query` - The search query
    /// * `time` - The time filter
    /// * `limit` - Maximum number of posts to return (1-100)
    /// * `after` - Pagination cursor for the next page
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn search(
        subreddit: &str,
        query: &str,
        time: Option<TimeFilter>,
        limit: u32,
        after: Option<&str>,
    ) -> Url {
        let path = format!("/r/{subreddit}/search");
        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);

        let mut query_pairs = url.query_pairs_mut();
        query_pairs.append_pair("q", query);
        query_pairs.append_pair("restrict_sr", "1");
        query_pairs.append_pair("limit", &limit.to_string());
        query_pairs.append_pair("raw_json", "1");

        if let Some(time) = time {
            query_pairs.append_pair("t", time.as_str());
        }

        if let Some(after) = after {
            query_pairs.append_pair("after", after);
        }

        drop(query_pairs);

        url
    }

    /// Builds a URL for fetching Subreddit information.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn about(subreddit: &str) -> Url {
        let path = format!("/r/{subreddit}/about");

        let mut url = Url::parse(OAUTH_BASE).expect("base URL is valid");
        url.set_path(&path);
        url.query_pairs_mut().append_pair("raw_json", "1");

        url
    }

    /// Builds a URL for fetching Subreddit rules.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn rules(subreddit: &str) -> Url {
        let path = format!("/r/{subreddit}/about/rules");

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
    fn subreddit_endpoint_listing_hot() {
        let url = SubredditEndpoint::listing("rust", SubredditSort::Hot, None, 25, None);

        assert_eq!(url.host_str(), Some("oauth.reddit.com"));
        assert_eq!(url.path(), "/r/rust/hot");
        assert!(url.query().unwrap().contains("limit=25"));
    }

    #[test]
    fn subreddit_endpoint_listing_top_with_time() {
        let url = SubredditEndpoint::listing(
            "rust",
            SubredditSort::Top,
            Some(TimeFilter::Week),
            50,
            None,
        );

        let query = url.query().unwrap();

        assert!(query.contains("t=week"));
        assert!(query.contains("limit=50"));
    }

    #[test]
    fn subreddit_endpoint_listing_with_pagination() {
        let url =
            SubredditEndpoint::listing("rust", SubredditSort::New, None, 25, Some("t3_abc123"));

        assert!(url.query().unwrap().contains("after=t3_abc123"));
    }

    #[test]
    fn subreddit_endpoint_search() {
        let url =
            SubredditEndpoint::search("rust", "async await", Some(TimeFilter::Month), 25, None);

        let query = url.query().unwrap();

        assert!(query.contains("q=async+await"));
        assert!(query.contains("restrict_sr=1"));
        assert!(query.contains("t=month"));
    }

    #[test]
    fn subreddit_endpoint_about() {
        let url = SubredditEndpoint::about("rust");

        assert_eq!(url.path(), "/r/rust/about");
        assert_eq!(url.host_str(), Some("oauth.reddit.com"));
    }

    #[test]
    fn subreddit_endpoint_rules() {
        let url = SubredditEndpoint::rules("rust");

        assert_eq!(url.path(), "/r/rust/about/rules");
    }
}
