//! Route handlers for the browse web server.
//!
//! Defines all HTTP endpoints: file browser, rich data viewer with per-item raw JSON toggle, CSV
//! table view, analytics exports, and static asset serving.

use std::fmt::Write as _;
use std::path::PathBuf;

use axum::Router;
use axum::extract::{Path as AxumPath, Query, State};
use axum::http::{HeaderMap, StatusCode, header};
use axum::response::{Html, IntoResponse, Response};
use axum::routing::{get, post};
use image::ImageFormat;
use serde::Deserialize;
use urs_core::analytics::{ColorScheme, WordCloudGenerator, WordFrequencyAnalyzer};

use super::csv;
use super::helpers::{
    build_breadcrumbs, error_html, error_response, into_html_response, wrap_in_shell,
};
use super::loader::{self, ScrapeType};
use super::scrape;
use super::server::AppState;
use super::settings;
use super::templates::{IndexTemplate, TreeFragmentTemplate};
use super::views;
use crate::commands::analyze::analyze_scrape_data;

/// Embedded static assets.
const FAVICON_SVG: &str = include_str!("assets/favicon.svg");
const HTMX_JS: &str = include_str!("assets/htmx.min.js");
const SCRAPE_JS: &str = include_str!("assets/scrape.js");
const STYLE_CSS: &str = include_str!("assets/style.css");

/// Minimum word length for analytics in the browse view.
const MIN_WORD_LENGTH: usize = 3;

/// Creates the application router with all routes.
pub fn router() -> Router<AppState> {
    Router::new()
        .route("/", get(index))
        .route("/analytics/{*path}", get(analytics))
        .route(
            "/api/analytics/frequencies/{*path}",
            get(analytics_frequencies),
        )
        .route("/api/analytics/wordcloud/{*path}", get(analytics_wordcloud))
        .route("/api/tree", get(tree_fragment))
        .route("/scrape", get(scrape::scrape_form))
        .route("/scrape/subreddit", post(scrape::scrape_subreddit))
        .route("/scrape/comments", post(scrape::scrape_comments))
        .route("/scrape/redditor", post(scrape::scrape_redditor))
        .route("/scrape/progress", get(scrape::scrape_progress_sse))
        .route("/scrape/livestream", post(scrape::scrape_livestream))
        .route(
            "/scrape/livestream/stop/{id}",
            post(scrape::stop_livestream),
        )
        .route(
            "/scrape/livestream/events/{id}",
            get(scrape::livestream_events_sse),
        )
        .route(
            "/scrape/livestream/live/{id}",
            get(scrape::livestream_live_view),
        )
        .route("/api/ratelimit/refresh", post(scrape::refresh_rate_limit))
        .route("/settings", get(settings::settings_page))
        .route("/settings/credentials", post(settings::save_credentials))
        .route(
            "/settings/credentials/test",
            post(settings::test_credentials),
        )
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
    /// Sort column for CSV views.
    pub sort: Option<String>,
    /// Tab name for Redditor views.
    pub tab: Option<String>,
}

/// Query parameters for word cloud image download.
#[derive(Debug, Deserialize)]
struct WordcloudQuery {
    /// Color scheme slug (e.g. "rainbow", "ocean").
    color: Option<String>,
    /// Image height in pixels.
    height: Option<usize>,
    /// Image width in pixels.
    width: Option<usize>,
}

/// Query parameters for frequency table export.
#[derive(Debug, Deserialize)]
struct FrequenciesQuery {
    /// Export format: "csv" or "json".
    format: Option<String>,
}

/// Result of validating an analytics file path.
struct ValidatedAnalyticsFile {
    /// The resolved full path on disk.
    full_path: PathBuf,
    /// The detected scrape type.
    scrape_type: ScrapeType,
}

/// Validates a file path for analytics operations.
///
/// Checks that the file exists, is within the scrapes directory, and is a supported type for
/// analytics (not CSV or livestream).
fn validate_analytics_path(
    file_path: &str,
    state: &AppState,
) -> Result<ValidatedAnalyticsFile, (StatusCode, String)> {
    let full_path = state.scrapes_dir.join(file_path);

    if !full_path.exists() {
        return Err((
            StatusCode::NOT_FOUND,
            format!("File not found: {file_path}"),
        ));
    }

    match full_path.canonicalize() {
        Ok(canonical) => {
            let scrapes_canonical = state.scrapes_dir.canonicalize().unwrap_or_default();
            if !canonical.starts_with(&scrapes_canonical) {
                tracing::warn!(path = %file_path, "Path traversal attempt blocked");
                return Err((StatusCode::FORBIDDEN, "Access denied".to_string()));
            }
        }
        Err(_) => {
            return Err((
                StatusCode::NOT_FOUND,
                format!("File not found: {file_path}"),
            ));
        }
    }

    let scrape_type = loader::detect_type(&full_path);

    if matches!(scrape_type, ScrapeType::Csv | ScrapeType::Livestream) {
        return Err((
            StatusCode::BAD_REQUEST,
            "Word frequency analysis is not available for CSV or livestream files".to_string(),
        ));
    }

    Ok(ValidatedAnalyticsFile {
        full_path,
        scrape_type,
    })
}

