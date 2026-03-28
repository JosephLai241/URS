//! Status bar drawing for the TUI.
//!
//! Renders the bottom status bar with item count, poll time, and keybinding help.

use ratatui::Frame;
use ratatui::layout::Rect;
use ratatui::style::{Color, Style, Stylize};
use ratatui::text::{Line, Span};
use ratatui::widgets::Paragraph;

use super::URS_BRAND;
use crate::tui::app::App;

/// Draws the bottom status bar with the URS brand color.
pub(super) fn draw_status_bar(frame: &mut Frame, area: Rect, app: &App) {
    let total = app.total_count();

    let last_poll_text = app.last_poll().map_or_else(
        || "never".to_string(),
        |instant| {
            let elapsed = instant.elapsed().as_secs();
            format!("{elapsed}s ago")
        },
    );

    let auto_scroll_indicator = if app.auto_scroll() { " [auto]" } else { "" };

    let status = format!(
        " {total} items │ Last poll: {last_poll_text} │ '↑'/'k' up │ '↓'/'j' down │ 'Ctrl+u' pgup │ 'Ctrl+d' pgdn │ 'g'/'Home' top+follow │ 'G'/'End' bottom │ 'Enter' detail │ 'q'/'Esc' quit{auto_scroll_indicator}"
    );

    let bar = Paragraph::new(Line::from(vec![Span::styled(
        status,
        Style::default().fg(Color::White).bold(),
    )]))
    .style(Style::default().bg(URS_BRAND));

    frame.render_widget(bar, area);
}
