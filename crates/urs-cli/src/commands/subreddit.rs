//! Subreddit scraping command.
//!
//! Scrapes posts from a Subreddit by category (hot, new, top, controversial, rising, or search)
//! and exports results to JSON or CSV.

use std::path::PathBuf;

use anyhow::{Result, bail};
use clap::{Args, ValueEnum};
use colored::Colorize;
use serde::Serialize;
use tracing::{debug, info, warn};
use urs_core::client::endpoints::TimeFilter;
use urs_core::export::{CsvExporter, JsonExporter, ensure_dir, output_dir, subreddit_filename};
use urs_core::models::{Submission, SubredditRules};
use urs_core::scrapers::SubredditScraper;

use crate::helpers::{create_client, create_spinner};

/// Arguments for the `subreddit` subcommand.
#[derive(Debug, Args)]
pub struct SubredditArgs {
    /// Subreddit name (without the `r/` prefix).
    pub subreddit: String,

    /// Sort category for posts.
    pub category: Category,

    /// Number of posts to scrape.
    #[arg(default_value_t = 25)]
    pub count: usize,

    /// Time filter for top/controversial categories.
    #[arg(short, long, default_value = "all")]
    pub time: CliTimeFilter,

    /// Search query (required when category is `search`).
    #[arg(short, long)]
    pub query: Option<String>,

    /// Include Subreddit rules in the output.
    #[arg(long, default_value_t = false)]
    pub rules: bool,

    /// Custom output directory.
    #[arg(short, long)]
    pub output: Option<PathBuf>,

    /// Export as CSV instead of JSON.
    #[arg(long, default_value_t = false)]
    pub csv: bool,
}

/// Post sort category.
#[derive(Debug, Clone, ValueEnum)]
pub enum Category {
    /// Hot posts (default Reddit view).
    Hot,
    /// Newest posts.
    New,
    /// Top posts (use `--time` to filter).
    Top,
    /// Controversial posts (use `--time` to filter).
    Controversial,
    /// Rising posts.
    Rising,
    /// Search posts (requires `--query`).
    Search,
}

/// CLI-compatible time filter enum.
#[derive(Debug, Clone, Default, ValueEnum)]
pub enum CliTimeFilter {
    /// All time.
    #[default]
    All,
    /// Past hour.
    Hour,
    /// Past 24 hours.
    Day,
    /// Past week.
    Week,
    /// Past month.
    Month,
    /// Past year.
    Year,
}

impl CliTimeFilter {
    /// Converts to the core library's `TimeFilter` type.
    const fn to_core(&self) -> TimeFilter {
        match self {
            Self::All => TimeFilter::All,
            Self::Hour => TimeFilter::Hour,
            Self::Day => TimeFilter::Day,
            Self::Week => TimeFilter::Week,
            Self::Month => TimeFilter::Month,
            Self::Year => TimeFilter::Year,
        }
    }
}

/// Combined output for Subreddit scrapes that include rules.
#[derive(Debug, Serialize)]
struct SubredditOutput {
    posts: Vec<Submission>,
    rules: SubredditRules,
}

/// Executes the Subreddit scraping command.
///
/// # Errors
///
/// Returns an error if:
/// - Category is `search` but `--query` is not provided
/// - Authentication fails
/// - The Reddit API request fails
/// - File export fails
pub async fn run(args: SubredditArgs) -> Result<()> {
    let category_str = format!("{:?}", args.category).to_lowercase();

    if matches!(args.category, Category::Search) && args.query.is_none() {
        warn!("Search category used without --query flag");
        bail!("The --query flag is required when using the 'search' category");
    }

    println!(
        "{} {} {} {} {} {}",
        "Scraping".bright_green(),
        format!("r/{}", args.subreddit).bold(),
        "—".dimmed(),
        category_str.bright_yellow(),
        "—".dimmed(),
        format!("{} posts", args.count).bright_cyan(),
    );

    info!(
        subreddit = %args.subreddit,
        category = %category_str,
        count = args.count,
        "Starting subreddit scrape"
    );

    let spinner = create_spinner("Authenticating with Reddit...");
    let client = create_client().await?;
    let scraper = SubredditScraper::new(&client);
    spinner.set_message("Fetching posts...");

    let time = args.time.to_core();
    let posts = match args.category {
        Category::Hot => scraper.hot(&args.subreddit, args.count).await?,
        Category::New => scraper.new_posts(&args.subreddit, args.count).await?,
        Category::Top => scraper.top(&args.subreddit, time, args.count).await?,
        Category::Controversial => {
            scraper
                .controversial(&args.subreddit, time, args.count)
                .await?
        }
        Category::Rising => scraper.rising(&args.subreddit, args.count).await?,
        Category::Search => {
            let query = args.query.as_deref().expect("validated above");
            scraper
                .search(&args.subreddit, query, Some(time), args.count)
                .await?
        }
    };

    let rules = if args.rules {
        spinner.set_message("Fetching Subreddit rules...");
        Some(scraper.rules(&args.subreddit).await?)
    } else {
        None
    };

    spinner.set_message("Exporting results...");

    let time_str = if matches!(args.category, Category::Top | Category::Controversial) {
        Some(time.as_str())
    } else {
        None
    };

    let dir = args.output.unwrap_or_else(|| output_dir("subreddits"));
    ensure_dir(&dir)?;

    let base_name = subreddit_filename(
        &args.subreddit,
        &category_str,
        posts.len(),
        time_str,
        args.rules,
    );

    let format = if args.csv { "CSV" } else { "JSON" };
    debug!(format = format, "Exporting results");

    if args.csv {
        let path = dir.join(format!("{base_name}.csv"));
        CsvExporter::new().export_submissions(&posts, &path)?;
        spinner.finish_and_clear();
        print_summary(&path, posts.len());
    } else {
        let path = dir.join(format!("{base_name}.json"));
        let exporter = JsonExporter::new();

        if let Some(rules) = rules {
            let output = SubredditOutput { posts, rules };
            exporter.export_to_file(&output, &path)?;
        } else {
            exporter.export_to_file(&posts, &path)?;
        }

        spinner.finish_and_clear();
        print_summary(&path, 0);
    }

    info!("Subreddit scrape complete");

    Ok(())
}

/// Prints a summary of the completed scrape.
fn print_summary(path: &std::path::Path, count: usize) {
    println!(
        "\n{} {}",
        "✓".bright_green().bold(),
        "Scrape complete!".bold()
    );

    if count > 0 {
        println!(
            "  {} {} posts scraped",
            "→".dimmed(),
            count.to_string().bright_cyan()
        );
    }

    println!(
        "  {} Saved to {}",
        "→".dimmed(),
        path.display().to_string().bright_yellow()
    );
}
