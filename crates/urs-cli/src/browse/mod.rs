//! Local web viewer for kicking off scrapes and viewing scraped Reddit data.
//!
//! This module provides an axum-based HTTP server that renders scraped data in a browser with rich
//! (Reddit-like) and raw (JSON/CSV) views and also enables users to kick off scrapes.

pub mod csv;
pub mod helpers;
pub mod loader;
pub mod markdown;
pub mod routes;
pub mod scrape;
pub mod server;
pub mod settings;
pub mod templates;
pub mod time;
pub mod views;
