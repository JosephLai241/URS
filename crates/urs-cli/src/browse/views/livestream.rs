//! Livestream feed rendering.
//!
//! Renders a chronological feed of livestream events with timestamps, author info, event type
//! icons, and per-event JSON inspector buttons.

use std::fmt::Write as _;

use super::super::helpers::render_template;
use super::super::loader::LivestreamEvent;
use super::super::markdown;
use super::super::templates::{BreadcrumbItem, LivestreamFragment};
use super::super::time;
use super::{LivestreamEventView, highlight_json};

/// SVG icon for submission events (document/post icon).
const SUBMISSION_ICON: &str = r#"<svg class="event-type-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M2 1a1 1 0 0 1 1-1h6l5 5v10a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V1zm1 0v14h10V6h-4a1 1 0 0 1-1-1V1H3z"/></svg>"#;

/// SVG icon for comment events (speech bubble icon).
const COMMENT_ICON: &str = r#"<svg class="event-type-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M1 2.5A1.5 1.5 0 0 1 2.5 1h11A1.5 1.5 0 0 1 15 2.5v8A1.5 1.5 0 0 1 13.5 12H5l-4 3V2.5zM2.5 2a.5.5 0 0 0-.5.5v9.793l2.146-2.147A.5.5 0 0 1 4.5 10h9a.5.5 0 0 0 .5-.5v-7a.5.5 0 0 0-.5-.5h-11z"/></svg>"#;

/// Renders the livestream feed view to an HTML string.
pub fn render_livestream_html(
    events: &[LivestreamEvent],
    file_path: &str,
    breadcrumbs: Vec<BreadcrumbItem>,
) -> String {
    let (target, source) = parse_livestream_filename(file_path);

    let event_views: Vec<LivestreamEventView> = events
        .iter()
        .map(|e| {
            let author = e
                .data
                .get("author")
                .and_then(|v| v.as_str())
                .unwrap_or("unknown")
                .to_string();
            let subreddit = e
                .data
                .get("subreddit")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let created_utc = e
                .data
                .get("created_utc")
                .and_then(serde_json::Value::as_f64)
                .unwrap_or(0.0);
            let body = e.data.get("body").and_then(|v| v.as_str()).unwrap_or("");
            let body_html_raw = e
                .data
                .get("body_html")
                .and_then(|v| v.as_str())
                .unwrap_or("");
            let title = e
                .data
                .get("title")
                .and_then(|v| v.as_str())
                .map(String::from);
            let permalink = e
                .data
                .get("permalink")
                .and_then(|v| v.as_str())
                .map(|p| format!("https://www.reddit.com{p}"));

            let icon = if e.event_type == "submission" {
                SUBMISSION_ICON
            } else {
                COMMENT_ICON
            };

            LivestreamEventView {
                author,
                body_html: markdown::render_comment(body, body_html_raw),
                icon: icon.to_string(),
                json_html: highlight_json(&e.data),
                permalink,
                subreddit,
                time_str: time::time_only(created_utc),
                time_utc: created_utc,
                title,
            }
        })
        .collect();

    // Compute start/end timestamps and duration from events.
    let first_utc = event_views.first().map_or(0.0, |e| e.time_utc);
    let last_utc = event_views.last().map_or(0.0, |e| e.time_utc);

    #[allow(clippy::cast_sign_loss, clippy::cast_possible_truncation)]
    let duration_secs = if last_utc > first_utc {
        (last_utc - first_utc) as u64
    } else {
        0
    };

    let hours = duration_secs / 3600;
    let minutes = (duration_secs % 3600) / 60;
    let secs = duration_secs % 60;

    let template = LivestreamFragment {
        breadcrumbs,
        duration: format!("{hours:02}:{minutes:02}:{secs:02}"),
        event_count: event_views.len(),
        events: event_views,
        first_event_time: if first_utc > 0.0 {
            time::absolute_time(first_utc)
        } else {
            String::new()
        },
        last_event_time: if last_utc > 0.0 {
            time::absolute_time(last_utc)
        } else {
            String::new()
        },
        source,
        target,
    };

    render_template(template)
}

