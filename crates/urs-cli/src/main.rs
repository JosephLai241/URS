//! Universal Reddit Scraper CLI.
//!
//! A command-line tool for scraping Reddit data using the `OAuth2` API.
//! Supports scraping subreddits, redditor profiles, and submission comments, with export to JSON
//! or CSV.

mod browse;
mod commands;
mod config;
mod helpers;
mod tui;

use clap::Parser;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;

use commands::{Cli, dispatch};

/// Run `URS`.
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    let log_dir = helpers::log_dir();
    std::fs::create_dir_all(&log_dir)?;

    let file_appender = tracing_appender::rolling::daily(&log_dir, "urs.log");
    let (non_blocking, _guard) = tracing_appender::non_blocking(file_appender);

    // `--debug` flag overrides RUST_LOG; default is INFO.
    let env_filter = if cli.debug {
        tracing_subscriber::EnvFilter::new("debug")
    } else {
        tracing_subscriber::EnvFilter::try_from_default_env()
            .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info"))
    };

    // Browse command gets stderr logging so users see server activity in the terminal. Other
    // commands only log to the file to keep terminal output clean.
    let is_browse = matches!(cli.command, commands::Commands::Browse(_));

    let registry = tracing_subscriber::registry()
        .with(env_filter)
        .with(tracing_subscriber::fmt::layer().with_writer(non_blocking));

    if is_browse {
        registry
            .with(tracing_subscriber::fmt::layer().with_writer(std::io::stderr))
            .init();
    } else {
        registry.init();
    }

    tracing::debug!(log_dir = %log_dir.display(), "Logging initialized");

    helpers::print_banner();

    tracing::debug!(command = ?cli.command, "Dispatching command");
    dispatch(cli).await
}
