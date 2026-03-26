//! File discovery, type detection, and data parsing for scraped Reddit data.
//!
//! This module handles scanning the scrapes directory, detecting file types, and parsing
//! JSON/JSONL/CSV data into structured types for rendering.

use std::path::Path;

use serde::Deserialize;
use urs_core::models::{
    Comment, CommentsResult, RedditorInteractions, Submission, Subreddit, SubredditRules,
};

/// A file or directory entry in the scrapes tree.
#[derive(Debug, Clone)]
pub struct FileEntry {
    /// Children entries (for pre-loaded directories; unused with lazy HTMX loading).
    #[allow(dead_code)]
    pub children: Vec<Self>,
    /// Whether this is a directory.
    pub is_dir: bool,
    /// Display name (filename or directory name).
    pub name: String,
    /// Relative path from the scrapes root.
    pub relative_path: String,
    /// File size in bytes (0 for directories).
    pub size: u64,
}

/// A single livestream event.
#[derive(Debug, Clone, serde::Serialize, Deserialize)]
pub struct LivestreamEvent {
    /// The event data (raw JSON).
    pub data: serde_json::Value,
    /// Event type ("comment" or "submission").
    #[serde(rename = "type")]
    pub event_type: String,
}

/// Parsed scrape data ready for rendering.
#[derive(Debug)]
#[allow(dead_code)]
pub enum ScrapeData {
    /// Comment thread (nested with replies).
    Comments {
        /// Top-level comments with nested replies.
        comments: Vec<Comment>,
        /// Whether this is raw (flat) format.
        is_raw: bool,
        /// The parent submission's metadata.
        submission: Box<Submission>,
    },
    /// CSV data.
    Csv {
        /// Column headers.
        headers: Vec<String>,
        /// Row data.
        rows: Vec<Vec<String>>,
    },
    /// Livestream events.
    Livestream(Vec<LivestreamEvent>),
    /// Redditor profile with interaction categories.
    Redditor(Box<RedditorInteractions>),
    /// Subreddit submissions with metadata and optional rules.
    Submissions {
        /// Subreddit metadata from the about endpoint.
        information: Box<Subreddit>,
        /// The list of submissions.
        posts: Vec<Submission>,
        /// Optional Subreddit rules.
        rules: Option<SubredditRules>,
    },
}

/// The type of scraped data in a file.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ScrapeType {
    /// Submission comments (nested or flat).
    Comments,
    /// CSV export.
    Csv,
    /// Livestream events (JSONL).
    Livestream,
    /// Redditor profile and interactions.
    Redditor,
    /// Subreddit posts (submissions).
    Subreddit,
}

/// Helper struct for deserializing the Subreddit JSON shape.
#[derive(Deserialize)]
struct SubredditWithInfo {
    /// Subreddit metadata from the about endpoint.
    information: Subreddit,
    /// Optional Subreddit rules.
    rules: Option<SubredditRules>,
    /// The list of submissions.
    #[serde(default)]
    submissions: Vec<Submission>,
}

/// Scans a directory and returns its immediate children as `FileEntry` items.
///
/// Directories are listed first (sorted alphabetically), then files (sorted alphabetically).
/// Date directories (YYYY-MM-DD) are sorted newest-first.
///
/// # Errors
///
/// Returns an error if the directory cannot be read.
pub fn scan_directory(scrapes_root: &Path, relative_path: &str) -> anyhow::Result<Vec<FileEntry>> {
    let full_path = if relative_path.is_empty() {
        scrapes_root.to_path_buf()
    } else {
        scrapes_root.join(relative_path)
    };

    tracing::debug!(path = %full_path.display(), "Scanning directory");

    let mut dirs = Vec::new();
    let mut files = Vec::new();

    for entry in std::fs::read_dir(&full_path)? {
        let entry = entry?;
        let metadata = entry.metadata()?;
        let name = entry.file_name().to_string_lossy().to_string();

        // Skip hidden files.
        if name.starts_with('.') {
            continue;
        }

        let child_relative = if relative_path.is_empty() {
            name.clone()
        } else {
            format!("{relative_path}/{name}")
        };

        let file_entry = FileEntry {
            children: Vec::new(),
            is_dir: metadata.is_dir(),
            name,
            relative_path: child_relative,
            size: if metadata.is_file() {
                metadata.len()
            } else {
                0
            },
        };

        if metadata.is_dir() {
            dirs.push(file_entry);
        } else {
            files.push(file_entry);
        }
    }

    // Sort date directories newest-first, others alphabetically.
    dirs.sort_by(|a, b| {
        let a_is_date = is_date_dir(&a.name);
        let b_is_date = is_date_dir(&b.name);
        if a_is_date && b_is_date {
            b.name.cmp(&a.name) // Reverse for dates.
        } else {
            a.name.cmp(&b.name)
        }
    });

    files.sort_by(|a, b| a.name.cmp(&b.name));

    dirs.extend(files);

    tracing::debug!(
        path = %full_path.display(),
        count = dirs.len(),
        "Directory scan complete"
    );

    Ok(dirs)
}

