//! Comments scraping command.
//!
//! Scrapes comments from a Reddit submission URL and exports results to JSON, either as a threaded
//! tree or a flat list.

use std::path::PathBuf;

use anyhow::Result;
use clap::Args;
use colored::Colorize;
use tracing::info;
use urs_core::export::{JsonExporter, comments_filename, ensure_dir, output_dir};
use urs_core::scrapers::CommentsScraper;

use crate::helpers::{create_client, create_spinner};

/// Arguments for the `comments` subcommand.
#[derive(Debug, Args)]
pub struct CommentsArgs {
    /// Full Reddit submission URL.
    pub url: String,

    /// Number of comments to scrape (0 = all).
    #[arg(default_value_t = 0)]
    pub count: usize,

    /// Output as a flat list instead of a threaded tree.
    #[arg(long, default_value_t = false)]
    pub raw: bool,

    /// Custom output directory.
    #[arg(short, long)]
    pub output: Option<PathBuf>,
}

/// Executes the comments scraping command.
///
/// Fetches comments from a Reddit submission URL and exports them as JSON.
/// By default, comments are structured as a threaded tree. Use `--raw` for a flat list.
///
/// # Errors
///
/// Returns an error if:
/// - The URL is invalid
/// - Authentication fails
/// - The Reddit API request fails
/// - File export fails
pub async fn run(args: CommentsArgs) -> Result<()> {
    let mode = if args.raw { "raw" } else { "structured" };
    let count_str = if args.count == 0 {
        "all".to_string()
    } else {
        args.count.to_string()
    };

    println!(
        "{} {} {} {} {} {}",
        "Scraping".bright_green(),
        "comments".bold(),
        "—".dimmed(),
        count_str.bright_cyan(),
        "—".dimmed(),
        mode.bright_yellow(),
    );
    println!("  {} {}", "URL:".dimmed(), args.url.bright_blue());

    info!(url = %args.url, mode = mode, count = %count_str, "Starting comments scrape");

    let spinner = create_spinner("Authenticating with Reddit...");
    let client = create_client().await?;
    let scraper = CommentsScraper::new(&client);

    spinner.set_message("Fetching comments...");

    let limit = if args.count == 0 {
        None
    } else {
        Some(args.count)
    };
    let structured = !args.raw;
    let (comments, total) = scraper.from_url(&args.url, limit, structured).await?;

    spinner.set_message("Exporting results...");

    let title = extract_title_from_url(&args.url);
    let all_comments = args.count == 0;

    let dir = args.output.unwrap_or_else(|| output_dir("comments"));
    ensure_dir(&dir)?;
    let filename = comments_filename(&title, total, all_comments, args.raw);
    let path = dir.join(format!("{filename}.json"));

    JsonExporter::new().export_to_file(&comments, &path)?;

    spinner.finish_and_clear();

    println!(
        "\n{} {}",
        "✓".bright_green().bold(),
        "Scrape complete!".bold()
    );
    println!(
        "  {} {} comments scraped",
        "→".dimmed(),
        total.to_string().bright_cyan()
    );
    println!(
        "  {} Saved to {}",
        "→".dimmed(),
        path.display().to_string().bright_yellow()
    );

    info!(total = total, path = %path.display(), "Comments scrape complete");

    Ok(())
}

/// Extracts a title slug from a Reddit submission URL.
///
/// Parses the URL path to find the title segment, which is typically the 5th segment in URLs like:
/// `https://www.reddit.com/r/rust/comments/abc123/the_post_title/`
///
/// Falls back to "submission" if the title cannot be extracted.
fn extract_title_from_url(url: &str) -> String {
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
    fn extract_title_from_standard_url() {
        let url = "https://www.reddit.com/r/rust/comments/abc123/my_cool_post/";
        assert_eq!(extract_title_from_url(url), "my_cool_post");
    }

    #[test]
    fn extract_title_from_url_without_trailing_slash() {
        let url = "https://www.reddit.com/r/rust/comments/abc123/my_cool_post";
        assert_eq!(extract_title_from_url(url), "my_cool_post");
    }

    #[test]
    fn extract_title_fallback() {
        let url = "https://reddit.com/short";
        assert_eq!(extract_title_from_url(url), "submission");
    }
}
