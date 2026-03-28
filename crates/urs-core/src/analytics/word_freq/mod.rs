//! Word frequency analysis for scraped Reddit data.
//!
//! This module provides a configurable word frequency analyzer that extracts and counts words from
//! Reddit submissions, comments, and raw text. It supports stop word filtering, case normalization,
//! and minimum word length filtering.
//!
//! # Example
//!
//! ```
//! use urs_core::analytics::WordFrequencyAnalyzer;
//!
//! let analyzer = WordFrequencyAnalyzer::new()
//!     .min_word_length(3);
//!
//! let freqs = analyzer.analyze_str(&["hello world hello rust", "rust is great"]);
//! assert_eq!(freqs.unique_count(), 4); // hello, world, rust, great ("is" is a stop word)
//! ```

mod analyzer;
mod extractable;
mod frequencies;

pub use analyzer::WordFrequencyAnalyzer;
pub use frequencies::WordFrequencies;
