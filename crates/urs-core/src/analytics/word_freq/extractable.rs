//! Text extraction trait and implementations for Reddit data models.
//!
//! Provides the [`TextExtractable`] trait that allows different Reddit data types to expose their
//! text content for word frequency analysis.

use crate::models::{Comment, Submission};

/// A type that can provide text content for frequency analysis.
///
/// Implement this trait for any data model whose text fields should be analyzed for word
/// frequencies.
pub trait TextExtractable {
    /// Extracts all analyzable text from this item.
    ///
    /// Returns a vector of string slices representing distinct text fields (e.g., title, body).
    /// Each field is tokenized separately but frequencies are accumulated together.
    fn extract_text(&self) -> Vec<&str>;
}

impl TextExtractable for Submission {
    fn extract_text(&self) -> Vec<&str> {
        let mut texts = vec![self.title.as_str()];

        if let Some(ref selftext) = self.selftext {
            if !selftext.is_empty() {
                texts.push(selftext.as_str());
            }
        }

        texts
    }
}

impl TextExtractable for Comment {
    fn extract_text(&self) -> Vec<&str> {
        // Skip deleted/removed comment placeholders.
        if self.body == "[deleted]" || self.body == "[removed]" {
            return vec![];
        }

        vec![self.body.as_str()]
    }
}
