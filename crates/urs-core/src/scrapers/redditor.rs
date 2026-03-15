//! This module provides functionality to scrape Reddit user profiles and their various interaction
//! categories.

use tracing::{debug, info, warn};

use crate::client::RedditClient;
use crate::client::endpoints::RedditorEndpoint;
use crate::error::{Error, Result};
use crate::models::api::{CommentData, Listing, SubmissionData};
use crate::models::{Comment, InteractionData, Redditor, RedditorInteractions, Submission};

/// Scraper for Redditor (user) data.
///
/// Provides methods to fetch user profiles and all 14 interaction categories.
#[derive(Debug)]
pub struct RedditorScraper<'a> {
    /// The Reddit client for making authenticated API requests.
    client: &'a RedditClient,
}

impl<'a> RedditorScraper<'a> {
    /// Creates a new Redditor scraper.
    ///
    /// # Arguments
    ///
    /// * `client` - The authenticated Reddit client to use for requests
    #[must_use]
    pub const fn new(client: &'a RedditClient) -> Self {
        Self { client }
    }

    /// Fetches a user's profile information.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username (without u/ prefix)
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn about(&self, username: &str) -> Result<Redditor> {
        info!(username = username, "Fetching Redditor info...");

        let url = RedditorEndpoint::about(username);
        let response = self.client.get(&url).await?;

        // Response is wrapped in { kind: "t2", data: {...} }.
        let data = response.get("data").cloned().unwrap_or(response);
        let user: Redditor = serde_json::from_value(data)?;

        Ok(user)
    }

    /// Fetches a user's submissions.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username
    /// * `limit` - Maximum number of submissions to fetch
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn submissions(&self, username: &str, limit: usize) -> Result<Vec<Submission>> {
        info!(
            username = username,
            limit = limit,
            "Fetching Redditor submissions"
        );

        let mut submissions = Vec::new();
        let mut after: Option<String> = None;

        while submissions.len() < limit {
            let batch_limit = std::cmp::min(100, limit - submissions.len());
            let batch_limit_u32 = u32::try_from(batch_limit).unwrap_or(100);
            let url = RedditorEndpoint::submitted(username, batch_limit_u32, after.as_deref());

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
                "Fetched submissions batch"
            );

            after = listing.data.after;
            if after.is_none() || batch_len == 0 {
                break;
            }
        }

        submissions.truncate(limit);

        Ok(submissions)
    }

    /// Fetches a user's comments.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username
    /// * `limit` - Maximum number of comments to fetch
    ///
    /// # Errors
    ///
    /// Returns an error if the API request fails.
    pub async fn comments(&self, username: &str, limit: usize) -> Result<Vec<Comment>> {
        info!(
            username = username,
            limit = limit,
            "Fetching Redditor comments"
        );

        let mut comments = Vec::new();
        let mut after: Option<String> = None;

        while comments.len() < limit {
            let batch_limit = std::cmp::min(100, limit - comments.len());
            let batch_limit_u32 = u32::try_from(batch_limit).unwrap_or(100);
            let url = RedditorEndpoint::comments(username, batch_limit_u32, after.as_deref());

            let response = self.client.get(&url).await?;
            let listing: Listing<CommentData> = serde_json::from_value(response)?;

            let batch: Vec<Comment> = listing
                .data
                .children
                .into_iter()
                .map(|thing| Comment::from(thing.data))
                .collect();

            let batch_len = batch.len();
            comments.extend(batch);

            debug!(
                fetched = batch_len,
                total = comments.len(),
                "Fetched comments batch"
            );

            after = listing.data.after;
            if after.is_none() || batch_len == 0 {
                break;
            }
        }

        comments.truncate(limit);

        Ok(comments)
    }

    /// Fetches all interaction data for a user.
    ///
    /// This fetches the user's profile and all available interaction categories. Categories that
    /// are forbidden (i.e. downvoted for other users) will be marked as `Forbidden` rather than
    /// causing an error.
    ///
    /// # Arguments
    ///
    /// * `username` - The Reddit username
    /// * `limit` - Maximum number of items per category
    ///
    /// # Errors
    ///
    /// Returns an error if the user is not found or the API request fails.
    pub async fn all_interactions(
        &self,
        username: &str,
        limit: usize,
    ) -> Result<RedditorInteractions> {
        info!(
            username = username,
            limit = limit,
            "Fetching all Redditor interactions"
        );

        let mut interactions = RedditorInteractions::default();

        match self.about(username).await {
            Ok(user) => interactions.information = Some(user),
            Err(Error::NotFound(_)) => return Err(Error::NotFound(format!("User {username}"))),
            Err(e) => warn!(error = %e, "Failed to fetch user info"),
        }

        match self.comments(username, limit).await {
            Ok(comments) => interactions.comments = InteractionData::Data(comments),
            Err(Error::Forbidden(_)) => interactions.comments = InteractionData::Forbidden,
            Err(e) => warn!(error = %e, "Failed to fetch comments"),
        }

        match self.submissions(username, limit).await {
            Ok(subs) => interactions.submissions = InteractionData::Data(subs),
            Err(Error::Forbidden(_)) => interactions.submissions = InteractionData::Forbidden,
            Err(e) => warn!(error = %e, "Failed to fetch submissions"),
        }

        // Fetch private categories (accessible for the authenticated user).
        interactions.downvoted = self
            .fetch_private_category(username, "downvoted", limit)
            .await;
        interactions.upvoted = self
            .fetch_private_category(username, "upvoted", limit)
            .await;
        interactions.saved = self.fetch_private_category(username, "saved", limit).await;
        interactions.hidden = self.fetch_private_category(username, "hidden", limit).await;
        interactions.gildings = self
            .fetch_private_category(username, "gilded/given", limit)
            .await;

        info!("Redditor interactions fetch complete");

        Ok(interactions)
    }

    /// Fetches a private interaction category, returning Forbidden if access denied.
    async fn fetch_private_category(
        &self,
        username: &str,
        category: &str,
        limit: u32,
    ) -> InteractionData<serde_json::Value> {
        let url = RedditorEndpoint::private_category(username, category, limit);

        match self.client.get(&url).await {
            Ok(response) => {
                if let Ok(listing) = serde_json::from_value::<Listing<serde_json::Value>>(response)
                {
                    let items: Vec<serde_json::Value> = listing
                        .data
                        .children
                        .into_iter()
                        .map(|thing| thing.data)
                        .collect();
                    InteractionData::Data(items)
                } else {
                    InteractionData::Data(vec![])
                }
            }
            Err(Error::Forbidden(_)) => InteractionData::Forbidden,
            Err(e) => {
                warn!(category = category, error = %e, "Failed to fetch category");
                InteractionData::Data(vec![])
            }
        }
    }
}

#[cfg(test)]
mod tests {
    // TODO: Add tests here.
}