/// Renders a single livestream event as an HTML fragment for the live SSE stream.
///
/// Returns the inner `.livestream-event` div HTML string. Reuses the same view construction logic
/// as `render_livestream_html`.
pub fn render_single_event_html(data: &serde_json::Value, event_type: &str) -> String {
    let author = data
        .get("author")
        .and_then(|v| v.as_str())
        .unwrap_or("unknown");
    let subreddit = data.get("subreddit").and_then(|v| v.as_str()).unwrap_or("");
    let created_utc = data
        .get("created_utc")
        .and_then(serde_json::Value::as_f64)
        .unwrap_or(0.0);
    let body = data.get("body").and_then(|v| v.as_str()).unwrap_or("");
    let body_html_raw = data.get("body_html").and_then(|v| v.as_str()).unwrap_or("");
    let title = data.get("title").and_then(|v| v.as_str()).map(String::from);
    let permalink = data
        .get("permalink")
        .and_then(|v| v.as_str())
        .map(|p| format!("https://www.reddit.com{p}"));

    let icon = if event_type == "submission" {
        SUBMISSION_ICON
    } else {
        COMMENT_ICON
    };

    let body_html = markdown::render_comment(body, body_html_raw);
    let json_html = highlight_json(data);
    let time_str = time::time_only(created_utc);

    let mut html = String::new();
    html.push_str("<div class=\"livestream-event\">");
    write!(html, "<span class=\"event-icon\">{icon}</span>")
        .expect("writing to String is infallible");
    html.push_str("<div class=\"event-content\">");
    html.push_str("<div class=\"event-header\">");
    write!(
        html,
        "<span class=\"event-time\" data-utc=\"{created_utc}\">{time_str}</span>"
    )
    .expect("writing to String is infallible");
    write!(html, "<span class=\"comment-author\">u/{author}</span>")
        .expect("writing to String is infallible");

    if !subreddit.is_empty() {
        write!(
            html,
            "<span class=\"text-muted\">&middot; r/{subreddit}</span>"
        )
        .expect("writing to String is infallible");
    }

    html.push_str(
        "<button class=\"item-json-btn\" onclick=\"toggleItemJson(this)\">{} Show JSON</button>",
    );
    write!(
        html,
        "<template class=\"item-json-data\"><div class=\"item-json-content\"><pre>{json_html}</pre></div></template>"
    )
    .expect("writing to String is infallible");

    html.push_str("</div>"); // Close event-header.

    if let Some(ref t) = title {
        if let Some(ref href) = permalink {
            write!(
                html,
                "<div class=\"submission-title\" style=\"margin-bottom: 4px\"><a href=\"{href}\" target=\"_blank\" rel=\"noopener\">{t}</a></div>"
            )
            .expect("writing to String is infallible");
        } else {
            write!(
                html,
                "<div class=\"submission-title\" style=\"margin-bottom: 4px\">{t}</div>"
            )
            .expect("writing to String is infallible");
        }
    }

    write!(html, "<div class=\"event-body\">{body_html}</div>")
        .expect("writing to String is infallible");
    html.push_str("</div>"); // Close event-content.
    html.push_str("</div>"); // Close livestream-event.

    html
}

/// Parses livestream filename to extract target and source.
///
/// Format: `{target}-{source}-{count}-livestream.jsonl`
fn parse_livestream_filename(file_path: &str) -> (String, String) {
    let filename = file_path
        .split('/')
        .next_back()
        .unwrap_or(file_path)
        .trim_end_matches(".jsonl");

    let parts: Vec<&str> = filename.split('-').collect();
    if parts.len() >= 2 {
        (parts[0].to_string(), parts[1].to_string())
    } else {
        (filename.to_string(), "unknown".to_string())
    }
}
