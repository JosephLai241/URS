//! Word frequency result container.
//!
//! Provides the [`WordFrequencies`] struct that holds sorted word-count pairs produced by the
//! analyzer.

use serde::{Deserialize, Serialize};

/// Sorted word frequency results.
///
/// Contains word-count pairs sorted by frequency in descending order. This is the output of
/// [`super::WordFrequencyAnalyzer::analyze`] and can be used for display, export, or passed to a
/// word cloud generator for visualization.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WordFrequencies {
    /// Word-count pairs sorted by frequency (descending).
    pub(super) entries: Vec<(String, u32)>,
}

impl WordFrequencies {
    /// Returns the frequency entries as a slice.
    #[must_use]
    pub fn entries(&self) -> &[(String, u32)] {
        &self.entries
    }

    /// Returns the top N most frequent words.
    ///
    /// If `n` exceeds the number of unique words, all entries are returned.
    #[must_use]
    pub fn top_n(&self, n: usize) -> &[(String, u32)] {
        let end = n.min(self.entries.len());
        &self.entries[..end]
    }

    /// Returns the total number of unique words.
    #[must_use]
    pub fn unique_count(&self) -> usize {
        self.entries.len()
    }

    /// Returns the total number of words counted (sum of all frequencies).
    #[must_use]
    pub fn total_count(&self) -> u32 {
        self.entries.iter().map(|(_, count)| count).sum()
    }

    /// Consumes the frequencies and returns the underlying word-count pairs.
    #[must_use]
    pub fn into_entries(self) -> Vec<(String, u32)> {
        self.entries
    }
}
