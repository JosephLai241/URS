//! Background scrape execution functions.
//!
//! These functions run as spawned tasks, performing the actual scraping and exporting work while
//! updating the shared task map with progress.

use std::sync::Arc;

use dashmap::DashMap;
use urs_core::client::RedditClient;
use urs_core::client::endpoints::TimeFilter;
use urs_core::export::{
    CsvExporter, JsonExporter, comments_filename, ensure_dir, output_dir_with_base,
    redditor_filename, subreddit_filename,
};
use urs_core::models::CommentsResult;
use urs_core::scrapers::{CommentsScraper, RedditorScraper, SubredditScraper};

use super::super::server::ScrapeTask;
use super::helpers::{
    CommentsScrapeParams, RedditorScrapeParams, SubredditOutput, SubredditScrapeParams,
    complete_task, extract_title_from_url, fail_task, parse_time_filter, update_task,
};

/// Runs a Subreddit scrape as a background task, updating the shared task map.
#[allow(clippy::too_many_lines)]
pub async fn run_subreddit_scrape(
    client: Arc<RedditClient>,
    scrapes_dir: Arc<std::path::PathBuf>,
    params: SubredditScrapeParams,
    tasks: Arc<DashMap<String, ScrapeTask>>,
    task_id: String,
) {
    let count = params.count.unwrap_or(25);
    let use_csv = params.format.as_deref() == Some("csv");
    let include_rules = params.rules.as_deref() == Some("true");
    let time = params
        .time
        .as_deref()
        .map_or(TimeFilter::All, parse_time_filter);
    let category = params.category.clone();

    // Fetch Subreddit info.
    let scraper = SubredditScraper::new(&client);
    let about = match scraper.about(&params.subreddit).await {
        Ok(info) => info,
        Err(e) => {
            fail_task(
                &tasks,
                &task_id,
                &format!(
                    "r/{} does not exist or is inaccessible: {e}",
                    params.subreddit
                ),
            );
            return;
        }
    };

    // Fetch posts.
    update_task(&tasks, &task_id, "fetching", "Fetching posts...", 1);
    let posts = match category.as_str() {
        "hot" => scraper.hot(&params.subreddit, count).await,
        "new" => scraper.new_posts(&params.subreddit, count).await,
        "top" => scraper.top(&params.subreddit, time, count).await,
        "controversial" => scraper.controversial(&params.subreddit, time, count).await,
        "rising" => scraper.rising(&params.subreddit, count).await,
        "search" => {
            let query = params.query.as_deref().unwrap_or("");
            scraper
                .search(&params.subreddit, query, Some(time), count)
                .await
        }
        _ => {
            fail_task(&tasks, &task_id, &format!("Unknown category: {category}"));
            return;
        }
    };

    let posts = match posts {
        Ok(p) => p,
        Err(e) => {
            fail_task(&tasks, &task_id, &format!("Failed to fetch posts: {e}"));
            return;
        }
    };

    // Fetch rules if needed.
    let rules = if include_rules {
        update_task(
            &tasks,
            &task_id,
            "fetching",
            "Fetching Subreddit rules...",
            1,
        );
        match scraper.rules(&params.subreddit).await {
            Ok(r) => Some(r),
            Err(e) => {
                tracing::warn!(error = %e, "Failed to fetch Subreddit rules, continuing without them");
                None
            }
        }
    } else {
        None
    };

    // Export the scrape.
    update_task(&tasks, &task_id, "exporting", "Exporting results...", 2);
    let dir = output_dir_with_base(&scrapes_dir, "subreddits");
    if let Err(e) = ensure_dir(&dir) {
        fail_task(
            &tasks,
            &task_id,
            &format!("Failed to create output directory: {e}"),
        );
        return;
    }

    let time_str = if matches!(category.as_str(), "top" | "controversial") {
        Some(time.as_str())
    } else {
        None
    };

    let base_name = subreddit_filename(
        &params.subreddit,
        &category,
        posts.len(),
        time_str,
        include_rules,
    );

    let export_result = if use_csv {
        let path = dir.join(format!("{base_name}.csv"));
        CsvExporter::new()
            .export_submissions(&posts, &path)
            .map(|()| path)
    } else {
        let path = dir.join(format!("{base_name}.json"));
        let output = SubredditOutput {
            information: about,
            rules,
            submissions: posts,
        };
        JsonExporter::new()
            .export_to_file(&output, &path)
            .map(|()| path)
    };

    match export_result {
        Ok(path) => {
            let rel = path
                .strip_prefix(scrapes_dir.as_ref())
                .unwrap_or(&path)
                .to_string_lossy()
                .to_string();
            complete_task(&tasks, &task_id, &rel);
        }
        Err(e) => {
            fail_task(&tasks, &task_id, &format!("Failed to export: {e}"));
        }
    }
}

