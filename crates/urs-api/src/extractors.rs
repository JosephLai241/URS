//! Query parameter extractors for API endpoints.
//!
//! These types are deserialized from URL query strings by Axum and provide validated, defaulted
//! values for common parameters like pagination limits, time filters, and search queries.

use serde::Deserialize;
use urs_core::client::endpoints::TimeFilter;

/// Maximum allowed value for the `limit` parameter.
const MAX_LIMIT: usize = 500;

/// Default value for the `limit` parameter.
const DEFAULT_LIMIT: usize = 25;

/// Pagination parameters for listing endpoints.
///
/// The `limit` is clamped to `1..=500` and defaults to `25`.
///
/// # Example Query String
///
/// `?limit=50`
#[derive(Debug, Deserialize)]
pub struct PaginationParams {
    /// Maximum number of items to return (1–500, default 25).
    limit: Option<usize>,
}

impl PaginationParams {
    /// Returns the clamped limit value.
    #[must_use]
    pub fn limit(&self) -> usize {
        self.limit.map_or(DEFAULT_LIMIT, |l| l.clamp(1, MAX_LIMIT))
    }
}

/// Parameters for endpoints that support both pagination and time filtering.
///
/// Used by `top` and `controversial` sort endpoints.
///
/// # Example Query String
///
/// `?limit=100&time=week`
#[derive(Debug, Deserialize)]
pub struct TimeFilterParams {
    /// Maximum number of items to return (1–500, default 25).
    limit: Option<usize>,
    /// Time filter for sorting (hour, day, week, month, year, all). Defaults to `all`.
    time: Option<String>,
}

impl TimeFilterParams {
    /// Returns the clamped limit value.
    #[must_use]
    pub fn limit(&self) -> usize {
        self.limit.map_or(DEFAULT_LIMIT, |l| l.clamp(1, MAX_LIMIT))
    }

    /// Parses the time string into a [`TimeFilter`], defaulting to `All`.
    #[must_use]
    pub fn time_filter(&self) -> TimeFilter {
        self.time
            .as_deref()
            .map(parse_time_filter)
            .unwrap_or_default()
    }
}

/// Parameters for the Subreddit search endpoint.
///
/// # Example Query String
///
/// `?q=rust+async&limit=50&time=month`
#[derive(Debug, Deserialize)]
pub struct SearchParams {
    /// Maximum number of items to return (1–500, default 25).
    limit: Option<usize>,
    /// The search query (required).
    pub q: Option<String>,
    /// Time filter for results (hour, day, week, month, year, all). Defaults to `all`.
    time: Option<String>,
}

impl SearchParams {
    /// Returns the clamped limit value.
    #[must_use]
    pub fn limit(&self) -> usize {
        self.limit.map_or(DEFAULT_LIMIT, |l| l.clamp(1, MAX_LIMIT))
    }

    /// Parses the time string into an optional [`TimeFilter`].
    #[must_use]
    pub fn time_filter(&self) -> Option<TimeFilter> {
        self.time.as_deref().map(parse_time_filter)
    }
}

/// Parameters for comment fetching endpoints.
///
/// # Example Query String
///
/// `?limit=200&structured=false`
#[derive(Debug, Deserialize)]
pub struct CommentsQueryParams {
    /// Maximum number of comments to return.
    limit: Option<usize>,
    /// Whether to return threaded tree structure (default `true`).
    structured: Option<bool>,
    /// Full submission URL (required for the URL-based endpoint).
    pub url: Option<String>,
}

impl CommentsQueryParams {
    /// Returns the limit, clamped if present.
    #[must_use]
    pub fn limit(&self) -> Option<usize> {
        self.limit.map(|l| l.clamp(1, MAX_LIMIT))
    }

    /// Whether to return structured (threaded) comments. Defaults to `true`.
    #[must_use]
    pub fn structured(&self) -> bool {
        self.structured.unwrap_or(true)
    }
}

/// Parameters for livestream SSE endpoints.
///
/// # Example Query String
///
/// `?source=submissions`
#[derive(Debug, Deserialize)]
pub struct LivestreamParams {
    /// Content source: `comments` (default) or `submissions`.
    source: Option<String>,
}

impl LivestreamParams {
    /// Parses the source string into a [`LivestreamSource`](urs_core::scrapers::LivestreamSource).
    #[must_use]
    pub fn source(&self) -> urs_core::scrapers::LivestreamSource {
        match self.source.as_deref() {
            Some("submissions") => urs_core::scrapers::LivestreamSource::Submissions,
            _ => urs_core::scrapers::LivestreamSource::Comments,
        }
    }
}

/// Parses a time filter string into a [`TimeFilter`].
///
/// Unrecognized values default to [`TimeFilter::All`].
fn parse_time_filter(s: &str) -> TimeFilter {
    match s.to_lowercase().as_str() {
        "hour" => TimeFilter::Hour,
        "day" => TimeFilter::Day,
        "week" => TimeFilter::Week,
        "month" => TimeFilter::Month,
        "year" => TimeFilter::Year,
        _ => TimeFilter::All,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pagination_defaults_to_25() {
        let params = PaginationParams { limit: None };

        assert_eq!(params.limit(), 25);
    }

    #[test]
    fn pagination_clamps_to_max() {
        let params = PaginationParams { limit: Some(1000) };

        assert_eq!(params.limit(), 500);
    }

    #[test]
    fn pagination_clamps_to_min() {
        let params = PaginationParams { limit: Some(0) };

        assert_eq!(params.limit(), 1);
    }

    #[test]
    fn time_filter_parsing() {
        assert!(matches!(parse_time_filter("hour"), TimeFilter::Hour));
        assert!(matches!(parse_time_filter("DAY"), TimeFilter::Day));
        assert!(matches!(parse_time_filter("Week"), TimeFilter::Week));
        assert!(matches!(parse_time_filter("month"), TimeFilter::Month));
        assert!(matches!(parse_time_filter("year"), TimeFilter::Year));
        assert!(matches!(parse_time_filter("all"), TimeFilter::All));
        assert!(matches!(parse_time_filter("invalid"), TimeFilter::All));
    }

    #[test]
    fn time_filter_params_defaults() {
        let params = TimeFilterParams {
            limit: None,
            time: None,
        };

        assert_eq!(params.limit(), 25);
        assert!(matches!(params.time_filter(), TimeFilter::All));
    }

    #[test]
    fn search_params_require_query() {
        let params = SearchParams {
            limit: None,
            q: None,
            time: None,
        };

        assert!(params.q.is_none());
    }

    #[test]
    fn comments_params_defaults() {
        let params = CommentsQueryParams {
            limit: None,
            structured: None,
            url: None,
        };

        assert!(params.limit().is_none());
        assert!(params.structured());
    }

    #[test]
    fn comments_structured_false() {
        let params = CommentsQueryParams {
            limit: Some(100),
            structured: Some(false),
            url: None,
        };

        assert_eq!(params.limit(), Some(100));
        assert!(!params.structured());
    }

    #[test]
    fn livestream_defaults_to_comments() {
        let params = LivestreamParams { source: None };

        assert!(matches!(
            params.source(),
            urs_core::scrapers::LivestreamSource::Comments
        ));
    }

    #[test]
    fn livestream_submissions() {
        let params = LivestreamParams {
            source: Some("submissions".to_string()),
        };

        assert!(matches!(
            params.source(),
            urs_core::scrapers::LivestreamSource::Submissions
        ));
    }
}
