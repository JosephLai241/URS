//! Livestream feed rendering.
//!
//! Renders a chronological feed of livestream events with timestamps, author info, event type
//! icons, and per-event JSON inspector buttons.

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

    let template = LivestreamFragment {
        breadcrumbs,
        event_count: event_views.len(),
        events: event_views,
        source,
        target,
    };

    render_template(template)
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
