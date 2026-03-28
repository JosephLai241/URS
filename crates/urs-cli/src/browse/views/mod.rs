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

pub mod analytics;
mod comments;
pub(super) mod livestream;
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
    /// Raw UTC timestamp for client-side tooltip formatting.
    pub time_utc: f64,
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
    /// SVG icon HTML for the event type.
    pub icon: String,
    /// Pre-rendered syntax-highlighted JSON for the inspector panel.
    pub json_html: String,
    /// Permalink URL for submissions (full Reddit URL).
    pub permalink: Option<String>,
    /// Subreddit the event belongs to.
    pub subreddit: String,
    /// Formatted timestamp (time only, e.g. "14:30:45").
    pub time_str: String,
    /// Raw UTC timestamp for client-side tooltip formatting.
    pub time_utc: f64,
    /// Submission title, if this is a submission event.
    pub title: Option<String>,
}

/// View model for the Subreddit info card shown above submissions.
#[derive(Debug, Clone)]
pub struct SubredditInfoView {
    /// Active users online (e.g. "1,234").
    pub active_users: Option<String>,
    /// Formatted creation date (e.g. "March 15, 2020").
    pub created_date: Option<String>,
    /// Short description from the Subreddit sidebar.
    pub description: Option<String>,
    /// URL to the Subreddit's icon image, if available.
    pub icon_url: Option<String>,
    /// Pre-rendered syntax-highlighted JSON for the inspector panel.
    pub information_json: String,
    /// Subreddit display name (without `r/` prefix).
    pub name: String,
    /// Whether the Subreddit is NSFW.
    pub nsfw: bool,
    /// Whether the Subreddit is quarantined.
    pub quarantined: bool,
    /// Formatted subscriber count (e.g. "2,330,872").
    pub subscribers: Option<String>,
    /// Subreddit type (e.g. "public", "private", "restricted").
    pub subreddit_type: Option<String>,
    /// Human-readable Subreddit title (e.g. "The Rust Programming Language").
    pub title: Option<String>,
}

/// View model for a Subreddit rule.
#[derive(Debug, Clone)]
pub struct RuleView {
    /// The rule description rendered as HTML.
    pub description_html: String,
    /// The rule kind (e.g. "all", "link", "comment").
    pub kind: String,
    /// Short name/title of the rule.
    pub short_name: String,
}

/// Converts a `Subreddit` model into a `SubredditInfoView` for rendering.
fn subreddit_info_from_model(info: &urs_core::models::Subreddit) -> SubredditInfoView {
    #[allow(clippy::cast_possible_wrap)]
    let subscribers = Some(time::format_number(info.subscribers as i64));

    #[allow(clippy::cast_possible_wrap)]
    let active_users = info.accounts_active.map(|n| time::format_number(n as i64));

    let description = if info.public_description.is_empty() {
        None
    } else {
        Some(info.public_description.clone())
    };

    let icon_url = info
        .icon_img
        .as_deref()
        .filter(|s| !s.is_empty())
        .map(String::from);

    let title = if info.title.is_empty() || info.title == info.display_name {
        None
    } else {
        Some(info.title.clone())
    };

    SubredditInfoView {
        active_users,
        created_date: Some(time::format_date(info.created_utc)),
        description,
        icon_url,
        information_json: highlight_json(info),
        name: info.display_name.clone(),
        nsfw: info.nsfw,
        quarantined: info
            .extra
            .get("quarantine")
            .and_then(serde_json::Value::as_bool)
            .unwrap_or(false),
        subscribers,
        subreddit_type: Some(info.subreddit_type.clone()),
        title,
    }
}

/// Extracts Subreddit metadata from the first post's extra fields.
///
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
        ScrapeData::Submissions {
            information,
            posts,
            rules,
        } => {
            let subreddit_info = Some(subreddit_info_from_model(&information));

            let rule_views: Vec<RuleView> = rules
                .map(|r| {
                    r.rules
                        .iter()
                        .map(|rule| RuleView {
                            description_html: if rule.description.is_empty() {
                                String::new()
                            } else {
                                markdown::render(&rule.description)
                            },
                            kind: rule.kind.clone(),
                            short_name: rule.short_name.clone(),
                        })
                        .collect()
                })
                .unwrap_or_default();

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
                    time_utc: p.created_utc,
                    title: p.title.clone(),
                    upvote_ratio: format!("{:.0}%", p.upvote_ratio * 100.0),
                })
                .collect();

            let template = SubmissionsFragment {
                breadcrumbs,
                file_path: file_path.to_string(),
                posts: post_views,
                rules: rule_views,
                subreddit_info,
            };

            render_template(template)
        }
        ScrapeData::Comments {
            comments,
            submission,
            ..
        } => comments::render_comments_view(&submission, &comments, file_path, breadcrumbs),
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
