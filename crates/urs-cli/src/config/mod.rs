//! User configuration management.
//!
//! Loads and saves URS configuration from a platform-specific TOML file. Provides the [`UrsConfig`]
//! struct that centralizes credentials, scraping defaults, and browse server settings.

pub mod init;

use std::fs;
use std::path::PathBuf;

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use tracing::debug;

/// Returns the path to the URS config file.
///
/// | Platform | Path |
/// |----------|------|
/// | macOS | `~/Library/Application Support/urs/config.toml` |
/// | Linux | `~/.config/urs/config.toml` |
/// | Windows | `C:\Users\<user>\AppData\Roaming\urs\config.toml` |
///
/// # Panics
///
/// Panics if the platform has no valid home/config directory.
#[must_use]
pub fn config_path() -> PathBuf {
    let dirs = directories::ProjectDirs::from("", "", "urs")
        .expect("Failed to determine platform config directory");
    dirs.config_dir().join("config.toml")
}

/// Returns the directory containing the config file.
///
/// # Panics
///
/// Panics if the platform has no valid home/config directory.
#[must_use]
pub fn config_dir() -> PathBuf {
    let dirs = directories::ProjectDirs::from("", "", "urs")
        .expect("Failed to determine platform config directory");
    dirs.config_dir().to_path_buf()
}

/// Loads the URS config from disk.
///
/// Returns the default config if the file does not exist.
///
/// # Errors
///
/// Returns an error if the file exists but cannot be read or parsed.
pub fn load_config() -> Result<UrsConfig> {
    let path = config_path();

    if !path.exists() {
        debug!("No config file found at {}, using defaults", path.display());
        return Ok(UrsConfig::default());
    }

    debug!("Loading config from {}", path.display());

    let contents =
        fs::read_to_string(&path).with_context(|| format!("Failed to read {}", path.display()))?;
    let config: UrsConfig =
        toml::from_str(&contents).with_context(|| format!("Failed to parse {}", path.display()))?;

    Ok(config)
}

/// Saves the URS config to disk.
///
/// Creates the parent directory if it does not exist.
///
/// # Errors
///
/// Returns an error if the file cannot be written.
pub fn save_config(config: &UrsConfig) -> Result<()> {
    let path = config_path();

    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)
            .with_context(|| format!("Failed to create config directory: {}", parent.display()))?;
    }

    let contents = toml::to_string_pretty(config).context("Failed to serialize config to TOML")?;
    fs::write(&path, contents)
        .with_context(|| format!("Failed to write config to {}", path.display()))?;

    debug!("Saved config to {}", path.display());

    Ok(())
}

/// Top-level URS configuration.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct UrsConfig {
    /// Browse server settings.
    #[serde(default)]
    pub browse: BrowseConfig,
    /// Reddit API credentials.
    #[serde(default)]
    pub credentials: CredentialsConfig,
    /// Scraping defaults.
    #[serde(default)]
    pub scraping: ScrapingConfig,
}

/// Reddit `OAuth2` API credentials.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct CredentialsConfig {
    /// The `OAuth2` client ID.
    pub client_id: Option<String>,
    /// The `OAuth2` client secret.
    pub client_secret: Option<String>,
    /// The Reddit account password.
    pub password: Option<String>,
    /// The Reddit account username.
    pub username: Option<String>,
}

impl CredentialsConfig {
    /// Returns `true` if all required credentials are set.
    #[must_use]
    pub const fn is_complete(&self) -> bool {
        self.client_id.is_some()
            && self.client_secret.is_some()
            && self.password.is_some()
            && self.username.is_some()
    }
}

/// Default export format.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ExportFormat {
    /// CSV export format.
    Csv,
    /// JSON export format.
    #[default]
    Json,
}

impl std::fmt::Display for ExportFormat {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Csv => write!(f, "csv"),
            Self::Json => write!(f, "json"),
        }
    }
}

/// Scraping default settings.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct ScrapingConfig {
    /// Default export format.
    #[serde(default)]
    pub default_format: ExportFormat,
    /// Default result limit when not specified on the CLI.
    pub default_limit: Option<u32>,
    /// Default directory for saving scrape results.
    pub scrapes_dir: Option<PathBuf>,
}

/// Browse web server settings.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrowseConfig {
    /// Bind address.
    #[serde(default = "default_address")]
    pub address: String,
    /// Whether to auto-open the browser.
    #[serde(default = "default_auto_open")]
    pub auto_open: bool,
    /// HTTP port.
    #[serde(default = "default_port")]
    pub port: u16,
}

impl Default for BrowseConfig {
    fn default() -> Self {
        Self {
            address: default_address(),
            auto_open: default_auto_open(),
            port: default_port(),
        }
    }
}

