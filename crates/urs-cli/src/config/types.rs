//! Configuration types for API, scraping, browse, and export settings.
//!
//! Provides [`ApiConfig`], [`ScrapingConfig`], [`BrowseConfig`], and [`ExportFormat`] used by the
//! top-level [`UrsConfig`](super::UrsConfig).

use std::path::PathBuf;

use serde::{Deserialize, Serialize};

/// REST API server settings.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiConfig {
    /// Bind address for the API server.
    #[serde(default = "default_api_address")]
    pub address: String,
    /// HTTP port for the API server.
    #[serde(default = "default_api_port")]
    pub port: u16,
    /// Bearer token for API authentication.
    ///
    /// When set, all API endpoints (except `/api/health`) require an
    /// `Authorization: Bearer <token>` header.
    pub token: Option<String>,
}

impl Default for ApiConfig {
    fn default() -> Self {
        Self {
            address: default_api_address(),
            port: default_api_port(),
            token: None,
        }
    }
}

/// Default API server address.
fn default_api_address() -> String {
    "127.0.0.1".to_string()
}

/// Default API server port.
const fn default_api_port() -> u16 {
    3000
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