/// Word frequency analytics view for a scrape file.
async fn analytics(
    State(state): State<AppState>,
    headers: HeaderMap,
    AxumPath(file_path): AxumPath<String>,
) -> Response {
    let is_htmx = headers.contains_key("hx-request");

    tracing::info!(path = %file_path, htmx = is_htmx, "GET /analytics — analyzing file");

    let scrape_enabled = state.client.read().await.is_some();
    let username_lock = state.username.read().await;
    let username = username_lock.as_deref().map(String::from);
    drop(username_lock);

    let validated = match validate_analytics_path(&file_path, &state) {
        Ok(v) => v,
        Err((status, msg)) => {
            if status == StatusCode::NOT_FOUND {
                tracing::warn!(path = %file_path, "File not found");
            }
            return error_response(
                status.as_u16(),
                &msg,
                is_htmx,
                &state.scrapes_dir,
                scrape_enabled,
                username.as_deref(),
            );
        }
    };

    let breadcrumbs = build_breadcrumbs(&file_path);

    let content_html = match loader::parse_file(&validated.full_path, validated.scrape_type) {
        Ok(data) => views::analytics::render_analytics_html(&data, &file_path, breadcrumbs),
        Err(e) => {
            tracing::error!(path = %file_path, error = %e, "Failed to parse file for analytics");
            error_html(500, &format!("Failed to parse file: {e}"))
        }
    };

    if is_htmx {
        Html(content_html).into_response()
    } else {
        tracing::debug!(path = %file_path, "Wrapping analytics in shell for direct access");
        wrap_in_shell(
            &state.scrapes_dir,
            scrape_enabled,
            username.as_deref(),
            &content_html,
            StatusCode::OK,
        )
    }
}

/// Download word cloud image with customizable appearance.
async fn analytics_wordcloud(
    State(state): State<AppState>,
    AxumPath(file_path): AxumPath<String>,
    Query(query): Query<WordcloudQuery>,
) -> Response {
    tracing::info!(path = %file_path, "GET /analytics/.../wordcloud — generating image");

    let validated = match validate_analytics_path(&file_path, &state) {
        Ok(v) => v,
        Err((status, msg)) => return (status, msg).into_response(),
    };

    let data = match loader::parse_file(&validated.full_path, validated.scrape_type) {
        Ok(d) => d,
        Err(e) => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("Failed to parse file: {e}"),
            )
                .into_response();
        }
    };

    let analyzer = WordFrequencyAnalyzer::new().min_word_length(MIN_WORD_LENGTH);
    let frequencies = analyze_scrape_data(&analyzer, &data);

    if frequencies.unique_count() == 0 {
        return (StatusCode::NOT_FOUND, "No words found in this file").into_response();
    }

    let color_scheme = query
        .color
        .as_deref()
        .map_or_else(ColorScheme::default, ColorScheme::from_slug);
    let width = query.width.unwrap_or(2048);
    let height = query.height.unwrap_or(1024);

    let generator = WordCloudGenerator::new()
        .dimensions(width, height)
        .color_scheme(color_scheme);
    let image = generator.generate(&frequencies);

    let mut buffer = std::io::Cursor::new(Vec::new());
    if let Err(e) = image.write_to(&mut buffer, ImageFormat::Png) {
        tracing::error!(error = %e, "Failed to encode word cloud image");
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Failed to encode image: {e}"),
        )
            .into_response();
    }

    let stem = std::path::Path::new(&file_path)
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("wordcloud");
    let filename = format!("{stem}-wordcloud.png");

    (
        StatusCode::OK,
        [
            (header::CONTENT_TYPE, "image/png".to_string()),
            (
                header::CONTENT_DISPOSITION,
                format!("attachment; filename=\"{filename}\""),
            ),
        ],
        buffer.into_inner(),
    )
        .into_response()
}

