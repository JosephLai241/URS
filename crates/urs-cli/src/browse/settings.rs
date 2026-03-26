//! Settings page handlers for the browse web server.
//!
//! Provides the settings page route, credential save/test handlers, and hot-reload of the Reddit
//! client after credentials are updated.

use std::sync::Arc;

use axum::extract::{Form, State};
use axum::http::{HeaderMap, StatusCode};
use axum::response::{Html, IntoResponse, Json, Response};
use serde::Deserialize;
use url::Url;
use urs_core::auth::Credentials;
use urs_core::client::RedditClient;

use super::helpers::{render_template, wrap_in_shell};
use super::server::AppState;
use super::templates::SettingsFragment;
use crate::config;

/// Form parameters for credential save/test operations.
#[derive(Debug, Deserialize)]
pub struct CredentialParams {
    /// The `OAuth2` client ID.
    pub client_id: Option<String>,
    /// The `OAuth2` client secret.
    pub client_secret: Option<String>,
    /// The Reddit account password.
    pub password: Option<String>,
    /// The Reddit account username.
    pub username: Option<String>,
}

/// GET handler for the settings page.
pub async fn settings_page(State(state): State<AppState>, headers: HeaderMap) -> Response {
    let is_htmx = headers.contains_key("hx-request");

    let scrape_enabled = state.client.read().await.is_some();
    let username_lock = state.username.read().await;
    let current_username = username_lock
        .as_deref()
        .map(String::from)
        .unwrap_or_default();
    let username_for_shell = username_lock.as_deref().map(String::from);

    drop(username_lock);

    let cfg = config::load_config().unwrap_or_default();

    let template = SettingsFragment {
        authenticated: scrape_enabled,
        client_id: cfg.credentials.client_id.unwrap_or_default(),
        client_secret: cfg.credentials.client_secret.unwrap_or_default(),
        config_path: config::config_path().display().to_string(),
        config_username: cfg.credentials.username.unwrap_or_default(),
        current_username,
        password: cfg.credentials.password.unwrap_or_default(),
    };
    let html = render_template(template);

    if is_htmx {
        Html(html).into_response()
    } else {
        wrap_in_shell(
            &state.scrapes_dir,
            scrape_enabled,
            username_for_shell.as_deref(),
            &html,
            StatusCode::OK,
        )
    }
}

/// POST handler for saving credentials and authenticating.
///
/// Saves the provided credentials to the config file, then attempts to authenticate with the
/// Reddit API. On success, updates the in-memory client and username via `RwLock`. Returns an
/// `HX-Redirect` header to trigger a full page reload.
pub async fn save_credentials(
    State(state): State<AppState>,
    Form(params): Form<CredentialParams>,
) -> Response {
    // Load existing config so we can merge. Blank secret fields mean "keep existing".
    let mut cfg = config::load_config().unwrap_or_default();

    if let Some(ref id) = params.client_id {
        if !id.is_empty() {
            cfg.credentials.client_id = Some(id.clone());
        }
    }
    if let Some(ref secret) = params.client_secret {
        if !secret.is_empty() {
            cfg.credentials.client_secret = Some(secret.clone());
        }
    }
    if let Some(ref user) = params.username {
        if !user.is_empty() {
            cfg.credentials.username = Some(user.clone());
        }
    }
    if let Some(ref pass) = params.password {
        if !pass.is_empty() {
            cfg.credentials.password = Some(pass.clone());
        }
    }

    if let Err(e) = config::save_config(&cfg) {
        tracing::error!(error = %e, "Failed to save config");

        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            Html(format!(
                r#"<div class="settings-result error">Failed to save config: {e}</div>"#
            )),
        )
            .into_response();
    }

    tracing::info!("Credentials saved to config file");

    if !cfg.credentials.is_complete() {
        return Json(serde_json::json!({
            "success": false,
            "authenticated": false,
            "message": "Credentials saved (incomplete \u{2014} fill all fields to connect)"
        }))
        .into_response();
    }

    let credentials = build_credentials(&cfg.credentials);
    match RedditClient::new(credentials).await {
        Ok(client) => {
            let client = Arc::new(client);

            let username = fetch_username(&client).await;
            let username_str = username.as_deref().unwrap_or("unknown").to_string();

            // Hot-reload: swap in the new client.
            *state.client.write().await = Some(client);
            *state.username.write().await = username;

            tracing::info!("Credentials saved and authenticated successfully");

            Json(serde_json::json!({
                "success": true,
                "authenticated": true,
                "username": username_str,
                "message": format!("Connected as u/{username_str}")
            }))
            .into_response()
        }
        Err(e) => {
            tracing::warn!(error = %e, "Authentication failed after saving credentials");

            // Clear client since credentials are invalid.
            *state.client.write().await = None;
            *state.username.write().await = None;

            Json(serde_json::json!({
                "success": false,
                "authenticated": false,
                "message": format!("Credentials saved but authentication failed: {e}")
            }))
            .into_response()
        }
    }
}

