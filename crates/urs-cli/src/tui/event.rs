//! Async event loop for the livestream TUI.
//!
//! Multiplexes terminal input events, Reddit poll ticks, and UI render ticks using
//! `tokio::select!`.

use std::time::Duration;

use anyhow::Result;
use crossterm::event::{Event, EventStream, KeyCode, KeyEvent, KeyModifiers};
use futures::StreamExt;
use tokio::time::interval;
use tracing::warn;
use urs_core::scrapers::Livestreamer;

use super::app::App;
use super::terminal::Tui;
use super::ui;
use crate::commands::livestream::StreamContext;

/// Runs the main event loop.
///
/// Multiplexes three event sources:
/// 1. Terminal key events (via crossterm `EventStream`)
/// 2. Reddit poll timer (calls `streamer.poll()`)
/// 3. Render tick (refreshes relative timestamps)
///
/// # Arguments
///
/// * `terminal` - The ratatui terminal
/// * `app` - The application state
/// * `streamer` - The Reddit livestreamer
/// * `ctx` - The streaming context (handles file I/O)
///
/// # Errors
///
/// Returns an error if terminal I/O or Reddit API calls fail.
pub async fn run_event_loop(
    terminal: &mut Tui,
    app: &mut App,
    streamer: &mut Livestreamer<'_>,
    ctx: &mut StreamContext,
) -> Result<()> {
    let mut event_stream = EventStream::new();
    let mut poll_interval = interval(ctx.poll_duration());
    let mut render_interval = interval(Duration::from_millis(250));

    let target = streamer.target().clone();
    let source = *streamer.source();

    // Do an initial poll immediately.
    match streamer.poll().await {
        Ok(events) => {
            ctx.append_events(&events)?;
            app.push_events(events);
            app.mark_poll();
        }
        Err(err) => warn!("Initial poll failed: {err}"),
    }

    loop {
        // Draw the current frame.
        terminal.draw(|frame| ui::draw(frame, app, &target, source))?;

        if app.should_quit() {
            break;
        }

        tokio::select! {
            // Terminal events.
            maybe_event = event_stream.next() => {
                match maybe_event {
                    Some(Ok(Event::Key(key))) => handle_key(app, key),
                    Some(Ok(_)) => {} // Mouse events, resize, etc. — not handled.
                    Some(Err(err)) => warn!("Terminal event error: {err}"),
                    None => break, // Event stream closed.
                }
            }

            // Reddit poll tick.
            _ = poll_interval.tick() => {
                match streamer.poll().await {
                    Ok(events) => {
                        if !events.is_empty() {
                            ctx.append_events(&events)?;
                            app.push_events(events);
                        }
                        app.mark_poll();
                    }
                    Err(err) => warn!("Poll failed: {err}"),
                }
            }

            // Render tick (for relative timestamp refresh and animations).
            _ = render_interval.tick() => {
                app.advance_tick();
            }
        }
    }

    Ok(())
}

/// Handles a key press event.
fn handle_key(app: &mut App, key: KeyEvent) {
    match key.code {
        KeyCode::Char('q') | KeyCode::Esc => handle_escape(app),
        KeyCode::Up | KeyCode::Char('k') => app.scroll_up(1),
        KeyCode::Down | KeyCode::Char('j') => app.scroll_down(1),
        KeyCode::Char('u') if key.modifiers.contains(KeyModifiers::CONTROL) => {
            app.scroll_up(15);
        }
        KeyCode::Char('d') if key.modifiers.contains(KeyModifiers::CONTROL) => {
            app.scroll_down(15);
        }
        KeyCode::Char('g') | KeyCode::Home => app.jump_to_top(),
        KeyCode::Char('G') | KeyCode::End => app.jump_to_bottom(),
        KeyCode::Char('o') => handle_open_link(app),
        KeyCode::Enter => handle_enter(app),
        _ => {}
    }
}

/// Handles Esc/q: exits pane → exits detail → quits app.
fn handle_escape(app: &mut App) {
    if app.view_mode() == super::app::ViewMode::Detail {
        // If inside a pane, go back to pane selection. Otherwise close the detail view.
        if !app.exit_pane() {
            app.close_detail();
        }
    } else {
        app.quit();
    }
}

/// Handles the Enter key.
///
/// - Main table: opens the detail view.
/// - Detail pane selection: enters the highlighted pane.
/// - Inside a pane: no-op.
fn handle_enter(app: &mut App) {
    use super::app::DetailMode;

    if app.view_mode() != super::app::ViewMode::Detail {
        app.toggle_detail();
        return;
    }

    if app.detail_mode() == DetailMode::Selecting {
        app.enter_pane();
    }
}

/// Opens the link associated with the detail view item in the default browser.
///
/// Only active when the detail view is open.
fn handle_open_link(app: &App) {
    if app.view_mode() != super::app::ViewMode::Detail {
        return;
    }

    let url = app.detail_url();
    if url.is_empty() {
        return;
    }

    if let Err(err) = open::that(url) {
        warn!("Failed to open URL {url}: {err}");
    }
}
