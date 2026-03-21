//! Livestream SSE (Server-Sent Events) routes.
//!
//! Provides endpoints that stream new comments or submissions in real-time from Subreddits or
//! Redditors using Server-Sent Events.
//!
//! The `Livestreamer` borrows `&RedditClient`, so it cannot outlive the borrow. To produce a
//! `'static` SSE stream, each handler clones the `Arc<RedditClient>` (via `AppState`) into the
//! `async-stream` generator closure, then creates the `Livestreamer` inside the closure where it
//! borrows from the captured `Arc`.

use std::convert::Infallible;
use std::sync::Arc;
use std::time::Duration;

use async_stream::stream;
use axum::Router;
use axum::extract::{Path, Query, State};
use axum::response::Sse;
use axum::response::sse::{Event, KeepAlive};
use axum::routing::get;
use tokio_stream::Stream;
use tracing::{info, instrument, warn};
use urs_core::client::RedditClient;
use urs_core::scrapers::{LivestreamSource, LivestreamTarget, Livestreamer};

use crate::extractors::LivestreamParams;
use crate::state::AppState;

/// Builds the livestream router.
///
/// # Routes
///
/// - `GET /subreddits/:name` — Stream Subreddit activity (SSE)
/// - `GET /redditors/:username` — Stream Redditor activity (SSE)
pub fn router() -> Router<AppState> {
    Router::new()
        .route("/redditors/{username}", get(redditor_stream))
        .route("/subreddits/{name}", get(subreddit_stream))
}

/// `GET /api/livestream/subreddits/{name}`
///
/// Streams new comments or submissions from a Subreddit as SSE events.
#[instrument(skip(state))]
async fn subreddit_stream(
    State(state): State<AppState>,
    Path(name): Path<String>,
    Query(params): Query<LivestreamParams>,
) -> Sse<impl Stream<Item = Result<Event, Infallible>>> {
    let interval = params.interval();
    let source = params.source();
    let target = LivestreamTarget::Subreddit(name);

    Sse::new(make_stream(state.client_arc(), target, source, interval))
        .keep_alive(KeepAlive::default())
}

/// `GET /api/livestream/redditors/{username}`
///
/// Streams new comments or submissions from a Redditor as SSE events.
#[instrument(skip(state))]
async fn redditor_stream(
    State(state): State<AppState>,
    Path(username): Path<String>,
    Query(params): Query<LivestreamParams>,
) -> Sse<impl Stream<Item = Result<Event, Infallible>>> {
    let interval = params.interval();
    let source = params.source();
    let target = LivestreamTarget::Redditor(username);

    Sse::new(make_stream(state.client_arc(), target, source, interval))
        .keep_alive(KeepAlive::default())
}

/// Creates an SSE event stream that polls the livestreamer.
///
/// The `Arc<RedditClient>` is moved into the generator closure so the `Livestreamer` can borrow
/// from it without lifetime issues. The `Livestreamer` is created inside the closure, borrowing
/// from the captured `Arc`.
fn make_stream(
    client: Arc<RedditClient>,
    target: LivestreamTarget,
    source: LivestreamSource,
    interval: Duration,
) -> impl Stream<Item = Result<Event, Infallible>> {
    stream! {
        info!(target = %target, source = %source, ?interval, "Starting livestream");
        let mut streamer = Livestreamer::new(&client, target, source);

        loop {
            match streamer.poll().await {
                Ok(events) => {
                    for event in events {
                        let json = serde_json::to_string(&event).unwrap_or_default();
                        yield Ok(Event::default().data(json));
                    }
                }
                Err(err) => {
                    warn!(error = %err, "Livestream poll error");

                    let error_json = serde_json::json!({ "error": err.to_string() });

                    yield Ok(Event::default().event("error").data(error_json.to_string()));
                }
            }

            tokio::time::sleep(interval).await;
        }
    }
}
