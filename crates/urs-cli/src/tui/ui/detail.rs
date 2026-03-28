//! Detail overlay drawing for the TUI.
//!
//! Renders the detail view with metadata fields, body content, URL box, and footer when a user
//! selects an event for closer inspection.

use ratatui::Frame;
use ratatui::layout::{Constraint, Layout, Margin, Rect};
use ratatui::style::{Color, Style, Stylize};
use ratatui::text::{Span, Text};
use ratatui::widgets::{
    Block, Borders, Cell, Clear, Paragraph, Row, Scrollbar, ScrollbarOrientation, ScrollbarState,
    Table, TableState, Wrap,
};
use urs_core::scrapers::LivestreamEvent;

use super::URS_BRAND;
use super::helpers::{format_json_value, wrapped_line_count};
use crate::tui::app::{App, DetailMode, DetailPane};

/// Draws the detail overlay with a two-pane layout: metadata table on top, body text below.
pub(super) fn draw_detail_overlay(frame: &mut Frame, app: &mut App) {
    let area = frame.area();

    // Center the overlay with padding.
    let h_margin = area.width / 8;
    let v_margin = area.height / 8;
    let overlay = Rect {
        x: area.x + h_margin,
        y: area.y + v_margin,
        width: area.width.saturating_sub(h_margin * 2),
        height: area.height.saturating_sub(v_margin * 2),
    };

    // Clear the area behind the overlay.
    frame.render_widget(Clear, overlay);

    let Some(event) = app.events().get(app.selected()) else {
        return;
    };

    let title = match event {
        LivestreamEvent::Comment(c) => format!(" Comment by u/{} ", c.author),
        LivestreamEvent::Submission(s) => format!(" Submission by u/{} ", s.author),
    };

    let has_body = !app.detail_body().is_empty();
    let has_url = !app.detail_url().is_empty();

    // Split the overlay into: fields table, body pane (if content exists), URL box, footer.
    let mut constraints = vec![if has_body {
        Constraint::Percentage(55) // Fields table
    } else {
        Constraint::Min(3) // Fields table (gets all space)
    }];

    if has_body {
        constraints.push(Constraint::Min(5)); // Body pane
    }
    if has_url {
        constraints.push(Constraint::Length(3)); // URL box (border + 1 line + border)
    }
    constraints.push(Constraint::Length(1)); // Footer

    let chunks = Layout::vertical(constraints).split(overlay);

    let mut chunk_idx = 0;
    let fields_area = chunks[chunk_idx];
    chunk_idx += 1;

    let body_area = if has_body {
        let area = chunks[chunk_idx];
        chunk_idx += 1;
        Some(area)
    } else {
        None
    };

    let url_area = if has_url {
        let area = chunks[chunk_idx];
        chunk_idx += 1;
        Some(area)
    } else {
        None
    };

    let footer_area = chunks[chunk_idx];

    draw_detail_fields(frame, fields_area, app, &title);

    if let Some(body_area) = body_area {
        draw_detail_body(frame, body_area, app);
    }

    if let Some(url_area) = url_area {
        draw_detail_url(frame, url_area, app);
    }

    draw_detail_footer(frame, footer_area, app);
}

