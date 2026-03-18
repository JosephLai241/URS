//! Axum web server setup, binding, and graceful shutdown.
//!
//! Configures the HTTP router, binds to the specified address/port, and handles graceful shutdown
//! on Ctrl+C.

use std::path::PathBuf;
use std::sync::Arc;

use axum::Router;
use tokio::net::TcpListener;
use tokio::signal;

use super::routes;

/// Server configuration.
pub struct ServerConfig {
    /// Bind address (e.g. "127.0.0.1").
    pub address: String,
    /// Whether to open the browser automatically.
    pub open_browser: bool,
    /// Bind port (e.g. 8080).
    pub port: u16,
    /// Root directory containing scraped data.
    pub scrapes_dir: PathBuf,
}

/// Shared application state passed to route handlers.
#[derive(Debug, Clone)]
pub struct AppState {
    /// Root directory containing scraped data.
    pub scrapes_dir: Arc<PathBuf>,
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

    let state = AppState {
        scrapes_dir: Arc::new(config.scrapes_dir),
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
        .with_graceful_shutdown(shutdown_signal())
        .await?;

    tracing::info!("Browse server stopped");

    println!("\nServer stopped.");

    Ok(())
}

/// Waits for a Ctrl+C signal.
async fn shutdown_signal() {
    signal::ctrl_c()
        .await
        .expect("Failed to install Ctrl+C handler");

    tracing::info!("Shutdown signal received");
}