/// Runs a comments scrape as a background task, updating the shared task map.
pub async fn run_comments_scrape(
    client: Arc<RedditClient>,
    scrapes_dir: Arc<std::path::PathBuf>,
    params: CommentsScrapeParams,
    tasks: Arc<DashMap<String, ScrapeTask>>,
    task_id: String,
) {
    let count = params.count.unwrap_or(0);
    let raw = params.raw.as_deref() == Some("true");

    // Validate the submission.
    let scraper = CommentsScraper::new(&client);
    if let Err(e) = scraper.validate_url(&params.url).await {
        fail_task(
            &tasks,
            &task_id,
            &format!("Submission does not exist or is inaccessible: {e}"),
        );
        return;
    }

    // Fetch the submission.
    update_task(&tasks, &task_id, "fetching", "Fetching comments...", 1);
    let limit = if count == 0 { None } else { Some(count) };
    let structured = !raw;
    let (submission, comments, total) = match scraper.from_url(&params.url, limit, structured).await
    {
        Ok(result) => result,
        Err(e) => {
            fail_task(&tasks, &task_id, &format!("Failed to fetch comments: {e}"));
            return;
        }
    };

    // Export the scrape.
    update_task(&tasks, &task_id, "exporting", "Exporting results...", 2);
    let dir = output_dir_with_base(&scrapes_dir, "comments");
    if let Err(e) = ensure_dir(&dir) {
        fail_task(
            &tasks,
            &task_id,
            &format!("Failed to create output directory: {e}"),
        );
        return;
    }

    let title = extract_title_from_url(&params.url);
    let all_comments = count == 0;
    let filename = comments_filename(&title, total, all_comments, raw);
    let path = dir.join(format!("{filename}.json"));

    let result = CommentsResult {
        submission,
        comments,
    };
    match JsonExporter::new().export_to_file(&result, &path) {
        Ok(()) => {
            let rel = path
                .strip_prefix(scrapes_dir.as_ref())
                .unwrap_or(&path)
                .to_string_lossy()
                .to_string();
            complete_task(&tasks, &task_id, &rel);
        }
        Err(e) => {
            fail_task(&tasks, &task_id, &format!("Failed to export: {e}"));
        }
    }
}

/// Runs a Redditor scrape as a background task, updating the shared task map.
pub async fn run_redditor_scrape(
    client: Arc<RedditClient>,
    scrapes_dir: Arc<std::path::PathBuf>,
    params: RedditorScrapeParams,
    tasks: Arc<DashMap<String, ScrapeTask>>,
    task_id: String,
) {
    let count = params.count.unwrap_or(25);

    // Validate the Redditor.
    let scraper = RedditorScraper::new(&client);
    if let Err(e) = scraper.about(&params.username).await {
        fail_task(
            &tasks,
            &task_id,
            &format!("u/{} does not exist or is suspended: {e}", params.username),
        );
        return;
    }

    // Fetch the Redditor.
    update_task(
        &tasks,
        &task_id,
        "fetching",
        &format!("Fetching interactions for u/{}...", params.username),
        1,
    );
    let interactions = match scraper.all_interactions(&params.username, count).await {
        Ok(i) => i,
        Err(e) => {
            fail_task(
                &tasks,
                &task_id,
                &format!("Failed to fetch Redditor data: {e}"),
            );
            return;
        }
    };

    // Export the scrape.
    update_task(&tasks, &task_id, "exporting", "Exporting results...", 2);
    let dir = output_dir_with_base(&scrapes_dir, "redditors");
    if let Err(e) = ensure_dir(&dir) {
        fail_task(
            &tasks,
            &task_id,
            &format!("Failed to create output directory: {e}"),
        );
        return;
    }

    let filename = redditor_filename(&params.username, count);
    let path = dir.join(format!("{filename}.json"));

    match JsonExporter::new().export_to_file(&interactions, &path) {
        Ok(()) => {
            let rel = path
                .strip_prefix(scrapes_dir.as_ref())
                .unwrap_or(&path)
                .to_string_lossy()
                .to_string();
            complete_task(&tasks, &task_id, &rel);
        }
        Err(e) => {
            fail_task(&tasks, &task_id, &format!("Failed to export: {e}"));
        }
    }
}