/// Draws the metadata fields table in the top pane of the detail overlay.
fn draw_detail_fields(frame: &mut Frame, area: Rect, app: &App, title: &str) {
    let fields = app.detail_fields();
    let is_this_pane = app.detail_pane() == DetailPane::Fields;

    // Three-state border styling:
    // - Active (entered) pane: orange border
    // - Highlighted (Selecting mode) pane: white border
    // - Neither: gray border
    let border_style = if is_this_pane && app.detail_mode() == DetailMode::Active {
        Style::default().fg(URS_BRAND)
    } else if is_this_pane && app.detail_mode() == DetailMode::Selecting {
        Style::default().fg(Color::White)
    } else {
        Style::default().fg(Color::DarkGray)
    };

    // Only show row highlight when this pane is active (entered).
    let is_active = is_this_pane && app.detail_mode() == DetailMode::Active;

    let block = Block::default()
        .title(title.to_string())
        .title_style(Style::default().fg(URS_BRAND).bold())
        .borders(Borders::ALL)
        .border_style(border_style)
        .style(Style::default().bg(Color::Black));

    let header = Row::new(vec![
        Cell::from("Field").style(Style::default().fg(Color::Yellow).bold()),
        Cell::from("Value").style(Style::default().fg(Color::Yellow).bold()),
    ])
    .height(1);

    let field_col_width: u16 = 22;
    let widths = [Constraint::Length(field_col_width), Constraint::Min(20)];

    let rows: Vec<Row> = fields
        .iter()
        .map(|(key, value)| {
            Row::new(vec![
                Cell::from(key.clone()).style(Style::default().fg(URS_BRAND)),
                Cell::from(format_json_value(value)),
            ])
        })
        .collect();

    let visible_rows = area.height.saturating_sub(3) as usize; // Borders + header
    let total_rows = rows.len();

    let table = Table::new(rows, widths)
        .header(header)
        .block(block)
        .highlight_symbol("▶ ")
        .row_highlight_style(Style::default().fg(Color::White).bold());

    let scroll_offset = app.detail_scroll() as usize;
    let mut state =
        TableState::default().with_selected(if is_active { Some(scroll_offset) } else { None });
    *state.offset_mut() = scroll_offset;

    frame.render_stateful_widget(table, area, &mut state);

    // Table scrollbar.
    if total_rows > visible_rows {
        let mut scrollbar_state = ScrollbarState::new(total_rows).position(scroll_offset);
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

/// Draws the body/selftext content in the bottom pane of the detail overlay.
fn draw_detail_body(frame: &mut Frame, area: Rect, app: &mut App) {
    let is_this_pane = app.detail_pane() == DetailPane::Body;

    // Three-state border styling (same logic as fields pane).
    let border_style = if is_this_pane && app.detail_mode() == DetailMode::Active {
        Style::default().fg(URS_BRAND)
    } else if is_this_pane && app.detail_mode() == DetailMode::Selecting {
        Style::default().fg(Color::White)
    } else {
        Style::default().fg(Color::DarkGray)
    };

    let block = Block::default()
        .title(" Content ")
        .title_style(Style::default().fg(URS_BRAND).bold())
        .borders(Borders::ALL)
        .border_style(border_style)
        .style(Style::default().bg(Color::Black));

    // Compute wrapped line count and clamp the scroll offset so it never exceeds the content.
    // Writing the clamped value back to App keeps the state in sync with what is rendered,
    // so that subsequent scroll_up/scroll_down operate from the real position.
    let inner_width = area.width.saturating_sub(2) as usize;
    let total_lines = app
        .detail_body()
        .lines()
        .map(|line| wrapped_line_count(line, inner_width))
        .sum::<usize>()
        .max(1);
    let visible_lines = area.height.saturating_sub(2) as usize;

    #[allow(clippy::cast_possible_truncation)]
    let max_scroll = total_lines.saturating_sub(visible_lines) as u16;
    let clamped_scroll = app.clamp_body_scroll(max_scroll);

    let paragraph = Paragraph::new(Text::raw(app.detail_body()))
        .block(block)
        .wrap(Wrap { trim: false })
        .scroll((clamped_scroll, 0));

    frame.render_widget(paragraph, area);

    // Body scrollbar.
    if total_lines > visible_lines {
        let mut scrollbar_state =
            ScrollbarState::new(total_lines).position(clamped_scroll as usize);
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

/// Draws the URL box below the content panes (not selectable).
fn draw_detail_url(frame: &mut Frame, area: Rect, app: &App) {
    let block = Block::default()
        .title(" Link ")
        .title_style(Style::default().fg(URS_BRAND).bold())
        .borders(Borders::ALL)
        .border_style(Style::default().fg(Color::DarkGray))
        .style(Style::default().bg(Color::Black));

    let url_text = app.detail_url();
    let paragraph = Paragraph::new(Span::styled(
        url_text,
        Style::default().fg(Color::Cyan).underlined(),
    ))
    .block(block);

    frame.render_widget(paragraph, area);
}

/// Draws the detail overlay footer with keybinding help.
fn draw_detail_footer(frame: &mut Frame, area: Rect, app: &App) {
    let help_text = match app.detail_mode() {
        DetailMode::Active => {
            " '↑'/'k' up │ '↓'/'j' down │ 'Ctrl+u' pgup │ 'Ctrl+d' pgdn │ 'g' top │ 'G' bottom │ 'o' open link │ 'q'/'Esc' exit pane"
        }
        DetailMode::Selecting => {
            " '↑'/'k' '↓'/'j' select pane │ 'Enter' enter pane │ 'o' open link │ 'q'/'Esc' close"
        }
    };

    let help = Paragraph::new(Span::styled(
        help_text,
        Style::default().fg(Color::White).bold(),
    ))
    .style(Style::default().bg(URS_BRAND));

    frame.render_widget(help, area);
}
