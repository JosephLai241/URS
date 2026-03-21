//! Shared helpers for CLI commands.
//!
//! Provides common utilities used across all CLI commands, including authenticated client creation
//! and progress spinner setup.

use anyhow::{Context, Result};
use colored::Colorize;
use indicatif::{ProgressBar, ProgressStyle};
use tracing::{debug, info};
use urs_core::auth::Credentials;
use urs_core::client::RedditClient;

use crate::config;

/// Creates an authenticated Reddit client.
///
/// Resolves credentials with the following precedence (highest to lowest):
/// 1. Environment variables (`URS_CLIENT_ID`, `URS_CLIENT_SECRET`, `URS_REDDIT_USERNAME`,
///    `URS_REDDIT_PASSWORD`)
/// 2. Config file (`~/.config/urs/config.toml` or platform equivalent)
///
/// If authentication fails, prints a hint to run `urs config init`.
///
/// # Errors
///
/// Returns an error if credentials are incomplete or `OAuth2` authentication fails.
pub async fn create_client() -> Result<RedditClient> {
    debug!("Resolving Reddit credentials");

    let credentials = resolve_credentials().inspect_err(|_| print_auth_hint())?;

    debug!("Authenticating with Reddit API");

    let client = RedditClient::new(credentials)
        .await
        .inspect_err(|_| print_auth_hint())
        .context("Failed to authenticate with Reddit")?;

    info!("Authenticated with Reddit API");

    Ok(client)
}

/// Resolves credentials from config file + environment variable overrides.
fn resolve_credentials() -> Result<Credentials> {
    let cfg = config::load_config().unwrap_or_default();

    // URS_-prefixed environment variables override config file values.
    let client_id = std::env::var("URS_CLIENT_ID")
        .ok()
        .or(cfg.credentials.client_id);
    let client_secret = std::env::var("URS_CLIENT_SECRET")
        .ok()
        .or(cfg.credentials.client_secret);
    let username = std::env::var("URS_REDDIT_USERNAME")
        .ok()
        .or(cfg.credentials.username);
    let password = std::env::var("URS_REDDIT_PASSWORD")
        .ok()
        .or(cfg.credentials.password);

    let client_id =
        client_id.context("Missing URS_CLIENT_ID (set via env var or urs config init)")?;
    let client_secret =
        client_secret.context("Missing URS_CLIENT_SECRET (set via env var or urs config init)")?;
    let username =
        username.context("Missing URS_REDDIT_USERNAME (set via env var or urs config init)")?;
    let password =
        password.context("Missing URS_REDDIT_PASSWORD (set via env var or urs config init)")?;

    let user_agent = std::env::var("URS_USER_AGENT").unwrap_or_else(|_| {
        format!(
            "{}:com.{username}.urs:v{} (by /u/{username})",
            std::env::consts::OS,
            env!("CARGO_PKG_VERSION"),
        )
    });

    Ok(Credentials::new(
        client_id,
        client_secret,
        username,
        password,
        user_agent,
    ))
}

/// Resolves the API token from environment variable or config file.
///
/// The `URS_API_TOKEN` environment variable takes precedence over the `api.token` value in
/// `config.toml`. Returns `None` if neither is set.
#[must_use]
pub fn resolve_api_token() -> Option<String> {
    let cfg = config::load_config().unwrap_or_default();
    std::env::var("URS_API_TOKEN").ok().or(cfg.api.token)
}

/// Prints a hint to run `urs config init` when authentication fails.
fn print_auth_hint() {
    eprintln!(
        "\n{} Run {} to configure your Reddit API credentials.",
        "hint:".bright_yellow().bold(),
        "urs config init".bold(),
    );
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
