//! TUI rendering for the livestream viewer.
//!
//! Draws the header, scrolling table, status bar, and optional detail overlay using ratatui
//! widgets.

mod detail;
mod header;
pub mod helpers;
mod status;
mod table;

use ratatui::Frame;
use ratatui::layout::{Constraint, Layout};
use ratatui::style::Color;
use urs_core::scrapers::{LivestreamSource, LivestreamTarget};

use super::app::{App, ViewMode};

/// The URS brand color used for the status bar.
const URS_BRAND: Color = Color::Rgb(206, 66, 43);

/// Animation frames for the LIVE indicator dot.
const LIVE_FRAMES: &[&str] = &["⏺", " "];

/// Draws the entire TUI frame.
///
/// # Arguments
///
/// * `frame` - The ratatui frame to draw into
/// * `app` - The application state
/// * `target` - The livestream target (Subreddit or Redditor)
/// * `source` - The livestream source (comments or submissions)
pub fn draw(frame: &mut Frame, app: &mut App, target: &LivestreamTarget, source: LivestreamSource) {
    let chunks = Layout::vertical([
        Constraint::Length(1), // Header
        Constraint::Min(3),    // Table
        Constraint::Length(1), // Status bar
    ])
    .split(frame.area());

    header::draw_header(frame, chunks[0], app, target, source);
    table::draw_table(frame, chunks[1], app, source);
    status::draw_status_bar(frame, chunks[2], app);

    if app.view_mode() == ViewMode::Detail {
        detail::draw_detail_overlay(frame, app);
    }
}
