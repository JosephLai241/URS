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

            let icon = if e.event_type == "submission" {
                "&#x1F4DD;"
            } else {
                "&#x1F4AC;"
            };

            LivestreamEventView {
                author,
                body_html: markdown::render_comment(body, body_html_raw),
                icon: icon.to_string(),
                json_html: highlight_json(&e.data),
                subreddit,
                time_str: time::time_only(created_utc),
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