/// Download word frequency table as CSV or JSON.
async fn analytics_frequencies(
    State(state): State<AppState>,
    AxumPath(file_path): AxumPath<String>,
    Query(query): Query<FrequenciesQuery>,
) -> Response {
    tracing::info!(path = %file_path, "GET /analytics/.../frequencies — exporting frequencies");

    let validated = match validate_analytics_path(&file_path, &state) {
        Ok(v) => v,
        Err((status, msg)) => return (status, msg).into_response(),
    };

    let data = match loader::parse_file(&validated.full_path, validated.scrape_type) {
        Ok(d) => d,
        Err(e) => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("Failed to parse file: {e}"),
            )
                .into_response();
        }
    };

    let analyzer = WordFrequencyAnalyzer::new().min_word_length(MIN_WORD_LENGTH);
    let frequencies = analyze_scrape_data(&analyzer, &data);

    let stem = std::path::Path::new(&file_path)
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("frequencies");

    if query.format.as_deref() == Some("json") {
        let map: serde_json::Map<String, serde_json::Value> = frequencies
            .entries()
            .iter()
            .map(|(word, count)| (word.clone(), serde_json::Value::from(*count)))
            .collect();

        let body = match serde_json::to_string_pretty(&map) {
            Ok(json) => json,
            Err(e) => {
                return (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    format!("Failed to serialize: {e}"),
                )
                    .into_response();
            }
        };

        let filename = format!("{stem}-frequencies.json");
        (
            StatusCode::OK,
            [
                (header::CONTENT_TYPE, "application/json".to_string()),
                (
                    header::CONTENT_DISPOSITION,
                    format!("attachment; filename=\"{filename}\""),
                ),
            ],
            body,
        )
            .into_response()
    } else {
        let mut csv_buf = String::from("word,count\n");

        for (word, count) in frequencies.entries() {
            // Escape words containing commas or quotes for CSV.
            if word.contains(',') || word.contains('"') {
                let escaped = word.replace('"', "\"\"");
                writeln!(csv_buf, "\"{escaped}\",{count}")
                    .expect("writing to String is infallible");
            } else {
                writeln!(csv_buf, "{word},{count}").expect("writing to String is infallible");
            }
        }

        let filename = format!("{stem}-frequencies.csv");
        (
            StatusCode::OK,
            [
                (header::CONTENT_TYPE, "text/csv".to_string()),
                (
                    header::CONTENT_DISPOSITION,
                    format!("attachment; filename=\"{filename}\""),
                ),
            ],
            csv_buf,
        )
            .into_response()
    }
}

/// Landing page including the file browser tree and file view.
async fn index(State(state): State<AppState>) -> Response {
    tracing::debug!("GET / — loading landing page");

    let scrape_enabled = state.client.read().await.is_some();
    let username_lock = state.username.read().await;
    let username = username_lock.as_deref().map(String::from);

    drop(username_lock);

    match loader::scan_directory(&state.scrapes_dir, "") {
        Ok(entries) => {
            tracing::debug!(count = entries.len(), "Loaded top-level entries");

            let template = IndexTemplate {
                entries,
                scrape_enabled,
                username,
            };
            into_html_response(template)
        }
        Err(e) => {
            tracing::error!(error = %e, "Failed to scan scrapes directory");

            let html = error_html(500, &format!("Failed to scan directory: {e}"));

            wrap_in_shell(
                &state.scrapes_dir,
                scrape_enabled,
                username.as_deref(),
                &html,
                StatusCode::INTERNAL_SERVER_ERROR,
            )
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

    let scrape_enabled = state.client.read().await.is_some();
    let username_lock = state.username.read().await;
    let username = username_lock.as_deref().map(String::from);

    drop(username_lock);

    if !full_path.exists() {
        tracing::warn!(path = %file_path, "File not found");

        return error_response(
            404,
            &format!("File not found: {file_path}"),
            is_htmx,
            &state.scrapes_dir,
            scrape_enabled,
            username.as_deref(),
        );
    }

    // Ensure path stays within scrapes_dir.
    match full_path.canonicalize() {
        Ok(canonical) => {
            let scrapes_canonical = state.scrapes_dir.canonicalize().unwrap_or_default();
            if !canonical.starts_with(&scrapes_canonical) {
                tracing::warn!(path = %file_path, "Path traversal attempt blocked");
                return error_response(
                    403,
                    "Access denied",
                    is_htmx,
                    &state.scrapes_dir,
                    scrape_enabled,
                    username.as_deref(),
                );
            }
        }
        Err(_) => {
            return error_response(
                404,
                "File not found",
                is_htmx,
                &state.scrapes_dir,
                scrape_enabled,
                username.as_deref(),
            );
        }
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
        wrap_in_shell(
            &state.scrapes_dir,
            scrape_enabled,
            username.as_deref(),
            &content_html,
            StatusCode::OK,
        )
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
        "favicon.svg" => (
            StatusCode::OK,
            [(header::CONTENT_TYPE, "image/svg+xml")],
            FAVICON_SVG,
        )
            .into_response(),
        "htmx.min.js" => (
            StatusCode::OK,
            [(header::CONTENT_TYPE, "application/javascript")],
            HTMX_JS,
        )
            .into_response(),
        "scrape.js" => (
            StatusCode::OK,
            [(header::CONTENT_TYPE, "application/javascript")],
            SCRAPE_JS,
        )
            .into_response(),
        "style.css" => (
            StatusCode::OK,
            [(header::CONTENT_TYPE, "text/css")],
            STYLE_CSS,
        )
            .into_response(),
        _ => (StatusCode::NOT_FOUND, "Not found").into_response(),
    }
}