/// POST handler for testing credentials without saving.
///
/// Attempts to authenticate with the provided credentials and returns a JSON result indicating
/// success or failure.
pub async fn test_credentials(Form(params): Form<CredentialParams>) -> Response {
    // Merge with existing config for blank fields.
    let cfg = config::load_config().unwrap_or_default();

    let client_id = non_empty_or(params.client_id, cfg.credentials.client_id);
    let client_secret = non_empty_or(params.client_secret, cfg.credentials.client_secret);
    let username = non_empty_or(params.username, cfg.credentials.username);
    let password = non_empty_or(params.password, cfg.credentials.password);

    let (Some(client_id), Some(client_secret), Some(username), Some(password)) =
        (client_id, client_secret, username, password)
    else {
        return Json(serde_json::json!({
            "success": false,
            "message": "All four credential fields are required"
        }))
        .into_response();
    };

    let user_agent = format!(
        "{}:com.{username}.urs:v{} (by /u/{username})",
        std::env::consts::OS,
        env!("CARGO_PKG_VERSION"),
    );

    let credentials = Credentials::new(client_id, client_secret, username, password, user_agent);

    match RedditClient::new(credentials).await {
        Ok(_) => Json(serde_json::json!({
            "success": true,
            "message": "Authentication successful"
        }))
        .into_response(),
        Err(e) => Json(serde_json::json!({
            "success": false,
            "message": format!("Authentication failed: {e}")
        }))
        .into_response(),
    }
}

/// Builds `Credentials` from a complete `CredentialsConfig`.
fn build_credentials(creds: &config::CredentialsConfig) -> Credentials {
    let username = creds.username.as_deref().unwrap_or_default();

    let user_agent = format!(
        "{}:com.{username}.urs:v{} (by /u/{username})",
        std::env::consts::OS,
        env!("CARGO_PKG_VERSION"),
    );

    Credentials::new(
        creds.client_id.as_deref().unwrap_or_default(),
        creds.client_secret.as_deref().unwrap_or_default(),
        username,
        creds.password.as_deref().unwrap_or_default(),
        user_agent,
    )
}

/// Fetches the authenticated Reddit username via `/api/v1/me`.
async fn fetch_username(client: &RedditClient) -> Option<Arc<str>> {
    let me_url = Url::parse("https://oauth.reddit.com/api/v1/me").expect("hardcoded URL is valid");

    match client.get(&me_url).await {
        Ok(me) => me.get("name").and_then(|v| v.as_str()).map(Arc::from),
        Err(e) => {
            tracing::warn!(error = %e, "Failed to fetch Reddit username");
            None
        }
    }
}

/// Returns the first non-empty `Option<String>`, falling back to the second.
fn non_empty_or(primary: Option<String>, fallback: Option<String>) -> Option<String> {
    match primary {
        Some(ref s) if !s.is_empty() => primary,
        _ => fallback,
    }
}
