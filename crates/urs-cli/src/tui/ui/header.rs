//! Header/title bar drawing for the TUI.
//!
//! Renders the animated LIVE indicator and target/source information.

use ratatui::Frame;
use ratatui::layout::Rect;
use ratatui::style::{Color, Style, Stylize};
use ratatui::text::{Line, Span};
use ratatui::widgets::Paragraph;
use urs_core::scrapers::{LivestreamSource, LivestreamTarget};

use super::{LIVE_FRAMES, URS_BRAND};
use crate::tui::app::App;

/// Draws the header line with animated LIVE indicator.
pub(super) fn draw_header(
    frame: &mut Frame,
    area: Rect,
    app: &App,
    target: &LivestreamTarget,
    source: LivestreamSource,
) {
    // Animate the LIVE dot: toggle every ~2 ticks (500ms at 250ms render interval).
    let live_frame_idx = (app.tick() / 2) as usize % LIVE_FRAMES.len();
    let live_dot = LIVE_FRAMES[live_frame_idx];

    let header = Line::from(vec![
        Span::styled(
            format!(" {live_dot} LIVE "),
            Style::default()
                .fg(Color::White)
                .bg(Color::Rgb(200, 0, 0))
                .bold(),
        ),
        Span::styled("  ", Style::default().bg(URS_BRAND)),
        Span::styled(
            format!("{target}"),
            Style::default().fg(Color::White).bg(URS_BRAND).bold(),
        ),
        Span::styled(" │ ", Style::default().fg(Color::White).bg(URS_BRAND)),
        Span::styled(
            format!("{source} "),
            Style::default().fg(Color::White).bg(URS_BRAND),
        ),
    ]);

    let bar = Paragraph::new(header).style(Style::default().bg(URS_BRAND));
    frame.render_widget(bar, area);
}
