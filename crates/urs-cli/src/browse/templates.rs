//! Askama template structs for the browse web server.
//!
//! Each struct corresponds to an HTML template in `crates/urs-cli/templates/`. Askama compiles
//! these at build time, so template syntax errors are caught during `cargo build`.

use askama::Template;

use super::loader::{FileEntry, format_size};
use super::views::{LivestreamEventView, RuleView, SubmissionView, SubredditInfoView, TabInfo};

/// A breadcrumb navigation item.
#[derive(Debug, Clone)]
pub struct BreadcrumbItem {
    /// Link target, or `None` for the current (non-clickable) segment.
    pub href: Option<String>,
    /// Display text for this breadcrumb segment.
    pub label: String,
}

/// Full-page shell: landing page with sidebar + empty content.
#[derive(Template)]
#[template(path = "index.html")]
pub struct IndexTemplate {
    /// Top-level directory entries to display in the file tree.
    pub entries: Vec<FileEntry>,
    /// Whether scraping is enabled (Reddit credentials are configured).
    pub scrape_enabled: bool,
    /// Reddit username of the authenticated account (None if no credentials).
    pub username: Option<String>,
}

/// Full-page shell: sidebar + pre-loaded content (for direct URL access).
#[derive(Template)]
#[template(path = "shell.html")]
pub struct ShellTemplate {
    /// Pre-rendered HTML content for the main area.
    pub content_html: String,
    /// Whether scraping is enabled (Reddit credentials are configured).
    pub scrape_enabled: bool,
    /// File tree entries for the sidebar navigation.
    pub sidebar_entries: Vec<FileEntry>,
    /// Reddit username of the authenticated account (None if no credentials).
    pub username: Option<String>,
}

/// HTMX partial: directory tree children.
#[derive(Template)]
#[template(path = "tree_fragment.html")]
pub struct TreeFragmentTemplate {
    /// Child entries of the expanded directory node.
    pub entries: Vec<FileEntry>,
}

/// HTMX partial: Redditor tab content.
#[derive(Template)]
#[template(path = "rich/redditor_tab.html")]
pub struct RedditorTabTemplate {
    /// Pre-rendered HTML for the tab's content.
    pub tab_content: String,
}

/// Fragment: submissions view (swapped into #main-content).
#[derive(Template)]
#[template(path = "fragments/submissions.html")]
pub struct SubmissionsFragment {
    /// Navigation breadcrumb trail.
    pub breadcrumbs: Vec<BreadcrumbItem>,
    /// Relative path to the scrape file (used for analytics link).
    pub file_path: String,
    /// Submission cards to render.
    pub posts: Vec<SubmissionView>,
    /// Subreddit rules, if included in the scrape.
    pub rules: Vec<RuleView>,
    /// Subreddit metadata extracted from the posts, if available.
    pub subreddit_info: Option<SubredditInfoView>,
}

/// Fragment: comments view.
#[derive(Template)]
#[template(path = "fragments/comments.html")]
pub struct CommentsFragment {
    /// Navigation breadcrumb trail.
    pub breadcrumbs: Vec<BreadcrumbItem>,
    /// Pre-rendered HTML for the nested comment thread.
    pub comments_html: String,
    /// Relative path to the scrape file (used for analytics link).
    pub file_path: String,
    /// The parent submission displayed as a header card.
    pub submission: SubmissionView,
    /// Total number of comments (including nested replies).
    pub total_count: usize,
}

/// Fragment: Redditor profile view.
#[derive(Template)]
#[template(path = "fragments/redditor.html")]
#[allow(clippy::struct_excessive_bools)]
pub struct RedditorFragment {
    /// Human-readable account age (e.g. "3 years").
    pub account_age: String,
    /// Name of the currently selected tab.
    pub active_tab: String,
    /// URL to the Redditor's avatar/icon image, if available.
    pub avatar_url: Option<String>,
    /// Formatted awardee karma (karma from receiving awards).
    pub awardee_karma: String,
    /// Formatted awarder karma (karma from giving awards).
    pub awarder_karma: String,
    /// The user's bio/tagline from their profile (`subreddit.public_description`).
    pub bio: Option<String>,
    /// Navigation breadcrumb trail.
    pub breadcrumbs: Vec<BreadcrumbItem>,
    /// Formatted comment karma.
    pub comment_karma: String,
    /// Formatted account creation date (e.g. "March 15, 2020").
    pub created_date: String,
    /// Relative path to the scrape file (used for JSON inspector API calls).
    pub file_path: String,
    /// Whether the Redditor has a verified email.
    pub has_verified_email: bool,
    /// Syntax-highlighted JSON of the Redditor's information block.
    pub information_json: String,
    /// Whether the Redditor is a Reddit employee.
    pub is_employee: bool,
    /// Whether the Redditor has Reddit Gold/Premium.
    pub is_gold: bool,
    /// Whether the Redditor is a moderator.
    pub is_mod: bool,
    /// Whether the Redditor's profile is marked NSFW.
    pub is_nsfw: bool,
    /// Formatted link karma.
    pub link_karma: String,
    /// Pre-rendered HTML for the active tab's content.
    pub tab_content: String,
    /// Available tabs with counts and forbidden status.
    pub tabs: Vec<TabInfo>,
    /// Formatted total karma.
    pub total_karma: String,
    /// The Redditor's username.
    pub username: String,
}