/// Default browse address.
fn default_address() -> String {
    "127.0.0.1".to_string()
}

/// Default auto-open setting.
const fn default_auto_open() -> bool {
    true
}

/// Default browse port.
const fn default_port() -> u16 {
    8080
}

/// Expands a leading `~` in a path to the user's home directory.
///
/// Shell tilde expansion doesn't happen when arguments are quoted, so `urs config set
/// scraping.scrapes_dir "~/data"` would store a literal `~/data`. This function handles that case.
pub fn expand_tilde(path: &str) -> PathBuf {
    if let Some(rest) = path.strip_prefix("~/") {
        if let Some(home) = directories::UserDirs::new() {
            return home.home_dir().join(rest);
        }
    } else if path == "~" {
        if let Some(home) = directories::UserDirs::new() {
            return home.home_dir().to_path_buf();
        }
    }
    PathBuf::from(path)
}

/// All recognized config keys for `get`/`set` operations.
pub const CONFIG_KEYS: &[&str] = &[
    "browse.address",
    "browse.auto_open",
    "browse.port",
    "credentials.client_id",
    "credentials.client_secret",
    "credentials.password",
    "credentials.username",
    "scraping.default_format",
    "scraping.default_limit",
    "scraping.scrapes_dir",
];

/// Gets a config value by dotted key path.
///
/// Returns `None` if the key is unrecognized.
#[must_use]
pub fn get_value(config: &UrsConfig, key: &str) -> Option<String> {
    match key {
        "browse.address" => Some(config.browse.address.clone()),
        "browse.auto_open" => Some(config.browse.auto_open.to_string()),
        "browse.port" => Some(config.browse.port.to_string()),
        "credentials.client_id" => config.credentials.client_id.clone(),
        "credentials.client_secret" => config.credentials.client_secret.clone(),
        "credentials.password" => config.credentials.password.clone(),
        "credentials.username" => config.credentials.username.clone(),
        "scraping.default_format" => Some(config.scraping.default_format.to_string()),
        "scraping.default_limit" => config.scraping.default_limit.map(|n| n.to_string()),
        "scraping.scrapes_dir" => config
            .scraping
            .scrapes_dir
            .as_ref()
            .map(|p| p.display().to_string()),
        _ => None,
    }
}

/// Sets a config value by dotted key path.
///
/// # Errors
///
/// Returns an error if the key is unrecognized or the value is invalid.
pub fn set_value(config: &mut UrsConfig, key: &str, value: &str) -> Result<()> {
    match key {
        "browse.address" => config.browse.address = value.to_string(),
        "browse.auto_open" => {
            config.browse.auto_open = value
                .parse()
                .context("Invalid value for browse.auto_open (expected true or false)")?;
        }
        "browse.port" => {
            let port: u16 = value
                .parse()
                .context("Invalid value for browse.port (expected a number 1-65535)")?;
            if port == 0 {
                anyhow::bail!("Invalid port: 0 (must be 1-65535)");
            }
            config.browse.port = port;
        }
        "credentials.client_id" => config.credentials.client_id = Some(value.to_string()),
        "credentials.client_secret" => config.credentials.client_secret = Some(value.to_string()),
        "credentials.password" => config.credentials.password = Some(value.to_string()),
        "credentials.username" => config.credentials.username = Some(value.to_string()),
        "scraping.default_format" => {
            config.scraping.default_format = match value {
                "json" => ExportFormat::Json,
                "csv" => ExportFormat::Csv,
                _ => anyhow::bail!("Invalid format: {value} (expected \"json\" or \"csv\")"),
            };
        }
        "scraping.default_limit" => {
            config.scraping.default_limit = if value == "none" || value.is_empty() {
                None
            } else {
                Some(
                    value
                        .parse()
                        .context("Invalid value for scraping.default_limit (expected a number)")?,
                )
            };
        }
        "scraping.scrapes_dir" => {
            config.scraping.scrapes_dir = if value == "none" || value.is_empty() {
                None
            } else {
                let path = expand_tilde(value);
                if path.is_absolute() {
                    Some(path)
                } else {
                    Some(std::env::current_dir().unwrap_or_default().join(path))
                }
            };
        }
        _ => anyhow::bail!("Unknown config key: {key}"),
    }

    Ok(())
}

