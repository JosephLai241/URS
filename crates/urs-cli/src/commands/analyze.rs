//! Word frequency analysis command.
//!
//! Analyzes scraped Reddit data files to produce word frequency tables and optional word cloud
//! images. Supports JSON (Subreddit/comments/Redditor) scrape files.

use std::path::PathBuf;

use anyhow::{Context, Result, bail};
use clap::Args;
use colored::Colorize;
use tracing::{debug, info};
use urs_core::analytics::{WordCloudGenerator, WordFrequencies, WordFrequencyAnalyzer};
use urs_core::models::{Comment, InteractionData};

use crate::browse::loader::{self, ScrapeData, ScrapeType};

/// Arguments for the `analyze` subcommand.
#[derive(Debug, Args)]
#[command(after_long_help = "\
\x1b[1;4mExamples:\x1b[0m

  Analyze word frequencies in a Subreddit scrape:
    urs analyze scrapes/2026-03-21/subreddits/rust-hot-50.json

  Show only the top 20 words:
    urs analyze scrapes/2026-03-21/subreddits/rust-hot-50.json --top 20

  Filter out short words:
    urs analyze scrapes/2026-03-21/comments/post.json --min-length 4

  Generate a word cloud image:
    urs analyze scrapes/2026-03-21/subreddits/rust-hot-50.json --wordcloud

  Save the word cloud to a specific path:
    urs analyze scrapes/2026-03-21/subreddits/rust-hot-50.json --wordcloud -o wordcloud.png

\x1b[1;4mSupported file types:\x1b[0m

  Subreddit scrapes    JSON files containing submission data
  Comment scrapes      JSON files containing comment threads
  Redditor scrapes     JSON files containing Redditor interaction data")]
pub struct AnalyzeArgs {
    /// Path to the scrape file to analyze.
    pub file: PathBuf,

    /// Minimum word length to include in results.
    #[arg(short, long, default_value_t = 3)]
    pub min_length: usize,

    /// Output path for the word cloud image (defaults to `<input>-wordcloud.png`).
    #[arg(short, long)]
    pub output: Option<PathBuf>,

    /// Number of top words to display (default: 25).
    #[arg(short, long, default_value_t = 25)]
    pub top: usize,

    /// Generate a word cloud image.
    #[arg(long, default_value_t = false)]
    pub wordcloud: bool,
}

/// Executes the analyze command.
///
/// # Errors
///
/// Returns an error if:
/// - The input file does not exist or cannot be parsed
/// - The file type is unsupported (CSV, livestream)
/// - Word cloud generation or saving fails
pub fn run(args: AnalyzeArgs) -> Result<()> {
    if !args.file.exists() {
        bail!("File not found: {}", args.file.display());
    }

    let scrape_type = loader::detect_type(&args.file);

    if matches!(scrape_type, ScrapeType::Csv | ScrapeType::Livestream) {
        bail!("Only Subreddit, comment, and Redditor scrape files are supported for analysis");
    }

    info!(
        file = %args.file.display(),
        scrape_type = ?scrape_type,
        "Starting word frequency analysis"
    );

    println!(
        "{} {}",
        "Analyzing".bright_green(),
        args.file.display().to_string().bold(),
    );

    let analyzer = WordFrequencyAnalyzer::new().min_word_length(args.min_length);

    let data = loader::parse_file(&args.file, scrape_type)
        .with_context(|| format!("Failed to parse {}", args.file.display()))?;

    let frequencies = analyze_scrape_data(&analyzer, &data);

    print_frequency_table(&frequencies, args.top);

    if args.wordcloud {
        generate_wordcloud(&frequencies, &args.file, args.output)?;
    }

    info!("Word frequency analysis complete");

    Ok(())
}

/// Analyzes scrape data and returns word frequencies.
///
/// Extracts text from submissions, comments, or Redditor data and runs word frequency analysis.
pub fn analyze_scrape_data(analyzer: &WordFrequencyAnalyzer, data: &ScrapeData) -> WordFrequencies {
    match data {
        ScrapeData::Comments { comments, .. } => {
            let all_comments = flatten_comments(comments);
            debug!(count = all_comments.len(), "Analyzing comments");

            analyzer.analyze(&all_comments)
        }
        ScrapeData::Redditor(interactions) => {
            let submissions = match &interactions.submissions {
                InteractionData::Data(data) => data.clone(),
                InteractionData::Forbidden => vec![],
            };
            let comments = match &interactions.comments {
                InteractionData::Data(data) => data.clone(),
                InteractionData::Forbidden => vec![],
            };

            debug!(
                submissions = submissions.len(),
                comments = comments.len(),
                "Analyzing Redditor data"
            );

            // Combine all text sources and analyze together.
            let all_texts: Vec<&str> = submissions
                .iter()
                .flat_map(|s| {
                    let mut t = vec![s.title.as_str()];
                    if let Some(ref st) = s.selftext {
                        if !st.is_empty() {
                            t.push(st.as_str());
                        }
                    }
                    t
                })
                .chain(
                    comments
                        .iter()
                        .filter(|c| c.body != "[deleted]" && c.body != "[removed]")
                        .map(|c| c.body.as_str()),
                )
                .collect();

            analyzer.analyze_str(&all_texts)
        }
        ScrapeData::Submissions { posts, .. } => {
            debug!(count = posts.len(), "Analyzing submissions");
            analyzer.analyze(posts)
        }
        ScrapeData::Csv { .. } | ScrapeData::Livestream(_) => {
            debug!("Unsupported data type for analysis");
            analyzer.analyze_str(&[])
        }
    }
}

/// Prints a formatted word frequency table to stdout.
fn print_frequency_table(frequencies: &WordFrequencies, top: usize) {
    let top_entries = frequencies.top_n(top);

    println!(
        "\n{} {} unique words, {} total",
        "Results:".bright_yellow().bold(),
        frequencies.unique_count().to_string().bright_cyan(),
        frequencies.total_count().to_string().bright_cyan(),
    );

    if top_entries.is_empty() {
        println!("\n  No words found matching the criteria.");
        return;
    }

    println!();
    println!(
        "  {:<6}  {:<30}  {}",
        "Rank".dimmed(),
        "Word".dimmed(),
        "Count".dimmed(),
    );
    println!("  {}", "─".repeat(50).dimmed());

    for (i, (word, count)) in top_entries.iter().enumerate() {
        println!(
            "  {:<6}  {:<30}  {}",
            format!("#{}", i + 1).dimmed(),
            word.bright_white(),
            count.to_string().bright_cyan(),
        );
    }

    if frequencies.unique_count() > top {
        println!(
            "\n  {} {} more words not shown (use --top to see more)",
            "...".dimmed(),
            (frequencies.unique_count() - top).to_string().dimmed(),
        );
    }
}

/// Generates and saves a word cloud image.
fn generate_wordcloud(
    frequencies: &WordFrequencies,
    input_file: &std::path::Path,
    output: Option<PathBuf>,
) -> Result<()> {
    let output_path = output.unwrap_or_else(|| {
        let stem = input_file
            .file_stem()
            .and_then(|s| s.to_str())
            .unwrap_or("output");
        input_file.with_file_name(format!("{stem}-wordcloud.png"))
    });

    println!("\n{} word cloud...", "Generating".bright_green());

    let generator = WordCloudGenerator::new();
    generator
        .save(frequencies, &output_path)
        .with_context(|| format!("Failed to save word cloud to {}", output_path.display()))?;

    println!(
        "{} {}",
        "✓".bright_green().bold(),
        format!("Word cloud saved to {}", output_path.display()).bold(),
    );

    Ok(())
}

/// Recursively flattens nested comment trees into a single vector.
fn flatten_comments(comments: &[Comment]) -> Vec<Comment> {
    let mut result = Vec::new();
    for comment in comments {
        result.push(comment.clone());

        if !comment.replies.is_empty() {
            result.extend(flatten_comments(&comment.replies));
        }
    }

    result
}
