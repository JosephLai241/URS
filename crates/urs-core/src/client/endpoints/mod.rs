//! Reddit API endpoint builders.
//!
//! This module provides type-safe builders for Reddit API endpoints, ensuring correct URL
//! construction and query parameter handling. All endpoints use the OAuth base URL
//! (`https://oauth.reddit.com`)

mod comments;
mod livestream;
mod redditor;
mod subreddit;

pub use comments::CommentsEndpoint;
pub use livestream::LivestreamEndpoint;
pub use redditor::RedditorEndpoint;
pub use subreddit::SubredditEndpoint;

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
}
