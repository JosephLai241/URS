//! Rich view rendering for scraped Reddit data.
//!
//! Converts parsed scrape data into HTML fragments for submissions, comments, Redditor profiles,
//! and livestream feeds. Each view mimics the Reddit UI with vote arrows, badges, nested comment
//! threads, and tabbed profiles.
//!
//! Submodules handle each view type:
//! - [`comments`]: Nested comment thread rendering
//! - [`livestream`]: Chronological event feed
//! - [`redditor`]: Tabbed Redditor profile

mod comments;
mod livestream;
mod redditor;

use super::helpers::{render_template, syntax_highlight_json};
use super::loader::ScrapeData;
use super::markdown;
use super::routes::ViewQuery;
use super::templates::{BreadcrumbItem, ErrorFragment, SubmissionsFragment};
use super::time;

/// View model for a submission card.
#[derive(Debug, Clone)]
#[allow(clippy::struct_excessive_bools)]
pub struct SubmissionView {
    /// Post author username.
    pub author: String,
    /// Link flair text, if any.
    pub flair: Option<String>,
    /// Whether the post is locked.
    pub is_locked: bool,
    /// Whether the post is marked NSFW.
    pub is_nsfw: bool,
    /// Whether the post is original content.
    pub is_oc: bool,
    /// Whether the post is marked as a spoiler.
    pub is_spoiler: bool,
    /// Whether the post is stickied.
    pub is_stickied: bool,
    /// Pre-rendered syntax-highlighted JSON for the inspector panel.
    pub json_html: String,
    /// Number of comments on the post.
    pub num_comments: u32,
    /// Full URL to the Reddit post.
    pub permalink: String,
    /// Formatted score (e.g. "1.2k").
    pub score: String,
    /// Markdown-rendered self-text body, or empty.
    pub selftext_html: String,
    /// Subreddit name (without `r/` prefix).
    pub subreddit: String,
    /// Relative timestamp (e.g. "2 hours ago").
    pub time_ago: String,
    /// Post title.
    pub title: String,
    /// Formatted upvote ratio (e.g. "96%").
    pub upvote_ratio: String,
}

/// Tab info for Redditor profile.
#[derive(Debug, Clone)]
pub struct TabInfo {
    /// Number of items in this tab, or `None` if forbidden.
    pub count: Option<usize>,
    /// Whether this tab requires authenticated access.
    pub is_forbidden: bool,
    /// Human-readable tab label (e.g. "Comments").
    pub label: String,
    /// Machine-readable tab identifier (e.g. "comments").
    pub name: String,
}

/// View model for a livestream event.
#[derive(Debug, Clone)]
pub struct LivestreamEventView {
    /// Event author username.
    pub author: String,
    /// Markdown-rendered event body.
    pub body_html: String,
    /// HTML entity for the event type icon.
    pub icon: String,
    /// Pre-rendered syntax-highlighted JSON for the inspector panel.
    pub json_html: String,
    /// Subreddit the event belongs to.
    pub subreddit: String,
    /// Formatted timestamp (time only, e.g. "14:30:45").
    pub time_str: String,
    /// Submission title, if this is a submission event.
    pub title: Option<String>,
}

/// Serializes a value to pretty JSON and syntax-highlights it for the inspector panel.
fn highlight_json<T: serde::Serialize>(value: &T) -> String {
    let pretty = serde_json::to_string_pretty(value).unwrap_or_default();
    syntax_highlight_json(&pretty)
}

/// Returns HTML for a "forbidden" notice.
fn forbidden_html() -> String {
    r#"<div class="forbidden-notice">&#x1F512; This category requires authenticated access</div>"#
        .to_string()
}

/// Returns HTML for an empty tab.
fn empty_html() -> String {
    r#"<div class="forbidden-notice">No items in this category</div>"#.to_string()
}

/// Renders a rich view to an HTML string based on the scrape data type.
pub fn render_rich_html(
    data: ScrapeData,
    file_path: &str,
    breadcrumbs: Vec<BreadcrumbItem>,
    query: &ViewQuery,
) -> String {
    match data {
        ScrapeData::Submissions { posts, .. } => {
            let post_views: Vec<SubmissionView> = posts
                .iter()
                .map(|p| SubmissionView {
                    author: p.author.clone(),
                    flair: p.link_flair_text.clone(),
                    is_locked: p.locked,
                    is_nsfw: p.nsfw,
                    is_oc: p.is_original_content,
                    is_spoiler: p.spoiler,
                    is_stickied: p.stickied,
                    json_html: highlight_json(p),
                    num_comments: p.num_comments,
                    permalink: p.full_url(),
                    score: time::format_score(p.score),
                    selftext_html: p
                        .selftext
                        .as_deref()
                        .filter(|s| !s.is_empty())
                        .map(markdown::render)
                        .unwrap_or_default(),
                    subreddit: p.subreddit.clone(),
                    time_ago: time::relative_time(p.created_utc),
                    title: p.title.clone(),
                    upvote_ratio: format!("{:.0}%", p.upvote_ratio * 100.0),
                })
                .collect();

            let template = SubmissionsFragment {
                breadcrumbs,
                posts: post_views,
            };

            render_template(template)
        }
        ScrapeData::Comments {
            submission,
            comments,
            ..
        } => comments::render_comments_view(&submission, &comments, breadcrumbs),
        ScrapeData::Redditor(interactions) => {
            redditor::render_redditor_html(&interactions, file_path, breadcrumbs, query)
        }
        ScrapeData::Livestream(events) => {
            livestream::render_livestream_html(&events, file_path, breadcrumbs)
        }
        ScrapeData::Csv { .. } => {
            let template = ErrorFragment {
                message: "Unexpected CSV data in rich view".to_string(),
                status: 500,
            };
            render_template(template)
        }
    }
}
