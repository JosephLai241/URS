//! Interactive setup wizard for first-time configuration.
//!
//! Walks the user through entering Reddit API credentials and scraping defaults, then validates
//! credentials with a test API call.

use anyhow::{Context, Result};

use super::{CredentialsConfig, UrsConfig, config_path, load_config, save_config};

/// Runs the interactive setup wizard.
///
/// If a config file already exists, asks whether to overwrite.
///
/// # Errors
///
/// Returns an error if prompts fail or the config file cannot be written.
pub fn run_init() -> Result<()> {
    cliclack::intro("URS Configuration")?;

    let path = config_path();

    let mut config = load_existing_or_default(&path)?;

    if !config.credentials.is_complete() {
        prompt_credentials(&mut config)?;
    }

    validate_and_confirm(&config.credentials)?;
    prompt_scraping_settings(&mut config)?;

    save_config(&config)?;

    cliclack::outro(format!("Configuration saved to {}", path.display()))?;

    Ok(())
}

/// Loads an existing config or creates a default, prompting for overwrite if one exists.
fn load_existing_or_default(path: &std::path::Path) -> Result<UrsConfig> {
    if path.exists() {
        return Ok(UrsConfig::default());
    }

    let overwrite: bool = cliclack::confirm(format!(
        "Config already exists at {}. Overwrite?",
        path.display()
    ))
    .initial_value(false)
    .interact()?;

    if !overwrite {
        cliclack::outro("Aborted.")?;
        std::process::exit(0);
    }

    Ok(load_config().unwrap_or_default())
}

/// Prompts the user for Reddit API credentials.
fn prompt_credentials(config: &mut UrsConfig) -> Result<()> {
    cliclack::log::info("Create a \"script\" app at https://www.reddit.com/prefs/apps")?;

    config.credentials.client_id = Some(
        cliclack::input("Client ID")
            .placeholder("14-character string")
            .default_input(config.credentials.client_id.as_deref().unwrap_or(""))
            .interact()?,
    );

    config.credentials.client_secret = Some(
        cliclack::input("Client Secret")
            .placeholder("27-character string")
            .default_input(config.credentials.client_secret.as_deref().unwrap_or(""))
            .interact()?,
    );

    config.credentials.username = Some(
        cliclack::input("Reddit username")
            .placeholder("spez")
            .default_input(config.credentials.username.as_deref().unwrap_or(""))
            .interact()?,
    );

    config.credentials.password = Some(cliclack::password("Reddit password").mask('▪').interact()?);

    Ok(())
}

/// Validates credentials and asks whether to save if validation fails.
fn validate_and_confirm(creds: &CredentialsConfig) -> Result<()> {
    let spinner = cliclack::spinner();
    spinner.start("Validating credentials...");

    if let Err(e) = validate_credentials(creds) {
        spinner.stop(format!("Credential validation failed: {e}"));

        let save_anyway: bool = cliclack::confirm("Save credentials anyway?")
            .initial_value(true)
            .interact()?;

        if !save_anyway {
            cliclack::outro("Aborted.")?;
            std::process::exit(0);
        }
    } else {
        spinner.stop("Credentials are valid!");
    }

    Ok(())
}

/// Prompts for scraping-related settings.
fn prompt_scraping_settings(config: &mut UrsConfig) -> Result<()> {
    let default_dir = config
        .scraping
        .scrapes_dir
        .as_ref()
        .map_or_else(|| "scrapes".to_string(), |p| p.display().to_string());

    cliclack::log::info(
        "Scrape results are saved to this directory.\n\
         Use a relative path (resolved from your current directory) or an absolute path.\n\
         Press Enter to keep the default.",
    )?;

    let scrapes_dir: String = cliclack::input("Scrapes directory path")
        .placeholder(&default_dir)
        .default_input(&default_dir)
        .required(false)
        .interact()?;

    let raw_str = if scrapes_dir.is_empty() {
        &default_dir
    } else {
        &scrapes_dir
    };

    // Expand tilde and resolve relative paths to absolute so the config works from any cwd.
    let raw = super::expand_tilde(raw_str);
    let path = if raw.is_absolute() {
        raw
    } else {
        std::env::current_dir()
            .unwrap_or_default()
            .join(raw)
    };

    config.scraping.scrapes_dir = Some(path);

    Ok(())
}

/// Validates credentials by attempting to fetch an `OAuth2` token.
fn validate_credentials(creds: &CredentialsConfig) -> Result<()> {
    let client_id = creds.client_id.as_deref().context("Missing client_id")?;
    let client_secret = creds
        .client_secret
        .as_deref()
        .context("Missing client_secret")?;
    let username = creds.username.as_deref().context("Missing username")?;
    let password = creds.password.as_deref().context("Missing password")?;

    let client = reqwest::blocking::Client::new();
    let response = client
        .post("https://www.reddit.com/api/v1/access_token")
        .basic_auth(client_id, Some(client_secret))
        .header(
            "User-Agent",
            format!(
                "{}:com.{username}.urs:v{} (by /u/{username})",
                std::env::consts::OS,
                env!("CARGO_PKG_VERSION"),
            ),
        )
        .form(&[
            ("grant_type", "password"),
            ("username", username),
            ("password", password),
        ])
        .send()
        .context("Failed to connect to Reddit API")?;

    let status = response.status();
    if status.is_success() {
        let body: serde_json::Value = response.json().context("Failed to parse response")?;
        if body.get("access_token").is_some() {
            return Ok(());
        }
        if let Some(error) = body.get("error").and_then(|v| v.as_str()) {
            anyhow::bail!("Reddit API error: {error}");
        }
    }

    anyhow::bail!("Authentication failed (HTTP {status})");
}
