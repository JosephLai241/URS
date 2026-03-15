//! Export functionality for scraped data.
//!
//! This module provides utilities for exporting scraped Reddit data to JSON and CSV.

mod csv;
mod json;

pub use csv::CsvExporter;
pub use json::JsonExporter;

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use chrono::Local;

/// The base directory for scraped data.
const SCRAPES_DIR: &str = "scrapes";

/// Generates the output directory path for scraped data.
///
/// Format: `scrapes/{YYYY-MM-DD}/{type}/`
///
/// # Arguments
///
/// * `scrape_type` - The type of scrape (e.g., "subreddits", "redditors", "comments")
#[must_use]
pub fn output_dir(scrape_type: &str) -> PathBuf {
    let today = Local::now().format("%Y-%m-%d").to_string();
    PathBuf::from(SCRAPES_DIR).join(today).join(scrape_type)
}

/// Generates a filename for Subreddit scrape output.
///
/// Format: `{sub}-{category}-{n}-results[-past-{time}][-rules]`
///
/// # Arguments
///
/// * `subreddit` - The Subreddit name
/// * `category` - The sort category (hot, new, top, etc.)
/// * `count` - Number of results
/// * `time` - Optional time filter
/// * `include_rules` - Whether rules were included
#[must_use]
pub fn subreddit_filename(
    subreddit: &str,
    category: &str,
    count: usize,
    time: Option<&str>,
    include_rules: bool,
) -> String {
    let mut name = format!("{subreddit}-{category}-{count}-results");

    if let Some(t) = time {
        write!(name, "-past-{t}").expect("writing to String should never fail");
    }
    if include_rules {
        name.push_str("-rules");
    }

    name
}

/// Generates a filename for Redditor scrape output.
///
/// Format: `{username}-{n}-results`
///
/// # Arguments
///
/// * `username` - The Reddit username
/// * `count` - Number of results
#[must_use]
pub fn redditor_filename(username: &str, count: usize) -> String {
    format!("{username}-{count}-results")
}

/// Generates a filename for comments scrape output.
///
/// Format: `{title}-{n}-results[-all][-raw]`
///
/// # Arguments
///
/// * `title` - The submission title (sanitized)
/// * `count` - Number of comments
/// * `all_comments` - Whether all comments were fetched
/// * `raw` - Whether the output is raw (flat) or structured (tree)
#[must_use]
pub fn comments_filename(title: &str, count: usize, all_comments: bool, raw: bool) -> String {
    let sanitized_title = sanitize_filename(title, 50);
    let mut name = format!("{sanitized_title}-{count}-results");

    if all_comments {
        name.push_str("-all");
    }
    if raw {
        name.push_str("-raw");
    }

    name
}

/// Generates a filename for livestream output.
///
/// Format: `{target}-{source}-{count}-livestream`
///
/// # Arguments
///
/// * `target` - The target name (Subreddit or username)
/// * `source` - The source type ("comments" or "submissions")
/// * `count` - Number of items captured
#[must_use]
pub fn livestream_filename(target: &str, source: &str, count: usize) -> String {
    format!("{target}-{source}-{count}-livestream")
}

/// Sanitizes a string for use as a filename.
///
/// Removes invalid characters and truncates to the specified length.
fn sanitize_filename(s: &str, max_len: usize) -> String {
    let sanitized: String = s
        .chars()
        .filter(|c| c.is_alphanumeric() || *c == '-' || *c == '_' || *c == ' ')
        .take(max_len)
        .collect();

    sanitized.trim().replace(' ', "_").to_lowercase()
}

/// Ensures a directory exists, creating it if necessary.
///
/// # Arguments
///
/// * `path` - The directory path to create
///
/// # Errors
///
/// Returns an error if the directory cannot be created.
pub fn ensure_dir(path: &Path) -> std::io::Result<()> {
    if !path.exists() {
        std::fs::create_dir_all(path)?;
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sanitize_filename_basic() {
        assert_eq!(sanitize_filename("Hello World", 50), "hello_world");
    }

    #[test]
    fn sanitize_filename_special_chars() {
        assert_eq!(
            sanitize_filename("Test: <file> with /special\\ chars!", 50),
            "test_file_with_special_chars"
        );
    }

    #[test]
    fn sanitize_filename_truncate() {
        let long_title = "a".repeat(100);
        assert_eq!(sanitize_filename(&long_title, 50).len(), 50);
    }

    #[test]
    fn subreddit_filename_basic() {
        let name = subreddit_filename("rust", "hot", 100, None, false);
        assert_eq!(name, "rust-hot-100-results");
    }

    #[test]
    fn subreddit_filename_with_time() {
        let name = subreddit_filename("rust", "top", 50, Some("week"), false);
        assert_eq!(name, "rust-top-50-results-past-week");
    }

    #[test]
    fn subreddit_filename_with_rules() {
        let name = subreddit_filename("rust", "hot", 25, None, true);
        assert_eq!(name, "rust-hot-25-results-rules");
    }

    #[test]
    fn redditor_filename_basic() {
        let name = redditor_filename("spez", 15);
        assert_eq!(name, "spez-15-results");
    }

    #[test]
    fn comments_filename_basic() {
        let name = comments_filename("Test Post", 100, false, false);
        assert_eq!(name, "test_post-100-results");
    }

    #[test]
    fn comments_filename_all_raw() {
        let name = comments_filename("Test", 50, true, true);
        assert_eq!(name, "test-50-results-all-raw");
    }

    #[test]
    fn livestream_filename_basic() {
        let name = livestream_filename("rust", "comments", 42);
        assert_eq!(name, "rust-comments-42-livestream");
    }

    #[test]
    fn livestream_filename_submissions() {
        let name = livestream_filename("spez", "submissions", 100);
        assert_eq!(name, "spez-submissions-100-livestream");
    }
}
