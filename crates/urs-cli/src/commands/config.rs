//! Configuration management command.
//!
//! Provides subcommands for initializing, viewing, and modifying URS configuration.

use anyhow::{Result, bail};
use base64::Engine;
use clap::{Args, Subcommand};
use colored::Colorize;
use rand::RngCore;
use tabled::{Table, Tabled, settings::Style};

use crate::config;

/// Arguments for the `config` command.
#[derive(Debug, Args)]
#[command(after_long_help = "\
\x1b[1;4mExamples:\x1b[0m

  First-time setup (interactive wizard):
    urs config init

  Set the default scrapes directory:
    urs config set scraping.scrapes_dir ~/reddit-data

  Set the default export format to CSV:
    urs config set scraping.default_format csv

  Change the browse server port:
    urs config set browse.port 9090

  Check a specific setting:
    urs config get browse.port

  Show all settings:
    urs config show

  Print the config file path:
    urs config path

\x1b[1;4mAvailable keys:\x1b[0m

  api.address                   API server bind address (default: 127.0.0.1)
  api.port                      API server port (default: 3000)
  api.token                     Bearer token for API authentication
  browse.address                Browse server bind address (default: 127.0.0.1)
  browse.auto_open              Auto-open browser on browse (default: true)
  browse.port                   Browse server port (default: 8080)
  credentials.client_id         Reddit OAuth2 client ID (14-character string)
  credentials.client_secret     Reddit OAuth2 client secret (27-character string)
  credentials.password          Reddit account password
  credentials.username          Reddit account username
  scraping.default_format       Default export format: json or csv
  scraping.default_limit        Default result limit per scrape
  scraping.scrapes_dir          Default output directory (default: scrapes/)")]
pub struct ConfigArgs {
    /// The config subcommand to run.
    #[command(subcommand)]
    pub action: ConfigAction,
}

/// Config subcommands.
#[derive(Debug, Subcommand)]
pub enum ConfigAction {
    /// Delete the config file entirely.
    Delete,

    /// Generate a cryptographically secure API token and save it to config.
    ///
    /// Running this command again will replace any existing API token.
    GenerateApiToken,

    /// Get a config value.
    Get {
        /// The config key (e.g. "browse.port").
        key: String,
    },

    /// Run the interactive setup wizard.
    Init,

    /// Print the config file path.
    Path {
        /// Print just the directory, not the full file path.
        #[arg(long, default_value_t = false)]
        dir: bool,
    },

    /// Reset a config key to its default value, or reset all keys.
    Reset {
        /// The config key to reset (e.g. "browse.port"). Omit to reset all.
        key: Option<String>,
    },

    /// Set a config value.
    Set {
        /// The config key (e.g. "browse.port").
        key: String,

        /// The value to set.
        value: String,
    },

    /// Show all config settings.
    Show,
}

/// Runs the config command.
///
/// # Errors
///
/// Returns an error if the config file cannot be read, written, or a key is invalid.
pub fn run(args: ConfigArgs) -> Result<()> {
    match args.action {
        ConfigAction::Delete => run_delete(),
        ConfigAction::GenerateApiToken => run_generate_api_token(),
        ConfigAction::Get { key } => run_get(&key),
        ConfigAction::Init => config::init::run_init(),
        ConfigAction::Path { dir } => {
            if dir {
                println!("{}", config::config_dir().display());
            } else {
                println!("{}", config::config_path().display());
            }
            Ok(())
        }
        ConfigAction::Reset { key } => run_reset(key.as_deref()),
        ConfigAction::Set { key, value } => run_set(&key, &value),
        ConfigAction::Show => run_show(),
    }
}

/// Token length in bytes (32 bytes = 256 bits of entropy).
const TOKEN_BYTES: usize = 32;

/// Handles `urs config generate-api-token`.
fn run_generate_api_token() -> Result<()> {
    let mut bytes = [0u8; TOKEN_BYTES];
    rand::rng().fill_bytes(&mut bytes);
    let token = base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(bytes);

    let mut cfg = config::load_config()?;
    cfg.api.token = Some(token.clone());
    config::save_config(&cfg)?;

    println!(
        "{} Generated API token and saved to config\n",
        "✓".bright_green().bold(),
    );
    println!("  {token}\n");
    println!(
        "{}",
        "Include this token in API requests as:".dimmed()
    );
    println!(
        "  {}",
        format!("Authorization: Bearer {token}").bold()
    );

    Ok(())
}

/// Handles `urs config get <key>`.
fn run_get(key: &str) -> Result<()> {
    let cfg = config::load_config()?;

    if let Some(value) = config::get_value(&cfg, key) {
        println!("{value}");
    } else if config::CONFIG_KEYS.contains(&key) {
        println!("{}", "(not set)".dimmed());
    } else {
        bail!("Unknown config key: {key}");
    }

    Ok(())
}

/// Handles `urs config set <key> <value>`.
fn run_set(key: &str, value: &str) -> Result<()> {
    let mut cfg = config::load_config()?;

    config::set_value(&mut cfg, key, value)?;
    config::save_config(&cfg)?;

    println!(
        "{} {} {} {}",
        "✓".bright_green().bold(),
        key.bold(),
        "=".dimmed(),
        value
    );

    Ok(())
}

/// Handles `urs config delete`.
fn run_delete() -> Result<()> {
    let path = config::config_path();

    if !path.exists() {
        println!("{}", "No config file found.".dimmed());
        return Ok(());
    }

    std::fs::remove_file(&path)?;

    println!(
        "{} Deleted {}",
        "✓".bright_green().bold(),
        path.display().to_string().dimmed()
    );

    Ok(())
}

/// Handles `urs config reset [key]`.
fn run_reset(key: Option<&str>) -> Result<()> {
    if let Some(key) = key {
        if !config::CONFIG_KEYS.contains(&key) {
            bail!("Unknown config key: {key}");
        }

        let mut cfg = config::load_config()?;
        let defaults = config::UrsConfig::default();

        let default_value = config::get_value(&defaults, key);
        if let Some(ref val) = default_value {
            config::set_value(&mut cfg, key, val)?;
        } else {
            config::reset_key(&mut cfg, key);
        }

        config::save_config(&cfg)?;

        let display = default_value.unwrap_or_else(|| "(not set)".to_string());
        println!(
            "{} {} {} {}",
            "✓".bright_green().bold(),
            key.bold(),
            "reset to".dimmed(),
            display
        );
    } else {
        let cfg = config::UrsConfig::default();
        config::save_config(&cfg)?;

        println!(
            "{} {}",
            "✓".bright_green().bold(),
            "All settings reset to defaults".bold()
        );
    }

    Ok(())
}

/// A single row in the config list table.
#[derive(Tabled)]
struct ConfigRow {
    /// The config key.
    #[tabled(rename = "NAME")]
    name: String,
    /// The config value.
    #[tabled(rename = "VALUE")]
    value: String,
}

/// Handles `urs config show`.
fn run_show() -> Result<()> {
    let cfg = config::load_config()?;

    let rows: Vec<ConfigRow> = config::CONFIG_KEYS
        .iter()
        .map(|&key| {
            let value = config::get_value(&cfg, key).unwrap_or_else(|| "(not set)".to_string());
            ConfigRow {
                name: key.to_string(),
                value,
            }
        })
        .collect();

    let mut table = Table::new(rows);
    table.with(Style::rounded());

    println!("{table}");

    Ok(())
}
