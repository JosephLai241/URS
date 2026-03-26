//! Word frequency analyzer with configurable filtering.
//!
//! Provides the [`WordFrequencyAnalyzer`] struct that tokenizes text and produces word frequency
//! counts with support for stop word filtering, case normalization, and minimum word length.

use std::collections::{HashMap, HashSet};

use super::extractable::TextExtractable;
use super::frequencies::WordFrequencies;
use crate::analytics::stop_words::ENGLISH_STOP_WORDS;

/// Analyzes text to produce word frequency counts.
///
/// Supports configurable stop word filtering, case normalization, and minimum word length
/// filtering.
///
/// # Example
///
/// ```
/// use urs_core::analytics::WordFrequencyAnalyzer;
///
/// let analyzer = WordFrequencyAnalyzer::new()
///     .min_word_length(2)
///     .no_stop_words();
///
/// let freqs = analyzer.analyze_str(&["hello world hello"]);
/// assert_eq!(freqs.entries()[0], ("hello".to_string(), 2));
/// ```
#[derive(Debug)]
pub struct WordFrequencyAnalyzer {
    /// Whether to preserve case during analysis.
    case_sensitive: bool,
    /// Minimum word length to include in results.
    min_word_length: usize,
    /// Words to exclude from frequency counts.
    stop_words: HashSet<String>,
}

impl Default for WordFrequencyAnalyzer {
    fn default() -> Self {
        Self::new()
    }
}

impl WordFrequencyAnalyzer {
    /// Creates a new analyzer with default settings.
    ///
    /// Defaults: case insensitive, min word length 1, English stop words loaded.
    #[must_use]
    pub fn new() -> Self {
        Self {
            case_sensitive: false,
            min_word_length: 1,
            stop_words: ENGLISH_STOP_WORDS
                .iter()
                .map(|w| (*w).to_string())
                .collect(),
        }
    }

    /// Sets whether analysis is case sensitive.
    ///
    /// When `false` (the default), all words are lowercased before counting.
    #[must_use]
    pub const fn case_sensitive(mut self, sensitive: bool) -> Self {
        self.case_sensitive = sensitive;
        self
    }

    /// Sets the minimum word length to include.
    ///
    /// Words shorter than this length are excluded from results. Default: `1`.
    #[must_use]
    pub const fn min_word_length(mut self, len: usize) -> Self {
        self.min_word_length = len;
        self
    }

    /// Sets the stop words to filter out.
    ///
    /// Replaces any previously set stop words. Words are stored in lowercase regardless of the
    /// `case_sensitive` setting.
    #[must_use]
    pub fn stop_words(mut self, words: &[&str]) -> Self {
        self.stop_words = words.iter().map(|w| w.to_lowercase()).collect();
        self
    }

    /// Adds additional stop words without replacing existing ones.
    #[must_use]
    pub fn add_stop_words(mut self, words: &[&str]) -> Self {
        for word in words {
            self.stop_words.insert(word.to_lowercase());
        }

        self
    }

    /// Clears all stop words (disables stop word filtering).
    #[must_use]
    pub fn no_stop_words(mut self) -> Self {
        self.stop_words.clear();
        self
    }

    /// Analyzes items implementing [`TextExtractable`] and returns word frequencies.
    ///
    /// This is the primary entry point for analyzing scraped Reddit data.
    #[must_use]
    pub fn analyze<T: TextExtractable>(&self, items: &[T]) -> WordFrequencies {
        let texts: Vec<&str> = items
            .iter()
            .flat_map(TextExtractable::extract_text)
            .collect();
        self.analyze_str(&texts)
    }

