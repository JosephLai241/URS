//! TUI rendering for the livestream viewer.
//!
//! Draws the header, scrolling table, status bar, and optional detail overlay using ratatui
//! widgets.

use chrono::Utc;
use ratatui::Frame;
use ratatui::layout::{Constraint, Layout, Margin, Rect};
use ratatui::style::{Color, Style, Stylize};
use ratatui::text::{Line, Span, Text};
use ratatui::widgets::{
    Block, Borders, Cell, Clear, Paragraph, Row, Scrollbar, ScrollbarOrientation, ScrollbarState,
    Table, TableState,
};
use urs_core::scrapers::{LivestreamEvent, LivestreamSource, LivestreamTarget};

use ratatui::widgets::Wrap;

use super::app::{App, DetailMode, DetailPane, ViewMode};

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

    draw_header(frame, chunks[0], app, target, source);
    draw_table(frame, chunks[1], app, source);
    draw_status_bar(frame, chunks[2], app);

    if app.view_mode() == ViewMode::Detail {
        draw_detail_overlay(frame, app);
    }
}

/// Draws the header line with animated LIVE indicator.
fn draw_header(
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

/// Right-side padding for the main table content.
const TABLE_RIGHT_PADDING: u16 = 2;

/// Draws the main scrolling table.
fn draw_table(frame: &mut Frame, area: Rect, app: &App, source: LivestreamSource) {
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

/// Computes how many visual lines a string occupies when wrapped at `max_width` characters.
///
/// Returns at least 1 (even for empty strings).
fn wrapped_line_count(s: &str, max_width: usize) -> usize {
    if max_width == 0 || s.is_empty() {
        return 1;
    }
    let char_count = s.chars().count();

    char_count.div_ceil(max_width).max(1)
}

/// Draws the bottom status bar with the URS brand color.
fn draw_status_bar(frame: &mut Frame, area: Rect, app: &App) {
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

/// Draws the detail overlay with a two-pane layout: metadata table on top, body text below.
fn draw_detail_overlay(frame: &mut Frame, app: &mut App) {
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

/// Formats a `serde_json::Value` as a human-readable string for display.
fn format_json_value(value: &serde_json::Value) -> String {
    match value {
        serde_json::Value::Array(arr) => {
            if arr.is_empty() {
                "[]".to_string()
            } else {
                serde_json::to_string(arr).unwrap_or_else(|_| format!("[{} items]", arr.len()))
            }
        }
        serde_json::Value::Bool(b) => b.to_string(),
        serde_json::Value::Null => "null".to_string(),
        serde_json::Value::Number(n) => n.to_string(),
        serde_json::Value::Object(obj) => {
            if obj.is_empty() {
                "{}".to_string()
            } else {
                serde_json::to_string(obj).unwrap_or_else(|_| format!("{{{} fields}}", obj.len()))
            }
        }
        serde_json::Value::String(s) => s.replace('\n', " ↵ "),
    }
}

/// Formats a UTC timestamp as a human-readable relative time string.
///
/// # Arguments
///
/// * `created_utc` - The UTC timestamp as seconds since epoch
#[must_use]
pub fn format_relative_time(created_utc: f64) -> String {
    let now = Utc::now().timestamp();
    let created = epoch_f64_to_i64(created_utc);
    let diff = (now - created).max(0);

    let secs: u64 = diff.unsigned_abs();

    if secs < 60 {
        format!("{secs}s ago")
    } else if secs < 3600 {
        format!("{}m ago", secs / 60)
    } else if secs < 86_400 {
        format!("{}h ago", secs / 3600)
    } else {
        format!("{}d ago", secs / 86_400)
    }
}

/// Converts an epoch timestamp from `f64` (as Reddit returns) to `i64`.
///
/// Reddit timestamps are positive integers well within `i64` range, so the truncation from `f64`
/// (52-bit mantissa) to `i64` (63-bit) is lossless for all realistic values.
#[allow(clippy::cast_possible_truncation)]
const fn epoch_f64_to_i64(epoch: f64) -> i64 {
    epoch as i64
}
