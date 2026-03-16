//! Redditor scraping command.
//!
//! Scrapes a Reddit user's profile and interactions (submissions, comments, and overview) and
//! exports results to JSON.

use std::path::PathBuf;

use anyhow::Result;
use clap::Args;
use colored::Colorize;
use urs_core::export::{JsonExporter, ensure_dir, output_dir, redditor_filename};
use urs_core::scrapers::RedditorScraper;

use crate::helpers::{create_client, create_spinner};

/// Arguments for the `redditor` subcommand.
#[derive(Debug, Args)]
pub struct RedditorArgs {
    /// Reddit username (without the `u/` prefix).
    pub username: String,

    /// Number of items to scrape per category.
    #[arg(default_value_t = 25)]
    pub count: usize,

    /// Custom output directory.
    #[arg(short, long)]
    pub output: Option<PathBuf>,
}

/// Executes the Redditor scraping command.
///
/// Fetches all interactions (submissions, comments, overview) for a user
/// and exports the combined results as JSON.
///
/// # Errors
///
/// Returns an error if:
/// - Authentication fails
/// - The Reddit API request fails
/// - File export fails
pub async fn run(args: RedditorArgs) -> Result<()> {
    println!(
        "{} {} {} {}",
        "Scraping".bright_green(),
        format!("u/{}", args.username).bold(),
        "—".dimmed(),
        format!("{} items per category", args.count).bright_cyan(),
    );

    let spinner = create_spinner("Authenticating with Reddit...");
    let client = create_client().await?;
    let scraper = RedditorScraper::new(&client);

    spinner.set_message(format!("Fetching interactions for u/{}...", args.username));
    let interactions = scraper.all_interactions(&args.username, args.count).await?;

    spinner.set_message("Exporting results...");

    let dir = args.output.unwrap_or_else(|| output_dir("redditors"));
    ensure_dir(&dir)?;

    let filename = redditor_filename(&args.username, args.count);
    let path = dir.join(format!("{filename}.json"));

    JsonExporter::new().export_to_file(&interactions, &path)?;

    spinner.finish_and_clear();

    println!(
        "\n{} {}",
        "✓".bright_green().bold(),
        "Scrape complete!".bold()
    );
    println!(
        "  {} Saved to {}",
        "→".dimmed(),
        path.display().to_string().bright_yellow()
    );

    Ok(())
}