    /// Analyzes raw string slices and returns word frequencies.
    ///
    /// Useful when you have pre-extracted text or want to combine text from multiple sources.
    #[must_use]
    pub fn analyze_str(&self, texts: &[&str]) -> WordFrequencies {
        let mut counts: HashMap<String, u32> = HashMap::new();

        for text in texts {
            for word in self.tokenize(text) {
                *counts.entry(word).or_insert(0) += 1;
            }
        }

        let mut entries: Vec<(String, u32)> = counts.into_iter().collect();

        // Sort by frequency descending, then alphabetically for ties.
        entries.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));

        WordFrequencies { entries }
    }

    /// Tokenizes a single text string into words, applying all configured filters.
    ///
    /// Words are split on non-alphanumeric characters, filtered by length and stop words, and
    /// optionally lowercased.
    fn tokenize<'a>(&'a self, text: &'a str) -> impl Iterator<Item = String> + 'a {
        text.split(|c: char| !c.is_alphanumeric())
            .filter(|word| !word.is_empty())
            .map(|word| {
                if self.case_sensitive {
                    word.to_string()
                } else {
                    word.to_lowercase()
                }
            })
            .filter(|word| word.len() >= self.min_word_length)
            .filter(|word| {
                let check = word.to_lowercase();
                !self.stop_words.contains(&check)
            })
    }
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::models::api::EditedField;
    use crate::models::{Comment, Submission};

    fn sample_submission(title: &str, selftext: Option<&str>) -> Submission {
        Submission {
            author: "testuser".to_string(),
            created_utc: 0.0,
            distinguished: None,
            edited: EditedField::Bool(false),
            id: "abc".to_string(),
            is_original_content: false,
            is_self: selftext.is_some(),
            link_flair_text: None,
            locked: false,
            name: "t3_abc".to_string(),
            nsfw: false,
            num_comments: 0,
            permalink: "/r/test/comments/abc/".to_string(),
            score: 0,
            selftext: selftext.map(String::from),
            spoiler: false,
            stickied: false,
            subreddit: "test".to_string(),
            title: title.to_string(),
            upvote_ratio: 1.0,
            url: "https://reddit.com".to_string(),
            extra: BTreeMap::new(),
        }
    }

    fn sample_comment(body: &str) -> Comment {
        Comment {
            author: "testuser".to_string(),
            body: body.to_string(),
            body_html: String::new(),
            created_utc: 0.0,
            distinguished: None,
            edited: EditedField::Bool(false),
            id: "abc".to_string(),
            is_submitter: false,
            link_id: "t3_abc".to_string(),
            parent_id: "t3_abc".to_string(),
            score: 0,
            stickied: false,
            extra: BTreeMap::new(),
            replies: vec![],
        }
    }

    #[test]
    fn basic_word_frequency() {
        let analyzer = WordFrequencyAnalyzer::new().no_stop_words();
        let freqs = analyzer.analyze_str(&["hello world hello"]);

        assert_eq!(freqs.entries()[0], ("hello".to_string(), 2));
        assert_eq!(freqs.entries()[1], ("world".to_string(), 1));
    }

    #[test]
    fn case_insensitive_by_default() {
        let analyzer = WordFrequencyAnalyzer::new().no_stop_words();
        let freqs = analyzer.analyze_str(&["Hello HELLO hello"]);

        assert_eq!(freqs.unique_count(), 1);
        assert_eq!(freqs.entries()[0], ("hello".to_string(), 3));
    }

    #[test]
    fn case_sensitive_mode() {
        let analyzer = WordFrequencyAnalyzer::new()
            .no_stop_words()
            .case_sensitive(true);
        let freqs = analyzer.analyze_str(&["Hello hello HELLO"]);

        assert_eq!(freqs.unique_count(), 3);
    }

    #[test]
    fn stop_words_filtered() {
        let analyzer = WordFrequencyAnalyzer::new();
        let freqs = analyzer.analyze_str(&["the quick brown fox is a test"]);

        let words: Vec<&str> = freqs.entries().iter().map(|(w, _)| w.as_str()).collect();

        assert!(!words.contains(&"the"));
        assert!(!words.contains(&"is"));
        assert!(!words.contains(&"a"));
        assert!(words.contains(&"quick"));
        assert!(words.contains(&"fox"));
    }

    #[test]
    fn min_word_length() {
        let analyzer = WordFrequencyAnalyzer::new()
            .no_stop_words()
            .min_word_length(4);
        let freqs = analyzer.analyze_str(&["hi to the world hello"]);

        let words: Vec<&str> = freqs.entries().iter().map(|(w, _)| w.as_str()).collect();

        assert!(!words.contains(&"hi"));
        assert!(!words.contains(&"to"));
        assert!(!words.contains(&"the"));
        assert!(words.contains(&"world"));
        assert!(words.contains(&"hello"));
    }

    #[test]
    fn custom_stop_words() {
        let analyzer = WordFrequencyAnalyzer::new().stop_words(&["hello", "world"]);
        let freqs = analyzer.analyze_str(&["hello world rust"]);

        assert_eq!(freqs.unique_count(), 1);
        assert_eq!(freqs.entries()[0].0, "rust");
    }

    #[test]
    fn add_stop_words() {
        let analyzer = WordFrequencyAnalyzer::new().add_stop_words(&["rust", "cargo"]);
        let freqs = analyzer.analyze_str(&["rust cargo crate"]);

        assert_eq!(freqs.unique_count(), 1);
        assert_eq!(freqs.entries()[0].0, "crate");
    }

    #[test]
    fn punctuation_splits_words() {
        let analyzer = WordFrequencyAnalyzer::new().no_stop_words();
        let freqs = analyzer.analyze_str(&["hello, world! foo-bar"]);

        let words: Vec<&str> = freqs.entries().iter().map(|(w, _)| w.as_str()).collect();

        assert!(words.contains(&"hello"));
        assert!(words.contains(&"world"));
        assert!(words.contains(&"foo"));
        assert!(words.contains(&"bar"));
    }

    #[test]
    fn total_count() {
        let analyzer = WordFrequencyAnalyzer::new().no_stop_words();
        let freqs = analyzer.analyze_str(&["a b c a b a"]);

        assert_eq!(freqs.total_count(), 6);
    }

    #[test]
    fn top_n() {
        let analyzer = WordFrequencyAnalyzer::new().no_stop_words();
        let freqs = analyzer.analyze_str(&["a a a b b c"]);

        let top2 = freqs.top_n(2);

        assert_eq!(top2.len(), 2);
        assert_eq!(top2[0], ("a".to_string(), 3));
        assert_eq!(top2[1], ("b".to_string(), 2));
    }

    #[test]
    fn top_n_exceeds_total() {
        let analyzer = WordFrequencyAnalyzer::new().no_stop_words();
        let freqs = analyzer.analyze_str(&["hello"]);

        assert_eq!(freqs.top_n(100).len(), 1);
    }

    #[test]
    fn empty_input() {
        let analyzer = WordFrequencyAnalyzer::new();
        let freqs = analyzer.analyze_str(&[]);

        assert_eq!(freqs.unique_count(), 0);
        assert_eq!(freqs.total_count(), 0);
    }

    #[test]
    fn submission_text_extraction() {
        let sub = sample_submission("Rust is awesome", Some("I love Rust programming"));

        let texts = sub.extract_text();

        assert_eq!(texts.len(), 2);
        assert_eq!(texts[0], "Rust is awesome");
        assert_eq!(texts[1], "I love Rust programming");
    }

    #[test]
    fn submission_without_selftext() {
        let sub = sample_submission("Link Post Title", None);

        let texts = sub.extract_text();

        assert_eq!(texts.len(), 1);
        assert_eq!(texts[0], "Link Post Title");
    }

    #[test]
    fn comment_text_extraction() {
        let comment = sample_comment("This is a great comment");

        let texts = comment.extract_text();

        assert_eq!(texts.len(), 1);
        assert_eq!(texts[0], "This is a great comment");
    }

    #[test]
    fn deleted_comment_skipped() {
        let deleted = sample_comment("[deleted]");
        let removed = sample_comment("[removed]");

        assert!(deleted.extract_text().is_empty());
        assert!(removed.extract_text().is_empty());
    }

    #[test]
    fn analyze_submissions() {
        let subs = vec![
            sample_submission("Rust Rust Rust", None),
            sample_submission("Rust Python", Some("Rust is fast")),
        ];

        let analyzer = WordFrequencyAnalyzer::new();
        let freqs = analyzer.analyze(&subs);

        assert_eq!(freqs.entries()[0], ("rust".to_string(), 5));
    }

    #[test]
    fn analyze_comments() {
        let comments = vec![
            sample_comment("great great post"),
            sample_comment("great comment"),
            sample_comment("[deleted]"),
        ];

        let analyzer = WordFrequencyAnalyzer::new();
        let freqs = analyzer.analyze(&comments);

        assert_eq!(freqs.entries()[0], ("great".to_string(), 3));
        let words: Vec<&str> = freqs.entries().iter().map(|(w, _)| w.as_str()).collect();
        assert!(!words.contains(&"deleted"));
    }

    #[test]
    fn sorted_by_frequency_then_alphabetical() {
        let analyzer = WordFrequencyAnalyzer::new().no_stop_words();
        let freqs = analyzer.analyze_str(&["banana apple cherry apple banana apple"]);

        assert_eq!(freqs.entries()[0], ("apple".to_string(), 3));
        assert_eq!(freqs.entries()[1], ("banana".to_string(), 2));
        assert_eq!(freqs.entries()[2], ("cherry".to_string(), 1));
    }

    #[test]
    fn urls_split_into_parts() {
        let analyzer = WordFrequencyAnalyzer::new()
            .no_stop_words()
            .min_word_length(4);
        let freqs = analyzer.analyze_str(&["check https://www.reddit.com/r/rust"]);

        let words: Vec<&str> = freqs.entries().iter().map(|(w, _)| w.as_str()).collect();

        assert!(words.contains(&"check"));
        assert!(words.contains(&"reddit"));
        assert!(words.contains(&"rust"));
        assert!(words.contains(&"https"));
    }
}
