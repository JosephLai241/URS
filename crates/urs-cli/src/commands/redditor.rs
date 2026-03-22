//! Redditor scraping command.
//!
//! Scrapes a Reddit user's profile and interactions (submissions, comments, and overview) and
//! exports results to JSON.

use std::path::PathBuf;

use anyhow::{Result, bail};
use clap::Args;
use colored::Colorize;
use tracing::info;
use urs_core::export::{
    JsonExporter, ensure_dir, output_dir, output_dir_with_base, redditor_filename,
};
use urs_core::scrapers::RedditorScraper;

use crate::config;
use crate::helpers::{create_client, create_spinner};

/// Arguments for the `redditor` subcommand.
#[derive(Debug, Args)]
#[command(after_long_help = "\
\x1b[1;4mExamples:\x1b[0m

  Scrape the last 25 items per category for u/spez:
    urs redditor spez

  Scrape 100 items per category:
    urs redditor spez 100

  Save to a custom directory:
    urs redditor spez 50 --output ./my-data/

\x1b[1;4mScraped categories:\x1b[0m

  Public (always available):
    submissions, comments, hot, new, top, controversial, gilded

  Private (requires the authenticated user's own account):
    upvoted, downvoted, saved, hidden, gildings

  Categories that are private or inaccessible are marked as \"FORBIDDEN\"
  in the output rather than causing an error.")]
pub struct RedditorArgs {
    /// Reddit username (without the `u/` prefix).
    pub username: String,

    /// Number of items to scrape per category (default: 25, or config value).
    pub count: Option<usize>,

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
    let cfg = config::load_config().unwrap_or_default();

    let count = args
        .count
        .or_else(|| cfg.scraping.default_limit.map(|n| n as usize))
        .unwrap_or(25);

    println!(
        "{} {} {} {}",
        "Scraping".bright_green(),
        format!("u/{}", args.username).bold(),
        "—".dimmed(),
        format!("{count} items per category").bright_cyan(),
    );

    info!(
        username = %args.username,
        count = count,
        "Starting redditor scrape"
    );

    let spinner = create_spinner("Authenticating with Reddit...");
    let client = create_client().await?;
    let scraper = RedditorScraper::new(&client);

    spinner.set_message(format!("Validating u/{}...", args.username));
    if let Err(e) = scraper.about(&args.username).await {
        bail!(
            "Redditor u/{} does not exist or is suspended: {e}",
            args.username
        );
    }

    spinner.set_message(format!("Fetching interactions for u/{}...", args.username));
    let interactions = scraper.all_interactions(&args.username, count).await?;

    spinner.set_message("Exporting results...");

    let dir = args.output.unwrap_or_else(|| {
        cfg.scraping.scrapes_dir.as_ref().map_or_else(
            || output_dir("redditors"),
            |base| output_dir_with_base(base, "redditors"),
        )
    });
    ensure_dir(&dir)?;

    let filename = redditor_filename(&args.username, count);
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

    info!(path = %path.display(), "Redditor scrape complete");

    Ok(())
}
