//! CLI command definitions and dispatch.
//!
//! This module defines the top-level CLI structure with subcommands for scraping Subreddits,
//! Redditors, submission comments, livestreaming Reddit activity, and additional utilities.

pub mod analyze;
pub mod check;
pub mod comments;
pub mod config;
pub mod livestream;
pub mod log;
pub mod redditor;
#[cfg(feature = "api")]
pub mod serve;
pub mod subreddit;

use std::path::PathBuf;

use clap::{Parser, Subcommand};
use colored::Colorize;

use crate::browse;
use crate::config as cfg;
use crate::helpers;

/// Universal Reddit Scraper — scrape Reddit data via the `OAuth2` API.
#[derive(Debug, Parser)]
#[command(name = "urs")]
#[command(author, version, about, long_about = None)]
#[command(after_long_help = "\
\x1b[1;4mQuick start:\x1b[0m

  1. Create a Reddit \"script\" app at https://www.reddit.com/prefs/apps
  2. Run the setup wizard: urs config init
  3. Run a scrape:

     urs subreddit rust hot 50
     urs comments https://reddit.com/r/rust/comments/abc123/post_title/
     urs redditor spez

  4. Launch the web UI:

     urs

\x1b[1;4mGlobal options:\x1b[0m

  --debug    Enable debug-level logging for troubleshooting")]
pub struct Cli {
    /// The subcommand to execute. If omitted, launches the web UI.
    #[command(subcommand)]
    pub command: Option<Commands>,

    /// Enable debug-level logging (default is INFO).
    #[arg(long, global = true, default_value_t = false)]
    pub debug: bool,
}

/// Available CLI commands.
#[derive(Debug, Subcommand)]
pub enum Commands {
    /// Analyze word frequencies in a scrape file.
    Analyze(analyze::AnalyzeArgs),

    /// Check Reddit API credentials and rate limits.
    Check,

    /// Scrape comments from a submission.
    Comments(comments::CommentsArgs),

    /// Manage URS configuration.
    Config(config::ConfigArgs),

    /// Livestream new Reddit activity in a TUI.
    Livestream(livestream::LivestreamArgs),

    /// View URS log output.
    Log(log::LogArgs),

    /// Scrape a Redditor's profile and interactions.
    Redditor(redditor::RedditorArgs),

    /// Start the REST API server (requires the `api` feature).
    #[cfg(feature = "api")]
    Serve(serve::ServeArgs),

    /// Scrape posts from a Subreddit.
    Subreddit(subreddit::SubredditArgs),
}

/// Dispatches the parsed CLI command to its handler.
///
/// When no subcommand is provided, launches the web UI.
///
/// # Errors
///
/// Returns an error if the command handler fails.
pub async fn dispatch(cli: Cli) -> anyhow::Result<()> {
    match cli.command {
        None => launch_ui().await,
        Some(cmd) => dispatch_command(cmd).await,
    }
}

/// Launches the web UI server (default when no subcommand is given).
async fn launch_ui() -> anyhow::Result<()> {
    let config = cfg::load_config().unwrap_or_default();

    let address = config.browse.address.clone();
    let port = config.browse.port;
    let open_browser = config.browse.auto_open;
    let raw_dir = config
        .scraping
        .scrapes_dir
        .clone()
        .unwrap_or_else(|| PathBuf::from("scrapes"));

    let scrapes_dir = raw_dir.canonicalize().unwrap_or_else(|_| {
        std::env::current_dir()
            .expect("Failed to get current directory")
            .join(&raw_dir)
    });

    if !scrapes_dir.is_dir() {
        anyhow::bail!(
            "Scrapes directory does not exist: {}",
            scrapes_dir.display()
        );
    }

    println!(
        "{} Launching URS at {}",
        "▸".cyan(),
        format!("http://{address}:{port}").bold().underline()
    );
    println!(
        "  {} {}",
        "Scrapes directory:".dimmed(),
        scrapes_dir.display()
    );
    println!("  {} Ctrl+C to stop\n", "Tip:".dimmed());

    tracing::info!(
        address = %address,
        port = port,
        scrapes_dir = %scrapes_dir.display(),
        "Starting URS web UI"
    );

    let client = helpers::try_create_client().await;

    browse::server::run(browse::server::ServerConfig {
        address,
        client,
        open_browser,
        port,
        scrapes_dir,
    })
    .await
}

/// Dispatches an explicit CLI subcommand.
async fn dispatch_command(cmd: Commands) -> anyhow::Result<()> {
    match cmd {
        Commands::Analyze(args) => tokio::task::spawn_blocking(move || analyze::run(args))
            .await
            .expect("Analyze task panicked"),
        Commands::Check => check::run().await,
        Commands::Comments(args) => comments::run(args).await,
        Commands::Config(args) => tokio::task::spawn_blocking(move || config::run(args))
            .await
            .expect("Config task panicked"),
        Commands::Livestream(args) => livestream::run(args).await,
        Commands::Log(args) => log::run(args).await,
        Commands::Redditor(args) => redditor::run(args).await,
        #[cfg(feature = "api")]
        Commands::Serve(args) => serve::run(args).await,
        Commands::Subreddit(args) => subreddit::run(args).await,
    }
}
