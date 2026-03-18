//! Local web viewer for scraped Reddit data.
//!
//! This module provides an axum-based HTTP server that renders scraped data in a browser with rich
//! (Reddit-like) and raw (JSON/CSV) view modes.

pub mod loader;
pub mod markdown;
pub mod routes;
pub mod server;
pub mod time;
