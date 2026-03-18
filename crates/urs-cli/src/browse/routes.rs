//! Route handlers for the browse web server.
//!
//! Defines all HTTP endpoints: file browser, rich data viewer with per-item raw JSON toggle, CSV
//! table view and static asset serving.

use axum::Router;
use axum::extract::{Path as AxumPath, Query, State};
use axum::http::{HeaderMap, StatusCode, header};
use axum::response::{Html, IntoResponse, Response};
use axum::routing::get;
use serde::Deserialize;

use super::csv;
use super::helpers::{
    build_breadcrumbs, error_html, error_response, into_html_response, wrap_in_shell,
};
use super::loader::{self, ScrapeType};
use super::server::AppState;
use super::templates::{IndexTemplate, TreeFragmentTemplate};
use super::views;

/// Embedded static assets.
const STYLE_CSS: &str = include_str!("assets/style.css");
const HTMX_JS: &str = include_str!("assets/htmx.min.js");

/// Creates the application router with all routes.
pub fn router() -> Router<AppState> {
    Router::new()
        .route("/", get(index))
        .route("/api/tree", get(tree_fragment))
        .route("/view/{*path}", get(view_file))
        .route("/raw/{*path}", get(raw_file))
        .route("/assets/{*path}", get(serve_asset))
}

/// Query parameters for tree fragment requests.
#[derive(Debug, Deserialize)]
struct TreeQuery {
    /// Relative path to expand.
    path: Option<String>,
}

/// Query parameters for file view requests.
#[derive(Debug, Deserialize)]
pub struct ViewQuery {
    /// Sort direction: "asc" or "desc".
    pub dir: Option<String>,
    /// Filter text for CSV views.
    pub filter: Option<String>,
    /// Sort column for CSV views.
    pub sort: Option<String>,
    /// Tab name for Redditor views.
    pub tab: Option<String>,
}

/// Landing page — file browser.
async fn index(State(state): State<AppState>) -> Response {
    tracing::debug!("GET / — loading landing page");

    match loader::scan_directory(&state.scrapes_dir, "") {
        Ok(entries) => {
            tracing::debug!(count = entries.len(), "Loaded top-level entries");

            let template = IndexTemplate { entries };
            into_html_response(template)
        }
        Err(e) => {
            tracing::error!(error = %e, "Failed to scan scrapes directory");

            let html = error_html(500, &format!("Failed to scan directory: {e}"));
            wrap_in_shell(&state, &html, StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// HTMX partial: expand directory subtree.
async fn tree_fragment(
    State(state): State<AppState>,
    Query(query): Query<TreeQuery>,
) -> impl IntoResponse {
    let path = query.path.unwrap_or_default();

    tracing::debug!(path = %path, "GET /api/tree — expanding directory");

    match loader::scan_directory(&state.scrapes_dir, &path) {
        Ok(entries) => {
            tracing::debug!(path = %path, count = entries.len(), "Directory expanded");

            let template = TreeFragmentTemplate { entries };
            into_html_response(template)
        }
        Err(e) => {
            tracing::error!(path = %path, error = %e, "Failed to expand directory");

            Html(error_html(500, &format!("Failed to expand directory: {e}"))).into_response()
        }
    }
}

/// View a scraped data file. Returns a fragment for HTMX or full page for direct access.
async fn view_file(
    State(state): State<AppState>,
    headers: HeaderMap,
    AxumPath(file_path): AxumPath<String>,
    Query(query): Query<ViewQuery>,
) -> Response {
    let full_path = state.scrapes_dir.join(&file_path);
    let is_htmx = headers.contains_key("hx-request");

    tracing::info!(
        path = %file_path,
        htmx = is_htmx,
        "GET /view — viewing file"
    );

    if !full_path.exists() {
        tracing::warn!(path = %file_path, "File not found");

        return error_response(
            404,
            &format!("File not found: {file_path}"),
            is_htmx,
            &state,
        );
    }

    // Ensure path stays within scrapes_dir.
    match full_path.canonicalize() {
        Ok(canonical) => {
            let scrapes_canonical = state.scrapes_dir.canonicalize().unwrap_or_default();
            if !canonical.starts_with(&scrapes_canonical) {
                tracing::warn!(path = %file_path, "Path traversal attempt blocked");
                return error_response(403, "Access denied", is_htmx, &state);
            }
        }
        Err(_) => return error_response(404, "File not found", is_htmx, &state),
    }

    let breadcrumbs = build_breadcrumbs(&file_path);
    let scrape_type = loader::detect_type(&full_path);

    tracing::debug!(path = %file_path, scrape_type = ?scrape_type, "Detected scrape type");

    let content_html = if scrape_type == ScrapeType::Csv {
        csv::render_csv_html(&full_path, &file_path, breadcrumbs, &query)
    } else {
        match loader::parse_file(&full_path, scrape_type) {
            Ok(data) => views::render_rich_html(data, &file_path, breadcrumbs, &query),
            Err(e) => {
                tracing::error!(path = %file_path, error = %e, "Failed to parse file");
                error_html(500, &format!("Failed to parse file: {e}"))
            }
        }
    };

    if is_htmx {
        Html(content_html).into_response()
    } else {
        tracing::debug!(path = %file_path, "Wrapping in shell for direct access");
        wrap_in_shell(&state, &content_html, StatusCode::OK)
    }
}

/// Serve raw file content for download.
async fn raw_file(
    State(state): State<AppState>,
    AxumPath(file_path): AxumPath<String>,
) -> Response {
    let full_path = state.scrapes_dir.join(&file_path);

    tracing::debug!(path = %file_path, "GET /raw — serving raw file");

    if !full_path.exists() {
        tracing::warn!(path = %file_path, "Raw file not found");

        return (
            StatusCode::NOT_FOUND,
            format!("File not found: {file_path}"),
        )
            .into_response();
    }

    match std::fs::read(&full_path) {
        Ok(contents) => {
            let mime = mime_guess::from_path(&full_path)
                .first_or_octet_stream()
                .to_string();

            let filename = full_path
                .file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("download");

            (
                StatusCode::OK,
                [
                    (header::CONTENT_TYPE, mime),
                    (
                        header::CONTENT_DISPOSITION,
                        format!("attachment; filename=\"{filename}\""),
                    ),
                ],
                contents,
            )
                .into_response()
        }
        Err(e) => {
            tracing::error!(path = %file_path, error = %e, "Failed to read raw file");

            (
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("Failed to read file: {e}"),
            )
                .into_response()
        }
    }
}

/// Serve embedded static assets.
async fn serve_asset(AxumPath(path): AxumPath<String>) -> Response {
    match path.as_str() {
        "style.css" => (
            StatusCode::OK,
            [(header::CONTENT_TYPE, "text/css")],
            STYLE_CSS,
        )
            .into_response(),
        "htmx.min.js" => (
            StatusCode::OK,
            [(header::CONTENT_TYPE, "application/javascript")],
            HTMX_JS,
        )
            .into_response(),
        _ => (StatusCode::NOT_FOUND, "Not found").into_response(),
    }
}
