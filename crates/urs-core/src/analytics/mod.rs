//! Analytics functionality for scraped Reddit data.
//!
//! This module provides text analysis utilities including word frequency extraction and word cloud
//! generation from scraped Reddit data.
//!
//! # Features
//!
//! - Word frequency analysis with stop word filtering and case normalization
//! - Word cloud image generation from word frequency data
//!
//! # Example
//!
//! ```
//! use urs_core::analytics::{WordFrequencyAnalyzer, ENGLISH_STOP_WORDS};
//!
//! let analyzer = WordFrequencyAnalyzer::new()
//!     .min_word_length(3);
//!
//! let freqs = analyzer.analyze_str(&["hello world hello rust", "rust is great"]);
//! assert_eq!(freqs.entries()[0], ("hello".to_string(), 2));
//! ```

mod stop_words;
mod word_freq;
mod wordcloud;

pub use stop_words::ENGLISH_STOP_WORDS;
pub use word_freq::{TextExtractable, WordFrequencies, WordFrequencyAnalyzer};
pub use wordcloud::WordCloudGenerator;
