//! CLI command definitions and dispatch.
//!
//! This module defines the top-level CLI structure with subcommands for scraping Subreddits,
//! Redditors, submission comments, livestreaming Reddit activity, and additional utilities.

pub mod browse;
pub mod check;
pub mod comments;
pub mod livestream;
pub mod log;
pub mod redditor;
pub mod subreddit;

use clap::{Parser, Subcommand};

/// Universal Reddit Scraper — scrape Reddit data via the `OAuth2` API.
#[derive(Debug, Parser)]
#[command(name = "urs")]
#[command(author, version, about, long_about = None)]
#[command(after_long_help = "\
\x1b[1;4mQuick start:\x1b[0m

  1. Create a Reddit \"script\" app at https://www.reddit.com/prefs/apps
  2. Copy .env.example to .env and fill in your credentials
  3. Run a scrape:

     urs subreddit rust hot 50
     urs comments https://reddit.com/r/rust/comments/abc123/post_title/
     urs redditor spez

  4. Browse the results:

     urs browse

\x1b[1;4mGlobal options:\x1b[0m

  --debug    Enable debug-level logging for troubleshooting")]
pub struct Cli {
    /// The subcommand to execute.
    #[command(subcommand)]
    pub command: Commands,

    /// Enable debug-level logging (default is INFO).
    #[arg(long, global = true, default_value_t = false)]
    pub debug: bool,
}

/// Available CLI commands.
#[derive(Debug, Subcommand)]
pub enum Commands {
    /// Browse scraped data in a local web viewer.
    Browse(browse::BrowseArgs),

    /// Check Reddit API credentials and rate limits.
    Check,

    /// Scrape comments from a submission.
    Comments(comments::CommentsArgs),

    /// Livestream new Reddit activity in a TUI.
    Livestream(livestream::LivestreamArgs),

    /// View URS log output.
    Log(log::LogArgs),

    /// Scrape a Redditor's profile and interactions.
    Redditor(redditor::RedditorArgs),

    /// Scrape posts from a Subreddit.
    Subreddit(subreddit::SubredditArgs),
}

/// Dispatches the parsed CLI command to its handler.
///
/// # Errors
///
/// Returns an error if the command handler fails.
pub async fn dispatch(cli: Cli) -> anyhow::Result<()> {
    match cli.command {
        Commands::Browse(args) => browse::run(args).await,
        Commands::Check => check::run().await,
        Commands::Comments(args) => comments::run(args).await,
        Commands::Livestream(args) => livestream::run(args).await,
        Commands::Log(args) => log::run(args).await,
        Commands::Redditor(args) => redditor::run(args).await,
        Commands::Subreddit(args) => subreddit::run(args).await,
    }
}
