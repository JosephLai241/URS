//! This module provides utilities for exporting data to CSV format.

use std::fmt::Write as _;
use std::io::Write;
use std::path::Path;

use crate::error::Result;
use crate::models::{Comment, Submission};

/// Exporter for CSV format.
#[derive(Debug, Default)]
pub struct CsvExporter;

impl CsvExporter {
    /// Creates a new CSV exporter.
    #[must_use]
    pub const fn new() -> Self {
        Self
    }

    /// Exports submissions to a CSV file.
    ///
    /// # Arguments
    ///
    /// * `submissions` - The submissions to export
    /// * `path` - The output file path
    ///
    /// # Errors
    ///
    /// Returns an error if file writing fails.
    pub fn export_submissions(&self, submissions: &[Submission], path: &Path) -> Result<()> {
        let csv = self.submissions_to_csv(submissions);

        let mut file = std::fs::File::create(path)?;
        file.write_all(csv.as_bytes())?;

        Ok(())
    }

    /// Converts submissions to a CSV string.
    ///
    /// # Arguments
    ///
    /// * `submissions` - The submissions to convert
    #[must_use]
    pub fn submissions_to_csv(&self, submissions: &[Submission]) -> String {
        let mut csv = String::new();

        csv.push_str("author,created_utc,title,score,num_comments,url,subreddit,is_self,nsfw\n");

        for sub in submissions {
            writeln!(
                csv,
                "{},{},{},{},{},{},{},{},{}",
                escape_csv(&sub.author),
                sub.created_utc,
                escape_csv(&sub.title),
                sub.score,
                sub.num_comments,
                escape_csv(&sub.url),
                escape_csv(&sub.subreddit),
                sub.is_self,
                sub.nsfw,
            )
            .expect("writing to String should never fail");
        }

        csv
    }

    /// Exports comments to a CSV file.
    ///
    /// # Arguments
    ///
    /// * `comments` - The comments to export
    /// * `path` - The output file path
    ///
    /// # Errors
    ///
    /// Returns an error if file writing fails.
    pub fn export_comments(&self, comments: &[Comment], path: &Path) -> Result<()> {
        let csv = self.comments_to_csv(comments);

        let mut file = std::fs::File::create(path)?;
        file.write_all(csv.as_bytes())?;

        Ok(())
    }

    /// Converts comments to a CSV string.
    ///
    /// # Arguments
    ///
    /// * `comments` - The comments to convert
    #[must_use]
    pub fn comments_to_csv(&self, comments: &[Comment]) -> String {
        let mut csv = String::new();
        csv.push_str("author,created_utc,body,score,is_submitter,parent_id\n");

        Self::flatten_comments_to_csv(comments, &mut csv);

        csv
    }

    /// Iteratively flattens nested comment replies into CSV rows via DFS.
    fn flatten_comments_to_csv(comments: &[Comment], csv: &mut String) {
        let mut stack: Vec<&[Comment]> = vec![comments];

        while let Some(slice) = stack.pop() {
            for comment in slice {
                writeln!(
                    csv,
                    "{},{},{},{},{},{}",
                    escape_csv(&comment.author),
                    comment.created_utc,
                    escape_csv(&comment.body),
                    comment.score,
                    comment.is_submitter,
                    escape_csv(&comment.parent_id),
                )
                .expect("writing to String should never fail");

                if !comment.replies.is_empty() {
                    stack.push(&comment.replies);
                }
            }
        }
    }
}

/// Escapes a string for CSV format.
///
/// Wraps the string in quotes and escapes internal quotes.
fn escape_csv(s: &str) -> String {
    if s.contains('"') || s.contains(',') || s.contains('\n') || s.contains('\r') {
        format!("\"{}\"", s.replace('"', "\"\""))
    } else {
        s.to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn escape_csv_simple() {
        assert_eq!(escape_csv("hello"), "hello");
    }

    #[test]
    fn escape_csv_with_comma() {
        assert_eq!(escape_csv("hello, world"), "\"hello, world\"");
    }

    #[test]
    fn escape_csv_with_quotes() {
        assert_eq!(escape_csv("say \"hello\""), "\"say \"\"hello\"\"\"");
    }

    #[test]
    fn escape_csv_with_newline() {
        assert_eq!(escape_csv("line1\nline2"), "\"line1\nline2\"");
    }

    #[test]
    fn submissions_to_csv_header() {
        let exporter = CsvExporter::new();
        let csv = exporter.submissions_to_csv(&[]);

        assert!(csv.starts_with(
            "author,created_utc,title,score,num_comments,url,subreddit,is_self,nsfw\n"
        ));
    }

    #[test]
    fn comments_to_csv_header() {
        let exporter = CsvExporter::new();
        let csv = exporter.comments_to_csv(&[]);

        assert!(csv.starts_with("author,created_utc,body,score,is_submitter,parent_id\n"));
    }
}
