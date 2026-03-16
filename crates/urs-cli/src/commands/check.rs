//! Credential and connectivity check command.
//!
//! Verifies that Reddit `OAuth2` credentials are valid and displays current rate limit information.

use anyhow::{Context, Result};
use colored::Colorize;
use tabled::{Table, Tabled, settings::Style};
use tracing::info;
use url::Url;

use crate::helpers::{create_client, create_spinner};

/// A row in the rate limit table.
#[derive(Tabled)]
struct RateLimitRow {
    #[tabled(rename = "Used")]
    used: u32,
    #[tabled(rename = "Remaining")]
    remaining: String,
    #[tabled(rename = "Reset In")]
    reset_in: String,
}

/// The `/api/v1/me` endpoint, used to verify credentials and populate rate limits.
const ME_ENDPOINT: &str = "https://oauth.reddit.com/api/v1/me";

/// Executes the credential check command.
///
/// Authenticates with Reddit via `OAuth2`, makes a lightweight API request to populate rate limit
/// headers and displays the results.
///
/// # Errors
///
/// Returns an error if:
/// - Required environment variables are missing
/// - `OAuth2` authentication fails
/// - The API request fails
pub async fn run() -> Result<()> {
    info!("Starting credential check");

    println!(
        "{} {}",
        "→".bright_cyan(),
        "Checking Reddit API credentials...".bold()
    );

    let spinner = create_spinner("Authenticating with Reddit...");
    let client = create_client().await?;

    spinner.set_message("Verifying API access...");

    let me_url = Url::parse(ME_ENDPOINT).expect("hardcoded URL is valid");
    let me = client
        .get(&me_url)
        .await
        .context("Failed to fetch account info from Reddit API")?;

    spinner.finish_and_clear();

    println!(
        "{} {}",
        "✓".bright_green().bold(),
        "Authentication successful!".bold()
    );

    if let Some(name) = me.get("name").and_then(|v| v.as_str()) {
        info!(username = name, "Credential check passed");

        println!(
            "  {} Logged in as {}",
            "→".dimmed(),
            format!("u/{name}").bold().bright_cyan()
        );
    }

    if let Some(rate_limit) = client.rate_limit_info().await {
        println!();

        let row = RateLimitRow {
            used: rate_limit.used,
            remaining: format!("{:.0}", rate_limit.remaining),
            reset_in: {
                let total = rate_limit.reset;
                let hours = total / 3600;
                let minutes = (total % 3600) / 60;
                let seconds = total % 60;
                format!("{hours:02}:{minutes:02}:{seconds:02}")
            },
        };

        let mut table = Table::new([row]);
        table.with(Style::rounded());

        println!("{table}");
    }

    Ok(())
}
