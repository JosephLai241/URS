//! Log viewer command.
//!
//! Prints the contents of the URS log file. Supports a `-f` flag to follow the log in real-time,
//! similar to `tail -f`.

use std::io::{self, BufRead, BufReader, Seek, SeekFrom};
use std::path::PathBuf;
use std::time::Duration;

use anyhow::{Context, Result, bail};
use clap::Parser;
use tracing::{debug, error};

use crate::helpers::log_dir;

/// View URS log output.
#[derive(Debug, Parser)]
#[command(after_long_help = "\
\x1b[1;4mExamples:\x1b[0m

  Show the last 50 lines of the most recent log:
    urs log

  Show the last 200 lines:
    urs log --lines 200

  Follow the log in real-time (like tail -f):
    urs log --follow

  Follow with more initial context:
    urs log -f -l 100

  Show logs from a specific date:
    urs log --date 2026-03-15

\x1b[1;4mLog location:\x1b[0m

  Logs are stored as daily rolling files named urs.log.YYYY-MM-DD in a
  platform-specific directory:

    Linux:   ~/.local/share/urs/logs/
    macOS:   ~/Library/Application Support/urs/logs/
    Windows: C:\\Users\\<user>\\AppData\\Roaming\\urs\\logs\\")]
pub struct LogArgs {
    /// Follow the log file in real-time (like `tail -f`).
    #[arg(short, long, default_value_t = false)]
    pub follow: bool,

    /// Number of lines to show from the end of the file.
    ///
    /// When used with `-f`, shows the last N lines before following.
    #[arg(short, long, default_value_t = 50)]
    pub lines: usize,

    /// Show logs from a specific date (YYYY-MM-DD). Defaults to the most recent log.
    #[arg(short, long)]
    pub date: Option<String>,
}

/// Runs the log viewer command.
///
/// # Errors
///
/// Returns an error if the log directory or file cannot be read.
pub async fn run(args: LogArgs) -> Result<()> {
    let log_path = if let Some(ref date) = args.date {
        find_log_for_date(date)?
    } else {
        find_latest_log()?
    };

    if args.follow {
        tail_follow(&log_path, args.lines).await
    } else {
        print_tail(&log_path, args.lines)
    }
}

/// Finds the most recently modified log file in the log directory.
fn find_latest_log() -> Result<PathBuf> {
    let dir = log_dir();
    debug!(dir = %dir.display(), "Searching for latest log file");

    if !dir.exists() {
        bail!("Log directory does not exist: {}", dir.display());
    }

    let mut entries: Vec<_> = std::fs::read_dir(&dir)
        .with_context(|| format!("Failed to read log directory: {}", dir.display()))?
        .filter_map(|entry| {
            let entry = entry.ok()?;
            let path = entry.path();
            if path.is_file()
                && path
                    .file_name()
                    .and_then(|n| n.to_str())
                    .is_some_and(|n| n.starts_with("urs.log"))
            {
                let modified = entry.metadata().ok()?.modified().ok()?;
                Some((path, modified))
            } else {
                None
            }
        })
        .collect();

    entries.sort_by(|a, b| b.1.cmp(&a.1));

    entries
        .into_iter()
        .next()
        .map(|(path, _)| path)
        .ok_or_else(|| anyhow::anyhow!("No log files found in {}", dir.display()))
}

/// Finds the log file for a specific date.
///
/// Looks for a file named `urs.log.YYYY-MM-DD` in the log directory.
fn find_log_for_date(date: &str) -> Result<PathBuf> {
    let dir = log_dir();
    let path = dir.join(format!("urs.log.{date}"));

    if path.is_file() {
        Ok(path)
    } else {
        bail!("No log file found for date {date} (expected {})", path.display());
    }
}

/// Prints the last `n` lines from the log file.
fn print_tail(path: &PathBuf, n: usize) -> Result<()> {
    let file =
        std::fs::File::open(path).with_context(|| format!("Failed to open {}", path.display()))?;
    let reader = BufReader::new(file);

    let lines: Vec<String> = reader
        .lines()
        .collect::<io::Result<Vec<_>>>()
        .with_context(|| format!("Failed to read {}", path.display()))?;

    let start = lines.len().saturating_sub(n);
    for line in &lines[start..] {
        println!("{line}");
    }

    Ok(())
}

/// Prints the last `n` lines then follows the log file for new output.
async fn tail_follow(path: &PathBuf, n: usize) -> Result<()> {
    // First print the tail.
    print_tail(path, n)?;

    // Now seek to end and poll for new content.
    let mut file =
        std::fs::File::open(path).with_context(|| format!("Failed to open {}", path.display()))?;
    file.seek(SeekFrom::End(0))
        .context("Failed to seek to end of log file")?;

    let mut reader = BufReader::new(file);
    let mut line_buf = String::new();

    println!("--- Following {} (Ctrl+C to stop) ---", path.display());

    loop {
        line_buf.clear();
        match reader.read_line(&mut line_buf) {
            Ok(0) => {
                // No new data — wait briefly before polling again.
                tokio::time::sleep(Duration::from_millis(200)).await;
            }
            Ok(_) => {
                // Trim the trailing newline for clean output.
                print!("{line_buf}");
            }
            Err(e) => {
                error!("Error reading log: {e}");
                eprintln!("Error reading log: {e}");
                break;
            }
        }
    }

    Ok(())
}
