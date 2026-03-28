//! Shared types and utility functions for scrape handlers.
//!
//! Provides parameter structs for each scrape type, task update helpers for the shared `DashMap`,
//! and small utility functions used across the scrape module.

use std::time::{Instant, SystemTime, UNIX_EPOCH};

use dashmap::DashMap;
use serde::Deserialize;
use urs_core::client::endpoints::TimeFilter;

use super::super::server::ScrapeTask;

/// Output shape for Subreddit scrape JSON export.
#[derive(serde::Serialize)]
pub struct SubredditOutput {
    pub information: urs_core::models::Subreddit,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rules: Option<urs_core::models::SubredditRules>,
    pub submissions: Vec<urs_core::models::Submission>,
}

/// Form parameters for Subreddit scrape.
#[derive(Debug, Deserialize)]
pub struct SubredditScrapeParams {
    /// Category: hot, new, top, controversial, rising, search.
    pub category: String,
    /// Number of posts to scrape.
    pub count: Option<usize>,
    /// Export format: json or csv.
    pub format: Option<String>,
    /// Search query (required for search category).
    pub query: Option<String>,
    /// Include Subreddit rules.
    pub rules: Option<String>,
    /// Subreddit name (without r/ prefix).
    pub subreddit: String,
    /// Time filter for top/controversial.
    pub time: Option<String>,
}

/// Form parameters for comments scrape.
#[derive(Debug, Deserialize)]
pub struct CommentsScrapeParams {
    /// Number of comments (0 = all).
    pub count: Option<usize>,
    /// Whether to output as flat list.
    pub raw: Option<String>,
    /// Full Reddit submission URL.
    pub url: String,
}

/// Form parameters for Redditor scrape.
#[derive(Debug, Deserialize)]
pub struct RedditorScrapeParams {
    /// Number of items per category.
    pub count: Option<usize>,
    /// Reddit username (without u/ prefix).
    pub username: String,
}

/// Updates a task's stage in the shared map.
pub fn update_task(
    tasks: &DashMap<String, ScrapeTask>,
    id: &str,
    stage: &str,
    detail: &str,
    index: u8,
) {
    if let Some(mut task) = tasks.get_mut(id) {
        task.stage = stage.to_string();
        task.detail = detail.to_string();
        task.stage_index = index;
    }
}

/// Marks a task as complete with its result path.
pub fn complete_task(tasks: &DashMap<String, ScrapeTask>, id: &str, result_path: &str) {
    if let Some(mut task) = tasks.get_mut(id) {
        task.stage = "complete".to_string();
        task.detail = "Complete!".to_string();
        task.stage_index = task.stage_total - 1;
        task.result_path = Some(result_path.to_string());
        task.finished_at = Some(Instant::now());
    }
}

/// Marks a task as failed with an error message.
pub fn fail_task(tasks: &DashMap<String, ScrapeTask>, id: &str, message: &str) {
    if let Some(mut task) = tasks.get_mut(id) {
        task.stage = "error".to_string();
        task.detail = "Error".to_string();
        task.error = Some(message.to_string());
        task.finished_at = Some(Instant::now());
    }
}

/// Returns the current time as a Unix timestamp in seconds.
pub fn now_unix() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}

/// Converts a time filter string to the core `TimeFilter` enum.
pub fn parse_time_filter(s: &str) -> TimeFilter {
    match s {
        "hour" => TimeFilter::Hour,
        "day" => TimeFilter::Day,
        "week" => TimeFilter::Week,
        "month" => TimeFilter::Month,
        "year" => TimeFilter::Year,
        _ => TimeFilter::All,
    }
}

/// Extracts a title slug from a Reddit submission URL.
pub fn extract_title_from_url(url: &str) -> String {
    url.trim_end_matches('/')
        .split('/')
        .nth(7)
        .unwrap_or("submission")
        .to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_time_filter_valid() {
        assert_eq!(parse_time_filter("hour"), TimeFilter::Hour);
        assert_eq!(parse_time_filter("day"), TimeFilter::Day);
        assert_eq!(parse_time_filter("week"), TimeFilter::Week);
        assert_eq!(parse_time_filter("month"), TimeFilter::Month);
        assert_eq!(parse_time_filter("year"), TimeFilter::Year);
        assert_eq!(parse_time_filter("all"), TimeFilter::All);
    }

    #[test]
    fn parse_time_filter_unknown_defaults_to_all() {
        assert_eq!(parse_time_filter("unknown"), TimeFilter::All);
        assert_eq!(parse_time_filter(""), TimeFilter::All);
    }

    #[test]
    fn extract_title_standard_url() {
        let url = "https://www.reddit.com/r/rust/comments/abc123/my_cool_post/";
        assert_eq!(extract_title_from_url(url), "my_cool_post");
    }

    #[test]
    fn extract_title_fallback() {
        let url = "https://reddit.com/short";
        assert_eq!(extract_title_from_url(url), "submission");
    }

    #[test]
    fn task_update_helpers_work() {
        let tasks = DashMap::new();
        let id = "test-id";

        tasks.insert(
            id.to_string(),
            ScrapeTask {
                detail: "Starting...".to_string(),
                error: None,
                finished_at: None,
                id: id.to_string(),
                result_path: None,
                stage: "validating".to_string(),
                stage_index: 0,
                stage_total: 4,
                started_at: 0.0,
                task_type: "batch".to_string(),
                title: "Test task".to_string(),
            },
        );

        update_task(&tasks, id, "fetching", "Fetching...", 1);

        let task = tasks.get(id).unwrap();

        assert_eq!(task.stage, "fetching");
        assert_eq!(task.detail, "Fetching...");
        assert_eq!(task.stage_index, 1);

        drop(task);

        complete_task(&tasks, id, "some/path.json");

        let task = tasks.get(id).unwrap();

        assert_eq!(task.stage, "complete");
        assert_eq!(task.result_path.as_deref(), Some("some/path.json"));
        assert!(task.finished_at.is_some());

        drop(task);
    }

    #[test]
    fn fail_task_sets_error() {
        let tasks = DashMap::new();
        let id = "fail-id";

        tasks.insert(
            id.to_string(),
            ScrapeTask {
                detail: "Starting...".to_string(),
                error: None,
                finished_at: None,
                id: id.to_string(),
                result_path: None,
                stage: "validating".to_string(),
                stage_index: 0,
                stage_total: 4,
                started_at: 0.0,
                task_type: "batch".to_string(),
                title: "Test task".to_string(),
            },
        );

        fail_task(&tasks, id, "Something went wrong");

        let task = tasks.get(id).unwrap();

        assert_eq!(task.stage, "error");
        assert_eq!(task.error.as_deref(), Some("Something went wrong"));
        assert!(task.finished_at.is_some());

        drop(task);
    }
}