/// Fragment: livestream feed view.
#[derive(Template)]
#[template(path = "fragments/livestream.html")]
pub struct LivestreamFragment {
    /// Navigation breadcrumb trail.
    pub breadcrumbs: Vec<BreadcrumbItem>,
    /// Formatted elapsed duration (e.g. "00:12:34").
    pub duration: String,
    /// Total number of livestream events.
    pub event_count: usize,
    /// Livestream events to render in the feed.
    pub events: Vec<LivestreamEventView>,
    /// Formatted timestamp of the first event.
    pub first_event_time: String,
    /// Formatted timestamp of the last event.
    pub last_event_time: String,
    /// Livestream source type (e.g. "comments", "submissions").
    pub source: String,
    /// Livestream target (e.g. Subreddit name).
    pub target: String,
}

/// Fragment: live livestream feed (for active streaming).
#[derive(Template)]
#[template(path = "fragments/livestream_live.html")]
pub struct LivestreamLiveFragment {
    /// Livestream source type (e.g. "comments", "submissions").
    pub source: String,
    /// Unix timestamp (seconds) when the livestream started.
    pub started_at: f64,
    /// Livestream target (e.g. "r/rust", "u/spez").
    pub target: String,
    /// Task ID for the livestream.
    pub task_id: String,
}

/// Fragment: CSV table view.
#[derive(Template)]
#[template(path = "fragments/csv.html")]
pub struct CsvFragment {
    /// Navigation breadcrumb trail.
    pub breadcrumbs: Vec<BreadcrumbItem>,
    /// Relative path to the scrape file (used for download link).
    pub file_path: String,
    /// Column headers for the table.
    pub headers: Vec<String>,
    /// Table rows (each row is a vector of cell values).
    pub rows: Vec<Vec<String>>,
    /// Currently sorted column name, if any.
    pub sort_col: Option<String>,
    /// Sort direction: "asc" or "desc".
    pub sort_dir: String,
}

/// Fragment: word frequency analytics view.
#[derive(Template)]
#[template(path = "fragments/analytics.html")]
pub struct AnalyticsFragment {
    /// Navigation breadcrumb trail.
    pub breadcrumbs: Vec<BreadcrumbItem>,
    /// Available color schemes for the word cloud.
    pub color_schemes: Vec<ColorSchemeOption>,
    /// Word frequency entries to display.
    pub entries: Vec<WordFreqEntry>,
    /// Relative path to the scrape file (used for download URLs).
    pub file_path: String,
    /// Total number of words counted.
    pub total_count: u32,
    /// Number of unique words.
    pub unique_count: usize,
    /// Base64-encoded PNG word cloud image, or empty if generation failed.
    pub wordcloud_base64: String,
}

/// A single word frequency entry for the analytics table.
#[derive(Debug, Clone)]
pub struct WordFreqEntry {
    /// The count of occurrences.
    pub count: u32,
    /// Percentage relative to the most frequent word (for bar width).
    pub percentage: f32,
    /// The word.
    pub word: String,
}

/// A color scheme option for the word cloud customization form.
#[derive(Debug, Clone)]
pub struct ColorSchemeOption {
    /// Display name.
    pub label: String,
    /// Whether this is the currently selected scheme.
    pub selected: bool,
    /// URL slug.
    pub slug: String,
}

/// Fragment: settings page with credentials form.
#[derive(Template)]
#[template(path = "fragments/settings.html")]
pub struct SettingsFragment {
    /// Whether the server is currently authenticated with Reddit.
    pub authenticated: bool,
    /// Pre-filled client ID from config (empty if not set).
    pub client_id: String,
    /// Pre-filled client secret from config (empty if not set).
    pub client_secret: String,
    /// Path to the config file on disk.
    pub config_path: String,
    /// Pre-filled username from config (empty if not set).
    pub config_username: String,
    /// Currently authenticated Reddit username (empty if not connected).
    pub current_username: String,
    /// Pre-filled password from config (empty if not set).
    pub password: String,
}

/// Fragment: scrape form with tabbed interface.
#[derive(Template)]
#[template(path = "fragments/scrape_form.html")]
pub struct ScrapeFormFragment {
    /// Whether scraping is enabled (Reddit credentials are configured).
    pub scrape_enabled: bool,
}

/// Fragment: error message.
#[derive(Template)]
#[template(path = "fragments/error.html")]
pub struct ErrorFragment {
    /// Human-readable error description.
    pub message: String,
    /// HTTP status code to display.
    pub status: u16,
}

/// Askama custom filter module.
pub mod filters {
    /// Formats a file size.
    ///
    /// # Errors
    ///
    /// Never errors. Always returns `Ok`.
    #[allow(clippy::trivially_copy_pass_by_ref, clippy::unnecessary_wraps)]
    pub fn filesize(size: &u64) -> Result<String, askama::Error> {
        Ok(super::format_size(*size))
    }
}
