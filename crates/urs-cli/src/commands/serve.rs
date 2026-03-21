//! Serve command — start the URS REST API server.
//!
//! This command authenticates with Reddit, builds the API router from `urs-api`, and starts an HTTP
//! server that exposes scraping functionality via REST endpoints.

use clap::Args;
use colored::Colorize;

use crate::config;
use crate::helpers;

/// Arguments for the `serve` command.
#[derive(Debug, Args)]
#[command(after_long_help = "\
\x1b[1;4mExamples:\x1b[0m

  Start the API server with defaults:
    urs serve

  Use a custom port:
    urs serve --port 8080

  Bind to all interfaces (e.g. for remote access):
    urs serve --address 0.0.0.0

  Generate an API token first, then serve:
    urs config generate-api-token
    urs serve

\x1b[1;4mAuthentication:\x1b[0m

  Generate an API token to require bearer token authentication on all
  endpoints (except /api/health):

    urs config generate-api-token

  Or set an API token via config or environment variable:

    urs config set api.token <TOKEN>
    URS_API_TOKEN=<TOKEN> urs serve

\x1b[1;4mEndpoints:\x1b[0m

  GET /api/health                              Health check + rate limits
  GET /api/subreddits/{name}                   Subreddit info
  GET /api/subreddits/{name}/hot               Hot posts
  GET /api/subreddits/{name}/new               New posts
  GET /api/subreddits/{name}/top               Top posts (?time=week&limit=50)
  GET /api/subreddits/{name}/controversial     Controversial posts
  GET /api/subreddits/{name}/rising            Rising posts
  GET /api/subreddits/{name}/search            Search (?q=rust&limit=50)
  GET /api/subreddits/{name}/rules             Subreddit rules
  GET /api/redditors/{username}                Redditor profile
  GET /api/redditors/{username}/submissions    Submissions
  GET /api/redditors/{username}/comments       Comments
  GET /api/redditors/{username}/interactions   All interactions
  GET /api/comments?url=<reddit_url>           Comments by URL
  GET /api/comments/{subreddit}/{id}           Comments by ID
  GET /api/livestream/subreddits/{name}        Livestream (SSE)
  GET /api/livestream/redditors/{username}     Livestream (SSE)")]
pub struct ServeArgs {
    /// Address to bind the API server on.
    #[arg(short, long)]
    pub address: Option<String>,

    /// Port to bind the API server on.
    #[arg(short, long)]
    pub port: Option<u16>,
}

/// Runs the serve command.
///
/// Authenticates with Reddit, resolves the API token, and starts the HTTP server.
///
/// # Errors
///
/// Returns an error if authentication fails or the server cannot bind.
pub async fn run(args: ServeArgs) -> anyhow::Result<()> {
    let cfg = config::load_config().unwrap_or_default();

    let address = args.address.unwrap_or(cfg.api.address);
    let port = args.port.unwrap_or(cfg.api.port);
    let api_token = helpers::resolve_api_token();

    let client = helpers::create_client().await?;
    let app = urs_api::build_router(client, api_token.clone());

    let bind_addr = format!("{address}:{port}");
    let listener = tokio::net::TcpListener::bind(&bind_addr).await?;

    println!(
        "{} API server listening at {}",
        "▸".cyan(),
        format!("http://{bind_addr}").bold().underline()
    );

    if api_token.is_some() {
        println!(
            "  {} {}",
            "Authentication:".dimmed(),
            "enabled (bearer token)".bright_green()
        );
    } else {
        println!(
            "  {} {}",
            "Authentication:".dimmed(),
            "disabled (open access)".bright_yellow()
        );
    }

    println!("  {} Ctrl+C to stop\n", "Tip:".dimmed());

    tracing::info!(
        address = %address,
        port = port,
        auth = api_token.is_some(),
        "Starting API server"
    );

    axum::serve(listener, app).await?;

    Ok(())
}
