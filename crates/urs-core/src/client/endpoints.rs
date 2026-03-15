//! Reddit API endpoint builders.
//!
//! This module provides type-safe builders for Reddit API endpoints, ensuring correct URL
//! construction and query parameter handling. All endpoints use the OAuth base URL
//! (`https://oauth.reddit.com`)

use url::Url;

/// The base URL for the Reddit OAuth API.
pub const OAUTH_BASE: &str = "https://oauth.reddit.com";

/// Time filter options for Reddit listings.
///
/// Used with "top" and "controversial" sorting to filter by time period.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub enum TimeFilter {
    /// All time.
    #[default]
    All,
    /// Past hour.
    Hour,
    /// Past 24 hours.
    Day,
    /// Past week.
    Week,
    /// Past month.
    Month,
    /// Past year.
    Year,
}

impl TimeFilter {
    /// Returns the API parameter value for this time filter.
    #[must_use]
    pub const fn as_str(&self) -> &'static str {
        match self {
            Self::All => "all",
            Self::Hour => "hour",
            Self::Day => "day",
            Self::Week => "week",
            Self::Month => "month",
            Self::Year => "year",
        }
    }
}

impl std::fmt::Display for TimeFilter {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// Sorting options for Subreddit listings.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub enum SubredditSort {
    /// Hot posts (default Reddit view).
    #[default]
    Hot,
    /// New posts by submission time.
    New,
    /// Top posts (requires time filter).
    Top,
    /// Controversial posts (requires time filter).
    Controversial,
    /// Rising posts.
    Rising,
}

impl SubredditSort {
    /// Returns the API path component for this sort option.
    #[must_use]
    pub const fn as_str(&self) -> &'static str {
        match self {
            Self::Hot => "hot",
            Self::New => "new",
            Self::Top => "top",
            Self::Controversial => "controversial",
            Self::Rising => "rising",
        }
    }

    /// Returns `true` if this sort requires a time filter.
    #[must_use]
    pub const fn requires_time_filter(&self) -> bool {
        matches!(self, Self::Top | Self::Controversial)
    }
}

impl std::fmt::Display for SubredditSort {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

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

/// Builds URLs for redditor (user) endpoints.
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

    /// Builds a URL for fetching a user's overview (submissions + comments).
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username
    /// * `limit` - Maximum number of items to return
    /// * `after` - Pagination cursor for the next page
    ///
    /// # Panics
    ///
    /// Panics if the hardcoded base URL is invalid (should never happen).
    #[must_use]
    pub fn overview(username: &str, limit: u32, after: Option<&str>) -> Url {
        Self::user_listing(username, "overview", limit, after)
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
    fn time_filter_as_str() {
        assert_eq!(TimeFilter::All.as_str(), "all");
        assert_eq!(TimeFilter::Hour.as_str(), "hour");
        assert_eq!(TimeFilter::Day.as_str(), "day");
        assert_eq!(TimeFilter::Week.as_str(), "week");
        assert_eq!(TimeFilter::Month.as_str(), "month");
        assert_eq!(TimeFilter::Year.as_str(), "year");
    }

    #[test]
    fn subreddit_sort_requires_time_filter() {
        assert!(!SubredditSort::Hot.requires_time_filter());
        assert!(!SubredditSort::New.requires_time_filter());
        assert!(SubredditSort::Top.requires_time_filter());
        assert!(SubredditSort::Controversial.requires_time_filter());
        assert!(!SubredditSort::Rising.requires_time_filter());
    }

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
