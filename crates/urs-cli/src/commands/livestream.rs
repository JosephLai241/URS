//! Livestream command for monitoring real-time Reddit activity.
//!
//! Launches a full-screen TUI that displays a scrolling table of new comments or submissions as
//! they appear, with streaming file I/O for crash-safe data capture.

use std::fs;
use std::io::{BufWriter, Write};
use std::path::PathBuf;
use std::time::Duration;

use anyhow::{Context, Result};
use clap::{Parser, ValueEnum};
use urs_core::export::{ensure_dir, livestream_filename, output_dir};
use urs_core::scrapers::{LivestreamEvent, LivestreamSource, LivestreamTarget, Livestreamer};

use crate::helpers::create_client;
use crate::tui::app::App;
use crate::tui::event::run_event_loop;
use crate::tui::terminal::{restore_terminal, setup_terminal};

/// The source type for livestreaming.
#[derive(Debug, Clone, Copy, ValueEnum, Default)]
pub enum SourceType {
    /// Stream comments.
    #[default]
    Comments,
    /// Stream submissions.
    Submissions,
}

/// The target type for livestreaming.
#[derive(Debug, Clone, Copy, ValueEnum, Default)]
pub enum TargetType {
    /// Monitor a Redditor.
    Redditor,
    /// Monitor a Subreddit.
    #[default]
    Subreddit,
}

/// Livestream new Reddit activity in a TUI.
#[derive(Debug, Parser)]
pub struct LivestreamArgs {
    /// Maximum items to keep in the TUI scroll buffer.
    #[arg(short, long, default_value_t = 10_000)]
    pub buffer_size: usize,

    /// Poll interval in seconds.
    #[arg(short, long, default_value_t = 5)]
    pub interval: u64,

    /// Delete the output file on clean exit.
    #[arg(long, default_value_t = false)]
    pub nosave: bool,

    /// Stream comments or submissions.
    #[arg(short, long, default_value = "comments")]
    pub source: SourceType,

    /// Subreddit name or username to monitor.
    pub target: String,

    /// Whether the target is a Subreddit or Redditor.
    #[arg(short = 't', long, default_value = "subreddit")]
    pub r#type: TargetType,
}

/// Manages streaming file I/O for the livestream command.
///
/// Writes events to a temporary file as newline-delimited JSON. On clean exit, renames to the
/// final filename or deletes if `--nosave` is set.
pub struct StreamContext {
    /// Total items written to the file.
    file_count: usize,
    /// Whether to delete the file on exit.
    nosave: bool,
    /// The output directory.
    output_dir: PathBuf,
    /// Poll interval duration.
    poll_duration: Duration,
    /// Source name for the final filename.
    source_name: String,
    /// Target name for the final filename.
    target_name: String,
    /// Path to the temporary file.
    temp_path: PathBuf,
    /// Writer to the temporary output file.
    writer: BufWriter<fs::File>,
}

impl StreamContext {
    /// Creates a new stream context, opening a temporary file for writing.
    ///
    /// # Errors
    ///
    /// Returns an error if the output directory or temp file cannot be created.
    pub fn new(
        target_name: &str,
        source_name: &str,
        nosave: bool,
        poll_duration: Duration,
    ) -> Result<Self> {
        let dir = output_dir("livestreams");
        ensure_dir(&dir).context("Failed to create output directory")?;

        let temp_path = dir.join(format!(".{target_name}-{source_name}-livestream.tmp.jsonl"));

        let file = fs::File::create(&temp_path)
            .with_context(|| format!("Failed to create temp file: {}", temp_path.display()))?;

        Ok(Self {
            file_count: 0,
            nosave,
            output_dir: dir,
            poll_duration,
            source_name: source_name.to_string(),
            target_name: target_name.to_string(),
            temp_path,
            writer: BufWriter::new(file),
        })
    }

    /// Returns the poll interval duration.
    #[must_use]
    pub const fn poll_duration(&self) -> Duration {
        self.poll_duration
    }

    /// Appends events to the temporary file as newline-delimited JSON.
    ///
    /// # Errors
    ///
    /// Returns an error if serialization or writing fails.
    pub fn append_events(&mut self, events: &[LivestreamEvent]) -> Result<()> {
        for event in events {
            serde_json::to_writer(&mut self.writer, event).context("Failed to serialize event")?;
            self.writer
                .write_all(b"\n")
                .context("Failed to write newline")?;

            self.file_count += 1;
        }

        self.writer.flush().context("Failed to flush writer")?;

        Ok(())
    }

    /// Finalizes the output file.
    ///
    /// If `nosave` is set, deletes the temp file. Otherwise, renames it to the final filename
    /// based on the target, source, and item count.
    ///
    /// # Errors
    ///
    /// Returns an error if the file cannot be renamed or deleted.
    pub fn finalize(mut self) -> Result<Option<PathBuf>> {
        self.writer
            .flush()
            .context("Failed to flush writer during finalize")?;

        // Drop the writer to release the file handle before renaming/deleting.
        drop(self.writer);

        if self.nosave || self.file_count == 0 {
            fs::remove_file(&self.temp_path).with_context(|| {
                format!("Failed to remove temp file: {}", self.temp_path.display())
            })?;
            return Ok(None);
        }

        let filename = livestream_filename(&self.target_name, &self.source_name, self.file_count);
        let final_path = self.output_dir.join(format!("{filename}.jsonl"));

        fs::rename(&self.temp_path, &final_path).with_context(|| {
            format!(
                "Failed to rename {} to {}",
                self.temp_path.display(),
                final_path.display()
            )
        })?;

        Ok(Some(final_path))
    }
}

/// Runs the livestream command.
///
/// # Errors
///
/// Returns an error if authentication, terminal setup, or the event loop fails.
pub async fn run(args: LivestreamArgs) -> Result<()> {
    let client = create_client().await?;

    let target = match args.r#type {
        TargetType::Redditor => LivestreamTarget::Redditor(args.target.clone()),
        TargetType::Subreddit => LivestreamTarget::Subreddit(args.target.clone()),
    };

    let source = match args.source {
        SourceType::Comments => LivestreamSource::Comments,
        SourceType::Submissions => LivestreamSource::Submissions,
    };

    let mut streamer = Livestreamer::new(&client, target, source);
    let mut app = App::new(args.buffer_size);
    let mut ctx = StreamContext::new(
        &args.target,
        &source.to_string(),
        args.nosave,
        Duration::from_secs(args.interval),
    )?;

    let mut terminal = setup_terminal()?;
    let result = run_event_loop(&mut terminal, &mut app, &mut streamer, &mut ctx).await;
    restore_terminal(&mut terminal)?;

    let final_path = ctx.finalize()?;
    if let Some(path) = final_path {
        println!("Saved {} items to {}", app.total_count(), path.display());
    }

    result
}
