//! Askama template structs for the browse web server.
//!
//! Each struct corresponds to an HTML template in `crates/urs-cli/templates/`. Askama compiles
//! these at build time, so template syntax errors are caught during `cargo build`.

use askama::Template;

use super::loader::{FileEntry, format_size};
use super::views::{LivestreamEventView, SubmissionView, TabInfo};

// ===== View Models =====

/// A breadcrumb navigation item.
#[derive(Debug, Clone)]
pub struct BreadcrumbItem {
    /// Link target, or `None` for the current (non-clickable) segment.
    pub href: Option<String>,
    /// Display text for this breadcrumb segment.
    pub label: String,
}

// ===== Full-Page Templates =====

/// Full-page shell: landing page with sidebar + empty content.
#[derive(Template)]
#[template(path = "index.html")]
pub struct IndexTemplate {
    /// Top-level directory entries to display in the file tree.
    pub entries: Vec<FileEntry>,
}

/// Full-page shell: sidebar + pre-loaded content (for direct URL access).
#[derive(Template)]
#[template(path = "shell.html")]
pub struct ShellTemplate {
    /// Pre-rendered HTML content for the main area.
    pub content_html: String,
    /// File tree entries for the sidebar navigation.
    pub sidebar_entries: Vec<FileEntry>,
}

// ===== HTMX Partials =====

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

// ===== Content Fragments =====

/// Fragment: submissions view (swapped into #main-content).
#[derive(Template)]
#[template(path = "fragments/submissions.html")]
pub struct SubmissionsFragment {
    /// Navigation breadcrumb trail.
    pub breadcrumbs: Vec<BreadcrumbItem>,
    /// Submission cards to render.
    pub posts: Vec<SubmissionView>,
}

/// Fragment: comments view.
#[derive(Template)]
#[template(path = "fragments/comments.html")]
pub struct CommentsFragment {
    /// Navigation breadcrumb trail.
    pub breadcrumbs: Vec<BreadcrumbItem>,
    /// Pre-rendered HTML for the nested comment thread.
    pub comments_html: String,
    /// The parent submission displayed as a header card.
    pub submission: SubmissionView,
    /// Total number of comments (including nested replies).
    pub total_count: usize,
}

/// Fragment: Redditor profile view.
#[derive(Template)]
#[template(path = "fragments/redditor.html")]
pub struct RedditorFragment {
    /// Human-readable account age (e.g. "3 years").
    pub account_age: String,
    /// Name of the currently selected tab.
    pub active_tab: String,
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
    /// Whether the Redditor has Reddit Gold/Premium.
    pub is_gold: bool,
    /// Whether the Redditor is a moderator.
    pub is_mod: bool,
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
    /// Total number of livestream events.
    pub event_count: usize,
    /// Livestream events to render in the feed.
    pub events: Vec<LivestreamEventView>,
    /// Livestream source type (e.g. "comments", "submissions").
    pub source: String,
    /// Livestream target (e.g. Subreddit name).
    pub target: String,
}

/// Fragment: CSV table view.
#[derive(Template)]
#[template(path = "fragments/csv.html")]
pub struct CsvFragment {
    /// Navigation breadcrumb trail.
    pub breadcrumbs: Vec<BreadcrumbItem>,
    /// Relative path to the scrape file (used for download link).
    pub file_path: String,
    /// Current filter text (shown in the search input).
    pub filter: String,
    /// Column headers for the table.
    pub headers: Vec<String>,
    /// Table rows (each row is a vector of cell values).
    pub rows: Vec<Vec<String>>,
    /// Currently sorted column name, if any.
    pub sort_col: Option<String>,
    /// Sort direction: "asc" or "desc".
    pub sort_dir: String,
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
