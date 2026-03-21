//! Browse command — launch a local web viewer for scraped data.
//!
//! This command starts an axum HTTP server that serves a web UI for browsing scraped Reddit data
//! (JSON, JSONL, CSV files) with rich and raw view modes.

use std::path::PathBuf;

use clap::Args;
use colored::Colorize;

use crate::browse;
use crate::config;

/// Arguments for the `browse` command.
#[derive(Debug, Args)]
#[command(after_long_help = "\
\x1b[1;4mExamples:\x1b[0m

  Browse scraped data (opens browser automatically):
    urs browse

  Use a custom port:
    urs browse --port 3000

  Browse a different scrapes directory:
    urs browse --scrapes-dir ./my-scrapes/

  Don't auto-open the browser:
    urs browse --no-open

  Bind to all interfaces (e.g. for access from another device):
    urs browse --address 0.0.0.0 --port 8080

\x1b[1;4mFeatures:\x1b[0m

  Renders scraped data in a Reddit-like UI. Comment threads with nested
  replies, submission cards with scores and flair, Redditor profiles with
  tabbed categories, and livestream event feeds.

  Each item has a \"Show JSON\" button that opens a sidebar panel with the
  raw JSON data for that specific object.")]
pub struct BrowseArgs {
    /// Address to bind the web server on.
    #[arg(short, long)]
    pub address: Option<String>,

    /// Don't automatically open the browser.
    #[arg(long, default_value_t = false)]
    pub no_open: bool,

    /// Port to bind the web server on.
    #[arg(short, long)]
    pub port: Option<u16>,

    /// Root directory containing scraped data.
    #[arg(short = 'd', long)]
    pub scrapes_dir: Option<PathBuf>,
}

/// Runs the browse command.
///
/// Starts a local web server that serves a file browser and data viewer for scraped Reddit data.
///
/// # Errors
///
/// Returns an error if the server fails to bind or an I/O error occurs.
pub async fn run(args: BrowseArgs) -> anyhow::Result<()> {
    let cfg = config::load_config().unwrap_or_default();

    let address = args
        .address
        .unwrap_or_else(|| cfg.browse.address.clone());
    let port = args.port.unwrap_or(cfg.browse.port);
    let open_browser = !args.no_open && cfg.browse.auto_open;
    let raw_dir = args
        .scrapes_dir
        .or_else(|| cfg.scraping.scrapes_dir.clone())
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
        "{} Launching browse server at {}",
        "▸".cyan(),
        format!("http://{address}:{port}")
            .bold()
            .underline()
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
        "Starting browse server"
    );

    browse::server::run(browse::server::ServerConfig {
        address,
        open_browser,
        port,
        scrapes_dir,
    })
    .await
}
