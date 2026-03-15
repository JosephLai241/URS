//! This module provides functionality to scrape Subreddit listings,
//! search results, and Subreddit information.

use tracing::{debug, info};

use crate::client::RedditClient;
use crate::client::endpoints::{SubredditEndpoint, SubredditSort, TimeFilter};
use crate::error::Result;
use crate::models::api::{Listing, SubmissionData};
use crate::models::{Submission, Subreddit, SubredditRules};

/// Scraper for Subreddit data.
///
/// Provides methods to fetch posts from Subreddits using various sorting
/// options, search within Subreddits, and retrieve Subreddit metadata.
#[derive(Debug)]
pub struct SubredditScraper<'a> {
    /// The Reddit client for making authenticated API requests.
    client: &'a RedditClient,
}

impl<'a> SubredditScraper<'a> {
    /// Creates a new Subreddit scraper.
    ///
    /// # Arguments
    ///
    /// * `client` - The authenticated Reddit client to use for requests
    #[must_use]
    pub const fn new(client: &'a RedditClient) -> Self {
        Self { client }
    }

    /// Fetches hot posts from a Subreddit.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `limit` - Maximum number of posts to fetch
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn hot(&self, subreddit: &str, limit: usize) -> Result<Vec<Submission>> {
        self.fetch_listing(subreddit, SubredditSort::Hot, None, limit)
            .await
    }

    /// Fetches new posts from a Subreddit.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `limit` - Maximum number of posts to fetch
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn new_posts(&self, subreddit: &str, limit: usize) -> Result<Vec<Submission>> {
        self.fetch_listing(subreddit, SubredditSort::New, None, limit)
            .await
    }

    /// Fetches top posts from a Subreddit.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `time` - Time filter (hour, day, week, month, year, all)
    /// * `limit` - Maximum number of posts to fetch
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn top(
        &self,
        subreddit: &str,
        time: TimeFilter,
        limit: usize,
    ) -> Result<Vec<Submission>> {
        self.fetch_listing(subreddit, SubredditSort::Top, Some(time), limit)
            .await
    }

    /// Fetches controversial posts from a Subreddit.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `time` - Time filter (hour, day, week, month, year, all)
    /// * `limit` - Maximum number of posts to fetch
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn controversial(
        &self,
        subreddit: &str,
        time: TimeFilter,
        limit: usize,
    ) -> Result<Vec<Submission>> {
        self.fetch_listing(subreddit, SubredditSort::Controversial, Some(time), limit)
            .await
    }

    /// Fetches rising posts from a Subreddit.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `limit` - Maximum number of posts to fetch
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn rising(&self, subreddit: &str, limit: usize) -> Result<Vec<Submission>> {
        self.fetch_listing(subreddit, SubredditSort::Rising, None, limit)
            .await
    }

    /// Searches for posts in a Subreddit.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    /// * `query` - The search query
    /// * `time` - Optional time filter
    /// * `limit` - Maximum number of posts to fetch
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn search(
        &self,
        subreddit: &str,
        query: &str,
        time: Option<TimeFilter>,
        limit: usize,
    ) -> Result<Vec<Submission>> {
        info!(
            subreddit = subreddit,
            query = query,
            limit = limit,
            "Searching Subreddit"
        );

        let mut submissions = Vec::new();
        let mut after: Option<String> = None;

        while submissions.len() < limit {
            let batch_limit = std::cmp::min(100, limit - submissions.len());
            let batch_limit_u32 = u32::try_from(batch_limit).unwrap_or(100);
            let url = SubredditEndpoint::search(
                subreddit,
                query,
                time,
                batch_limit_u32,
                after.as_deref(),
            );

            let response = self.client.get(&url).await?;
            let listing: Listing<SubmissionData> = serde_json::from_value(response)?;

            let batch: Vec<Submission> = listing
                .data
                .children
                .into_iter()
                .map(|thing| Submission::from(thing.data))
                .collect();

            let batch_len = batch.len();
            submissions.extend(batch);

            debug!(
                fetched = batch_len,
                total = submissions.len(),
                "Fetched search results batch"
            );

            after = listing.data.after;
            if after.is_none() || batch_len == 0 {
                break;
            }
        }

        submissions.truncate(limit);

        info!(count = submissions.len(), "Search complete");

        Ok(submissions)
    }

    /// Fetches Subreddit information.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn about(&self, subreddit: &str) -> Result<Subreddit> {
        info!(subreddit = subreddit, "fetching Subreddit info");

        let url = SubredditEndpoint::about(subreddit);
        let response = self.client.get(&url).await?;

        // The response is wrapped in { kind: "t5", data: {...} }.
        let data = response.get("data").cloned().unwrap_or(response);

        let subreddit: Subreddit = serde_json::from_value(data)?;

        Ok(subreddit)
    }

    /// Fetches Subreddit rules.
    ///
    /// # Arguments
    ///
    /// * `subreddit` - The Subreddit name (without r/ prefix)
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn rules(&self, subreddit: &str) -> Result<SubredditRules> {
        info!(subreddit = subreddit, "fetching Subreddit rules");

        let url = SubredditEndpoint::rules(subreddit);
        let response = self.client.get(&url).await?;

        let rules: SubredditRules = serde_json::from_value(response)?;

        Ok(rules)
    }

    /// Internal method to fetch a listing with pagination.
    async fn fetch_listing(
        &self,
        subreddit: &str,
        sort: SubredditSort,
        time: Option<TimeFilter>,
        limit: usize,
    ) -> Result<Vec<Submission>> {
        info!(
            subreddit = subreddit,
            sort = %sort,
            limit = limit,
            "Fetching Subreddit listing"
        );

        let mut submissions = Vec::new();
        let mut after: Option<String> = None;

        while submissions.len() < limit {
            let batch_limit = std::cmp::min(100, limit - submissions.len());
            let batch_limit_u32 = u32::try_from(batch_limit).unwrap_or(100);
            let url = SubredditEndpoint::listing(
                subreddit,
                sort,
                time,
                batch_limit_u32,
                after.as_deref(),
            );

            let response = self.client.get(&url).await?;
            let listing: Listing<SubmissionData> = serde_json::from_value(response)?;

            let batch: Vec<Submission> = listing
                .data
                .children
                .into_iter()
                .map(|thing| Submission::from(thing.data))
                .collect();

            let batch_len = batch.len();
            submissions.extend(batch);

            debug!(
                fetched = batch_len,
                total = submissions.len(),
                "Fetched listing batch"
            );

            after = listing.data.after;
            if after.is_none() || batch_len == 0 {
                break;
            }
        }

        submissions.truncate(limit);

        info!(count = submissions.len(), "Listing fetch complete");

        Ok(submissions)
    }
}

#[cfg(test)]
mod tests {
    // TODO: Add tests here.
}
