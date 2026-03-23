//! Axum web server setup, binding, and graceful shutdown.
//!
//! Configures the HTTP router, binds to the specified address/port, and handles graceful shutdown
//! on Ctrl+C.

use std::path::PathBuf;
use std::sync::Arc;
use std::time::Instant;

use axum::Router;
use dashmap::DashMap;
use tokio::net::TcpListener;
use tokio::signal;
use tokio_util::sync::CancellationToken;
use url::Url;
use urs_core::client::RedditClient;

use super::routes;

/// Server configuration.
pub struct ServerConfig {
    /// Bind address (e.g. "127.0.0.1").
    pub address: String,
    /// Authenticated Reddit client for scraping (None if credentials are not configured).
    pub client: Option<RedditClient>,
    /// Whether to open the browser automatically.
    pub open_browser: bool,
    /// Bind port (e.g. 8080).
    pub port: u16,
    /// Root directory containing scraped data.
    pub scrapes_dir: PathBuf,
}

/// Progress state for a single background scrape task.
#[derive(Debug, Clone)]
pub struct ScrapeTask {
    /// Human-readable detail for the current stage (e.g. "Fetching posts...").
    pub detail: String,
    /// Error message if the task failed.
    pub error: Option<String>,
    /// When this task reached a terminal state (complete or error).
    pub finished_at: Option<Instant>,
    /// Unique task identifier.
    pub id: String,
    /// Relative file path of the exported result (set on completion).
    pub result_path: Option<String>,
    /// Current stage name: "validating", "fetching", "exporting", "complete", or "error".
    pub stage: String,
    /// Zero-based index of the current stage (for progress bar percentage).
    pub stage_index: u8,
    /// Total number of stages (typically 4: validating, fetching, exporting, complete).
    pub stage_total: u8,
    /// Unix timestamp (seconds) when this task was created.
    pub started_at: f64,
    /// Task type: "batch" for standard scrapes, "livestream" for streaming scrapes.
    pub task_type: String,
    /// Display title (e.g. "r/rust — hot").
    pub title: String,
}

/// Shared application state passed to route handlers.
#[derive(Debug, Clone)]
pub struct AppState {
    /// Authenticated Reddit client for scraping (None = scraping disabled).
    pub client: Option<Arc<RedditClient>>,
    /// In-memory event buffers for active livestream tasks, keyed by task ID.
    pub livestream_events: Arc<DashMap<String, Vec<serde_json::Value>>>,
    /// Per-task cancellation tokens for stopping individual livestream tasks.
    pub livestream_tokens: Arc<DashMap<String, CancellationToken>>,
    /// Active and recently completed scrape tasks.
    pub scrape_tasks: Arc<DashMap<String, ScrapeTask>>,
    /// Root directory containing scraped data.
    pub scrapes_dir: Arc<PathBuf>,
    /// Token that signals server shutdown to long-lived connections (e.g. SSE streams).
    pub shutdown: CancellationToken,
    /// Reddit username of the authenticated account (None if no credentials).
    pub username: Option<Arc<str>>,
}

/// Starts the browse web server.
///
/// Binds to the configured address/port, optionally opens the browser, and runs until Ctrl+C
/// triggers graceful shutdown.
///
/// # Errors
///
/// Returns an error if binding fails or an I/O error occurs.
pub async fn run(config: ServerConfig) -> anyhow::Result<()> {
    tracing::info!(
        scrapes_dir = %config.scrapes_dir.display(),
        address = %config.address,
        port = config.port,
        open_browser = config.open_browser,
        "Starting browse server"
    );

    let scrape_enabled = config.client.is_some();

    tracing::info!(scrape_enabled, "Scrape capability status");

    // Fetch the authenticated username (reuses the same /api/v1/me pattern as `urs check`).
    let client = config.client.map(Arc::new);
    let username = if let Some(ref c) = client {
        let me_url =
            Url::parse("https://oauth.reddit.com/api/v1/me").expect("hardcoded URL is valid");

        match c.get(&me_url).await {
            Ok(me) => {
                let name = me.get("name").and_then(|v| v.as_str()).map(Arc::from);

                if let Some(ref n) = name {
                    tracing::info!(username = %n, "Authenticated as Reddit user");
                }

                name
            }
            Err(e) => {
                tracing::warn!(error = %e, "Failed to fetch Reddit username");
                None
            }
        }
    } else {
        None
    };

    let scrape_tasks = Arc::new(DashMap::new());
    let shutdown = CancellationToken::new();

    let state = AppState {
        client,
        livestream_events: Arc::new(DashMap::new()),
        livestream_tokens: Arc::new(DashMap::new()),
        scrape_tasks,
        scrapes_dir: Arc::new(config.scrapes_dir),
        shutdown: shutdown.clone(),
        username,
    };

    let app = Router::new().merge(routes::router()).with_state(state);

    let addr = format!("{}:{}", config.address, config.port);
    let listener = TcpListener::bind(&addr).await?;

    tracing::info!(address = %addr, "Browse server listening");

    if config.open_browser {
        let url = format!("http://{addr}");

        tokio::spawn(async move {
            // Add a small delay so the server is ready before browser hits it.
            tokio::time::sleep(std::time::Duration::from_millis(200)).await;

            if let Err(e) = open::that(&url) {
                tracing::warn!(error = %e, "Failed to open browser");
            }
        });
    }

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal(shutdown))
        .await?;

    tracing::info!("Browse server stopped");

    println!("\nServer stopped.");

    Ok(())
}

/// Waits for a Ctrl+C signal, then cancels the shutdown token to terminate long-lived connections
/// (e.g. SSE streams).
async fn shutdown_signal(token: CancellationToken) {
    signal::ctrl_c()
        .await
        .expect("Failed to install Ctrl+C handler");

    tracing::info!("Shutdown signal received");

    // Cancel long-lived connections so graceful shutdown can complete.
    token.cancel();
}
