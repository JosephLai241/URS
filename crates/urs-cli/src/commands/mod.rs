//! CLI command definitions and dispatch.
//!
//! This module defines the top-level CLI structure with subcommands for scraping Subreddits,
//! Redditors, submission comments, livestreaming Reddit activity, viewing logs, and checking
//! credentials.

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
pub struct Cli {
    /// Enable debug-level logging (default is INFO).
    #[arg(long, global = true, default_value_t = false)]
    pub debug: bool,

    /// The subcommand to execute.
    #[command(subcommand)]
    pub command: Commands,
}

/// Available CLI commands.
#[derive(Debug, Subcommand)]
pub enum Commands {
    /// Scrape posts from a Subreddit.
    Subreddit(subreddit::SubredditArgs),

    /// Scrape a Redditor's profile and interactions.
    Redditor(redditor::RedditorArgs),

    /// Scrape comments from a submission.
    Comments(comments::CommentsArgs),

    /// Livestream new Reddit activity in a TUI.
    Livestream(livestream::LivestreamArgs),

    /// View URS log output.
    Log(log::LogArgs),

    /// Check Reddit API credentials and rate limits.
    Check,
}

/// Dispatches the parsed CLI command to its handler.
///
/// # Errors
///
/// Returns an error if the command handler fails.
pub async fn dispatch(cli: Cli) -> anyhow::Result<()> {
    match cli.command {
        Commands::Subreddit(args) => subreddit::run(args).await,
        Commands::Redditor(args) => redditor::run(args).await,
        Commands::Comments(args) => comments::run(args).await,
        Commands::Livestream(args) => livestream::run(args).await,
        Commands::Log(args) => log::run(args).await,
        Commands::Check => check::run().await,
    }
}
