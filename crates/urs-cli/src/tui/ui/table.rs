//! Event table drawing for the TUI.
//!
//! Renders the main scrolling table of livestream events with a scrollbar.

use ratatui::Frame;
use ratatui::layout::{Constraint, Margin, Rect};
use ratatui::style::{Color, Style, Stylize};
use ratatui::widgets::{
    Block, Borders, Cell, Row, Scrollbar, ScrollbarOrientation, ScrollbarState, Table, TableState,
};
use urs_core::scrapers::{LivestreamEvent, LivestreamSource};

use super::helpers::format_relative_time;
use crate::tui::app::App;

/// Right-side padding for the main table content.
const TABLE_RIGHT_PADDING: u16 = 2;

/// Draws the main scrolling table.
pub(super) fn draw_table(frame: &mut Frame, area: Rect, app: &App, source: LivestreamSource) {
    let padded_area = Rect {
        x: area.x,
        y: area.y,
        width: area.width.saturating_sub(TABLE_RIGHT_PADDING),
        height: area.height,
    };

    let header_cells = match source {
        LivestreamSource::Comments => vec!["Time", "Author", "Body"],
        LivestreamSource::Submissions => vec!["Time", "Author", "Title"],
    };

    let header = Row::new(
        header_cells
            .into_iter()
            .map(|h| Cell::from(h).style(Style::default().fg(Color::Yellow).bold())),
    )
    .height(1);

    let rows: Vec<Row> = app
        .events()
        .iter()
        .enumerate()
        .map(|(i, event)| {
            let is_selected = i == app.selected();
            let style = if is_selected {
                Style::default().bg(Color::DarkGray)
            } else {
                Style::default()
            };
            event_to_row(event, style)
        })
        .collect();

    let widths = [
        Constraint::Length(10),
        Constraint::Length(18),
        Constraint::Min(20),
    ];

    let table = Table::new(rows, widths)
        .header(header)
        .block(Block::default().borders(Borders::NONE))
        .row_highlight_style(Style::default().bg(Color::DarkGray));

    let mut state = TableState::default().with_selected(Some(app.selected()));
    frame.render_stateful_widget(table, padded_area, &mut state);

    // Scrollbar.
    if app.events().len() > padded_area.height as usize {
        let mut scrollbar_state = ScrollbarState::new(app.events().len()).position(app.selected());
        let scrollbar = Scrollbar::new(ScrollbarOrientation::VerticalRight);

        frame.render_stateful_widget(
            scrollbar,
            area.inner(Margin {
                vertical: 1,
                horizontal: 0,
            }),
            &mut scrollbar_state,
        );
    }
}

/// Converts a livestream event into a table row.
fn event_to_row(event: &LivestreamEvent, style: Style) -> Row<'static> {
    match event {
        LivestreamEvent::Comment(c) => {
            let time_ago = format_relative_time(c.created_utc);
            let author = format!("u/{}", c.author);
            let body = c.body.replace('\n', " ");

            Row::new(vec![
                Cell::from(time_ago),
                Cell::from(author).style(Style::default().fg(Color::Green)),
                Cell::from(body),
            ])
            .style(style)
        }
        LivestreamEvent::Submission(s) => {
            let time_ago = format_relative_time(s.created_utc);
            let author = format!("u/{}", s.author);

            Row::new(vec![
                Cell::from(time_ago),
                Cell::from(author).style(Style::default().fg(Color::Green)),
                Cell::from(s.title.clone()),
            ])
            .style(style)
        }
    }
}