/// Resets a config key to its default (unset) state for `Option`-backed fields.
///
/// For keys backed by `Option<T>`, this sets the field to `None`.
/// For keys with non-optional defaults (e.g. `browse.port`), use [`set_value`] with the default
/// value instead.
pub fn reset_key(config: &mut UrsConfig, key: &str) {
    match key {
        "credentials.client_id" => config.credentials.client_id = None,
        "credentials.client_secret" => config.credentials.client_secret = None,
        "credentials.password" => config.credentials.password = None,
        "credentials.username" => config.credentials.username = None,
        "scraping.default_limit" => config.scraping.default_limit = None,
        "scraping.scrapes_dir" => config.scraping.scrapes_dir = None,
        _ => {} // Non-optional fields are handled via set_value with default value
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_config_round_trips() {
        let config = UrsConfig::default();
        let serialized = toml::to_string_pretty(&config).unwrap();
        let deserialized: UrsConfig = toml::from_str(&serialized).unwrap();

        assert_eq!(deserialized.browse.port, config.browse.port);
        assert_eq!(deserialized.browse.address, config.browse.address);
    }

    #[test]
    fn get_set_browse_port() {
        let mut config = UrsConfig::default();

        set_value(&mut config, "browse.port", "9090").unwrap();

        assert_eq!(get_value(&config, "browse.port"), Some("9090".to_string()));
        assert_eq!(config.browse.port, 9090);
    }

    #[test]
    fn get_set_credentials() {
        let mut config = UrsConfig::default();

        set_value(&mut config, "credentials.client_id", "abc123").unwrap();

        assert_eq!(
            get_value(&config, "credentials.client_id"),
            Some("abc123".to_string())
        );
    }

    #[test]
    fn set_invalid_port_returns_error() {
        let mut config = UrsConfig::default();
        let result = set_value(&mut config, "browse.port", "not_a_number");

        assert!(result.is_err());
    }

    #[test]
    fn set_unknown_key_returns_error() {
        let mut config = UrsConfig::default();
        let result = set_value(&mut config, "unknown.key", "value");

        assert!(result.is_err());
    }

    #[test]
    fn get_unknown_key_returns_none() {
        let config = UrsConfig::default();

        assert!(get_value(&config, "unknown.key").is_none());
    }

    #[test]
    fn set_default_format() {
        let mut config = UrsConfig::default();

        set_value(&mut config, "scraping.default_format", "csv").unwrap();
        assert_eq!(
            get_value(&config, "scraping.default_format"),
            Some("csv".to_string())
        );

        set_value(&mut config, "scraping.default_format", "json").unwrap();
        assert_eq!(
            get_value(&config, "scraping.default_format"),
            Some("json".to_string())
        );
    }

    #[test]
    fn set_invalid_format_returns_error() {
        let mut config = UrsConfig::default();
        let result = set_value(&mut config, "scraping.default_format", "xml");

        assert!(result.is_err());
    }

    #[test]
    fn set_port_zero_returns_error() {
        let mut config = UrsConfig::default();
        let result = set_value(&mut config, "browse.port", "0");

        assert!(result.is_err());
    }

    #[test]
    fn reset_key_clears_optional_field() {
        let mut config = UrsConfig::default();
        config.credentials.client_id = Some("test".to_string());

        reset_key(&mut config, "credentials.client_id");

        assert!(config.credentials.client_id.is_none());
    }

    #[test]
    fn reset_key_clears_scrapes_dir() {
        let mut config = UrsConfig::default();
        config.scraping.scrapes_dir = Some(PathBuf::from("/some/path"));

        reset_key(&mut config, "scraping.scrapes_dir");

        assert!(config.scraping.scrapes_dir.is_none());
    }

    #[test]
    fn expand_tilde_expands_home() {
        let result = expand_tilde("~/data");

        // Should not start with ~ anymore
        assert!(!result.to_string_lossy().starts_with('~'));
        assert!(result.to_string_lossy().ends_with("/data"));
    }

    #[test]
    fn expand_tilde_leaves_absolute_paths() {
        let result = expand_tilde("/usr/local/data");

        assert_eq!(result, PathBuf::from("/usr/local/data"));
    }

    #[test]
    fn expand_tilde_leaves_relative_paths() {
        let result = expand_tilde("my-data");

        assert_eq!(result, PathBuf::from("my-data"));
    }

    #[test]
    fn set_scrapes_dir_expands_tilde() {
        let mut config = UrsConfig::default();
        set_value(&mut config, "scraping.scrapes_dir", "~/reddit-data").unwrap();

        let dir = config.scraping.scrapes_dir.unwrap();

        assert!(!dir.to_string_lossy().starts_with('~'));
        assert!(dir.to_string_lossy().ends_with("/reddit-data"));
    }

    #[test]
    fn credentials_complete_when_all_set() {
        let mut config = UrsConfig::default();

        assert!(!config.credentials.is_complete());

        config.credentials.client_id = Some("id".to_string());
        config.credentials.client_secret = Some("secret".to_string());
        config.credentials.username = Some("user".to_string());
        config.credentials.password = Some("pass".to_string());

        assert!(config.credentials.is_complete());
    }
}