/// Detects the scrape type of a file based on its path and parent directory.
///
/// Detection priority:
/// 1. `.csv` extension -> Csv
/// 2. `.jsonl` extension -> Livestream
/// 3. Parent directory name -> corresponding type
/// 4. JSON content inspection (fallback)
#[must_use]
pub fn detect_type(file_path: &Path) -> ScrapeType {
    let ext = file_path.extension().and_then(|e| e.to_str()).unwrap_or("");

    match ext {
        "csv" => {
            tracing::debug!(path = %file_path.display(), "Detected type by extension: Csv");
            return ScrapeType::Csv;
        }
        "jsonl" => {
            tracing::debug!(path = %file_path.display(), "Detected type by extension: Livestream");
            return ScrapeType::Livestream;
        }
        _ => {}
    }

    // Check parent directory name.
    if let Some(parent) = file_path.parent().and_then(|p| p.file_name()) {
        let result = match parent.to_str().unwrap_or("") {
            "subreddits" => Some(ScrapeType::Subreddit),
            "redditors" => Some(ScrapeType::Redditor),
            "comments" => Some(ScrapeType::Comments),
            "livestreams" => Some(ScrapeType::Livestream),
            _ => None,
        };

        if let Some(t) = result {
            tracing::debug!(path = %file_path.display(), scrape_type = ?t, "Detected type by parent directory");
            return t;
        }
    }

    // Fallback: inspect JSON content.
    tracing::debug!(path = %file_path.display(), "Falling back to content inspection for type detection");

    if let Ok(contents) = std::fs::read_to_string(file_path) {
        // Subreddit format has "submissions" key; check before Redditor "information" since the
        // Subreddit format also has an "information" section.
        if contents.contains("\"submissions\"") {
            tracing::debug!(path = %file_path.display(), "Detected type by content: Subreddit");
            return ScrapeType::Subreddit;
        }
        if contents.contains("\"information\"") {
            tracing::debug!(path = %file_path.display(), "Detected type by content: Redditor");
            return ScrapeType::Redditor;
        }
    }

    tracing::debug!(path = %file_path.display(), "Defaulting to Subreddit type");

    ScrapeType::Subreddit
}

/// Parses a scrape file into structured data.
///
/// # Errors
///
/// Returns an error if the file cannot be read or parsed.
pub fn parse_file(file_path: &Path, scrape_type: ScrapeType) -> anyhow::Result<ScrapeData> {
    tracing::debug!(
        path = %file_path.display(),
        scrape_type = ?scrape_type,
        "Parsing file"
    );

    let result = match scrape_type {
        ScrapeType::Comments => parse_comments(file_path),
        ScrapeType::Csv => parse_csv(file_path),
        ScrapeType::Livestream => parse_livestream(file_path),
        ScrapeType::Redditor => parse_redditor(file_path),
        ScrapeType::Subreddit => parse_subreddit(file_path),
    };

    if let Err(ref e) = result {
        tracing::error!(path = %file_path.display(), error = %e, "File parse failed");
    }

    result
}

/// Formats a file size in bytes to a human-readable string.
#[must_use]
#[allow(clippy::cast_precision_loss)]
pub fn format_size(bytes: u64) -> String {
    const KB: u64 = 1024;
    const MB: u64 = 1024 * KB;
    const GB: u64 = 1024 * MB;

    if bytes >= GB {
        format!("{:.1} GB", bytes as f64 / GB as f64)
    } else if bytes >= MB {
        format!("{:.1} MB", bytes as f64 / MB as f64)
    } else if bytes >= KB {
        format!("{:.1} KB", bytes as f64 / KB as f64)
    } else {
        format!("{bytes} B")
    }
}

/// Returns `true` if a directory name looks like a date (YYYY-MM-DD).
fn is_date_dir(name: &str) -> bool {
    name.len() == 10
        && name.as_bytes().get(4) == Some(&b'-')
        && name.as_bytes().get(7) == Some(&b'-')
        && name
            .chars()
            .filter(|c| *c != '-')
            .all(|c| c.is_ascii_digit())
}

