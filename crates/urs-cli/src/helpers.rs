//! Shared helpers for CLI commands.
//!
//! Provides common utilities used across all CLI commands, including authenticated client creation
//! and progress spinner setup.

use anyhow::{Context, Result};
use colored::Colorize;
use indicatif::{ProgressBar, ProgressStyle};
use urs_core::auth::Credentials;
use urs_core::client::RedditClient;

/// Creates an authenticated Reddit client from environment variables.
///
/// Loads credentials from the `.env` file (via `dotenvy`) and environment variables, then
/// authenticates with Reddit's `OAuth2` API.
///
/// # Errors
///
/// Returns an error if:
/// - Required environment variables are missing
/// - `OAuth2` authentication fails
pub async fn create_client() -> Result<RedditClient> {
    let credentials =
        Credentials::from_env().context("Failed to load Reddit credentials from environment")?;

    let client = RedditClient::new(credentials)
        .await
        .context("Failed to authenticate with Reddit")?;

    Ok(client)
}

/// Creates a styled spinner progress bar with the given message.
///
/// The spinner uses a dots style and displays while long-running operations are in progress.
///
/// # Arguments
///
/// * `msg` - The message to display next to the spinner
#[must_use]
pub fn create_spinner(msg: &str) -> ProgressBar {
    let spinner = ProgressBar::new_spinner();
    spinner.set_style(
        ProgressStyle::default_spinner()
            .tick_chars("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")
            .template("{spinner:.cyan} {wide_msg}")
            .expect("Invalid spinner template"),
    );
    spinner.set_message(msg.to_string());
    spinner.enable_steady_tick(std::time::Duration::from_millis(80));

    spinner
}

/// Returns the directory used for log files.
///
/// Uses the platform-specific data directory via the `directories` crate:
/// - Linux: `~/.local/share/urs/logs`
/// - macOS: `~/Library/Application Support/urs/logs`
/// - Windows: `C:\Users\<user>\AppData\Roaming\urs\logs`
///
/// # Panics
///
/// Panics if the platform has no valid home/data directory.
#[must_use]
pub fn log_dir() -> std::path::PathBuf {
    let dirs = directories::ProjectDirs::from("", "", "urs")
        .expect("Failed to determine platform data directory");
    dirs.data_dir().join("logs")
}

/// The URS ASCII art banner, embedded at compile time.
const BANNER: &str = include_str!("../assets/banner.txt");

/// Prints the URS banner header.
pub fn print_banner() {
    print!("{}", BANNER.bold().truecolor(206, 66, 43));
    println!("  v{}\n", env!("CARGO_PKG_VERSION"));
}
