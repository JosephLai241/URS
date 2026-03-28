//! TUI application state for the livestream viewer.
//!
//! Manages the display buffer of livestream events, scroll position, auto-scroll behavior, and
//! detail view state.
//!
//! The [`App`] struct and its methods are split across submodules:
//!
//! - [`getters`]: Read-only accessor methods
//! - [`handlers`]: Methods that mutate application state

mod getters;
mod handlers;

use urs_core::scrapers::LivestreamEvent;

/// The interaction state within the detail view.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DetailMode {
    /// Inside a pane. Scroll controls apply to its contents.
    Active,
    /// Choosing which pane to enter. The highlighted pane is stored separately.
    Selecting,
}

/// Which pane is highlighted or active in the detail view.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DetailPane {
    /// The body/selftext content area.
    Body,
    /// The metadata fields table.
    Fields,
}

/// The current view mode of the TUI.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ViewMode {
    /// Detail view showing full content of the selected item.
    Detail,
    /// The main scrolling table view.
    Table,
}

/// Field names that contain long text content shown in the body pane.
pub const BODY_FIELDS: &[&str] = &["body", "body_html", "selftext"];

/// Application state for the livestream TUI.
#[derive(Debug)]
pub struct App {
    /// Whether auto-scroll is enabled (follows newest items).
    pub(crate) auto_scroll: bool,
    /// Maximum number of events to keep in the display buffer.
    pub(crate) buffer_limit: usize,
    /// Cached body text for the detail view (body for comments, selftext for submissions).
    pub(crate) detail_body: String,
    /// Scroll offset for the body pane in the detail view.
    pub(crate) detail_body_scroll: u16,
    /// Cached metadata fields for the currently open detail view (excludes body content).
    pub(crate) detail_fields: Vec<(String, serde_json::Value)>,
    /// Whether we're selecting a pane or active inside one.
    pub(crate) detail_mode: DetailMode,
    /// Which pane is highlighted in the detail view.
    pub(crate) detail_pane: DetailPane,
    /// Selected row index within the detail view field table.
    pub(crate) detail_scroll: u16,
    /// The URL associated with the currently open detail view item.
    pub(crate) detail_url: String,
    /// The display buffer of livestream events (newest first).
    pub(crate) events: Vec<LivestreamEvent>,
    /// Timestamp of the last successful poll.
    pub(crate) last_poll: Option<std::time::Instant>,
    /// The index of the currently selected row.
    pub(crate) selected: usize,
    /// Whether the application should quit.
    pub(crate) should_quit: bool,
    /// Render tick counter for animations (wraps around).
    pub(crate) tick: u64,
    /// Total number of events ever received (including those dropped from the buffer).
    pub(crate) total_count: usize,
    /// The current view mode.
    pub(crate) view_mode: ViewMode,
}

impl App {
    /// Creates a new application state with the given buffer limit.
    ///
    /// # Arguments
    ///
    /// * `buffer_limit` - Maximum number of events to keep in the display buffer
    #[must_use]
    pub const fn new(buffer_limit: usize) -> Self {
        Self {
            auto_scroll: true,
            buffer_limit,
            detail_body: String::new(),
            detail_body_scroll: 0,
            detail_fields: Vec::new(),
            detail_mode: DetailMode::Selecting,
            detail_pane: DetailPane::Fields,
            detail_scroll: 0,
            detail_url: String::new(),
            events: Vec::new(),
            last_poll: None,
            selected: 0,
            should_quit: false,
            tick: 0,
            total_count: 0,
            view_mode: ViewMode::Table,
        }
    }
}