/// Parses a comments JSON file.
fn parse_comments(file_path: &Path) -> anyhow::Result<ScrapeData> {
    let contents = std::fs::read_to_string(file_path)?;

    // Detect if raw (flat) format: raw comments have no nested replies.
    let is_raw = file_path
        .file_name()
        .and_then(|n| n.to_str())
        .is_some_and(|n| n.contains("-raw"));

    let result: CommentsResult = serde_json::from_str(&contents)?;

    tracing::debug!(
        count = result.comments.len(),
        is_raw = is_raw,
        "Parsed comments"
    );

    Ok(ScrapeData::Comments {
        comments: result.comments,
        is_raw,
        submission: Box::new(result.submission),
    })
}

/// Parses a CSV file.
fn parse_csv(file_path: &Path) -> anyhow::Result<ScrapeData> {
    let contents = std::fs::read_to_string(file_path)?;
    let mut reader = csv::ReaderBuilder::new().from_reader(contents.as_bytes());

    let headers: Vec<String> = reader.headers()?.iter().map(String::from).collect();

    let mut rows = Vec::new();
    for result in reader.records() {
        let record = result?;
        rows.push(record.iter().map(String::from).collect());
    }

    tracing::debug!(
        columns = headers.len(),
        rows = rows.len(),
        "Parsed CSV data"
    );

    Ok(ScrapeData::Csv { headers, rows })
}

/// Parses a JSONL livestream file.
fn parse_livestream(file_path: &Path) -> anyhow::Result<ScrapeData> {
    let contents = std::fs::read_to_string(file_path)?;
    let events: Vec<LivestreamEvent> = contents
        .lines()
        .filter(|line| !line.trim().is_empty())
        .map(serde_json::from_str)
        .collect::<Result<Vec<_>, _>>()?;

    tracing::debug!(count = events.len(), "Parsed livestream events");

    Ok(ScrapeData::Livestream(events))
}

/// Parses a Redditor JSON file.
fn parse_redditor(file_path: &Path) -> anyhow::Result<ScrapeData> {
    let contents = std::fs::read_to_string(file_path)?;
    let interactions: RedditorInteractions = serde_json::from_str(&contents)?;

    tracing::debug!(
        username = interactions
            .information
            .as_ref()
            .map_or("unknown", |i| &i.name),
        "Parsed Redditor profile"
    );

    Ok(ScrapeData::Redditor(Box::new(interactions)))
}

/// Parses a Subreddit JSON file.
fn parse_subreddit(file_path: &Path) -> anyhow::Result<ScrapeData> {
    let contents = std::fs::read_to_string(file_path)?;
    let data: SubredditWithInfo = serde_json::from_str(&contents)?;

    tracing::debug!(
        count = data.submissions.len(),
        has_rules = data.rules.is_some(),
        "Parsed Subreddit data"
    );

    Ok(ScrapeData::Submissions {
        information: Box::new(data.information),
        posts: data.submissions,
        rules: data.rules,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn detect_type_by_extension() {
        assert_eq!(detect_type(Path::new("data.csv")), ScrapeType::Csv);
        assert_eq!(
            detect_type(Path::new("stream.jsonl")),
            ScrapeType::Livestream
        );
    }

    #[test]
    fn detect_type_by_parent_dir() {
        assert_eq!(
            detect_type(Path::new("scrapes/2026-03-16/subreddits/rust.json")),
            ScrapeType::Subreddit
        );
        assert_eq!(
            detect_type(Path::new("scrapes/2026-03-16/redditors/spez.json")),
            ScrapeType::Redditor
        );
        assert_eq!(
            detect_type(Path::new("scrapes/2026-03-16/comments/post.json")),
            ScrapeType::Comments
        );
        assert_eq!(
            detect_type(Path::new("scrapes/2026-03-16/livestreams/data.json")),
            ScrapeType::Livestream
        );
    }

    #[test]
    fn format_size_bytes() {
        assert_eq!(format_size(0), "0 B");
        assert_eq!(format_size(500), "500 B");
    }

    #[test]
    fn format_size_kilobytes() {
        assert_eq!(format_size(1024), "1.0 KB");
        assert_eq!(format_size(12_700), "12.4 KB");
    }

    #[test]
    fn format_size_megabytes() {
        assert_eq!(format_size(1_048_576), "1.0 MB");
        assert_eq!(format_size(4_500_000), "4.3 MB");
    }

    #[test]
    fn is_date_dir_invalid() {
        assert!(!is_date_dir("subreddits"));
        assert!(!is_date_dir("2026-3-16"));
        assert!(!is_date_dir(""));
    }

    #[test]
    fn is_date_dir_valid() {
        assert!(is_date_dir("2026-03-16"));
        assert!(is_date_dir("2024-01-01"));
    }
}
