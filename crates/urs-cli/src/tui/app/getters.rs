//! Read-only accessor methods for [`App`].
//!
//! These methods provide access to the application state without modifying it.

use super::{App, DetailMode, DetailPane, ViewMode};
use urs_core::scrapers::LivestreamEvent;

impl App {
    /// Returns the events in the display buffer.
    #[must_use]
    pub fn events(&self) -> &[LivestreamEvent] {
        &self.events
    }

    /// Returns the index of the currently selected row.
    #[must_use]
    pub const fn selected(&self) -> usize {
        self.selected
    }

    /// Returns whether auto-scroll is enabled.
    #[must_use]
    pub const fn auto_scroll(&self) -> bool {
        self.auto_scroll
    }

    /// Returns the current view mode.
    #[must_use]
    pub const fn view_mode(&self) -> ViewMode {
        self.view_mode
    }

    /// Returns the total number of events ever received.
    #[must_use]
    pub const fn total_count(&self) -> usize {
        self.total_count
    }

    /// Returns the instant of the last successful poll.
    #[must_use]
    pub const fn last_poll(&self) -> Option<std::time::Instant> {
        self.last_poll
    }

    /// Returns whether the application should quit.
    #[must_use]
    pub const fn should_quit(&self) -> bool {
        self.should_quit
    }

    /// Returns the detail view selected row index.
    #[must_use]
    pub const fn detail_scroll(&self) -> u16 {
        self.detail_scroll
    }

    /// Returns which pane is currently highlighted in the detail view.
    #[must_use]
    pub const fn detail_pane(&self) -> DetailPane {
        self.detail_pane
    }

    /// Returns the current detail view interaction mode.
    #[must_use]
    pub const fn detail_mode(&self) -> DetailMode {
        self.detail_mode
    }

    /// Returns the cached detail view metadata fields.
    #[must_use]
    pub fn detail_fields(&self) -> &[(String, serde_json::Value)] {
        &self.detail_fields
    }

    /// Returns the cached detail view body text.
    #[must_use]
    pub fn detail_body(&self) -> &str {
        &self.detail_body
    }

    /// Returns the URL associated with the detail view item.
    #[must_use]
    pub fn detail_url(&self) -> &str {
        &self.detail_url
    }

    /// Returns the current render tick counter.
    #[must_use]
    pub const fn tick(&self) -> u64 {
        self.tick
    }

    /// Returns the maximum valid selection index.
    pub(crate) fn max_index(&self) -> usize {
        self.events.len().saturating_sub(1)
    }
}
