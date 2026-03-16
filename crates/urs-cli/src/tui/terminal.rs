//! Terminal setup and cleanup for the TUI.
//!
//! Provides functions to enter and exit raw mode, set up the alternate screen, and install a panic
//! hook that restores the terminal on crash.

use std::io::{self, Stdout};

use crossterm::execute;
use crossterm::terminal::{
    EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode,
};
use ratatui::Terminal;
use ratatui::backend::CrosstermBackend;
use tracing::error;

/// The terminal type used by the TUI.
pub type Tui = Terminal<CrosstermBackend<Stdout>>;

/// Sets up the terminal for TUI rendering.
///
/// Enables raw mode, enters the alternate screen, and installs a panic hook that restores the
/// terminal if the application panics.
///
/// # Errors
///
/// Returns an error if enabling raw mode or entering the alternate screen fails.
pub fn setup_terminal() -> io::Result<Tui> {
    let original_hook = std::panic::take_hook();
    std::panic::set_hook(Box::new(move |panic_info| {
        if let Err(e) = restore_terminal_impl() {
            error!("Failed to restore terminal during panic: {e}");
            eprintln!("Failed to restore terminal during panic: {e}");
        }
        original_hook(panic_info);
    }));

    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;

    let backend = CrosstermBackend::new(stdout);
    let terminal = Terminal::new(backend)?;

    Ok(terminal)
}

/// Restores the terminal to its original state.
///
/// Disables raw mode and leaves the alternate screen. Safe to call multiple times.
///
/// # Errors
///
/// Returns an error if disabling raw mode or leaving the alternate screen fails.
pub fn restore_terminal(terminal: &mut Tui) -> io::Result<()> {
    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;

    Ok(())
}

/// Internal terminal restoration (used by the panic hook).
fn restore_terminal_impl() -> io::Result<()> {
    disable_raw_mode()?;
    execute!(io::stdout(), LeaveAlternateScreen)?;

    Ok(())
}
