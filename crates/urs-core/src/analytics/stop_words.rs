//! Built-in English stop words list.
//!
//! This module provides a standard English stop words list based on the NLTK corpus. These are
//! common words (articles, prepositions, pronouns, etc.) that are typically filtered out during
//! text analysis because they carry little semantic meaning.

/// Standard English stop words from the NLTK corpus.
///
/// Contains ~179 common English words that are typically excluded from word frequency analysis.
///
/// # Example
///
/// ```
/// use urs_core::analytics::ENGLISH_STOP_WORDS;
///
/// assert!(ENGLISH_STOP_WORDS.contains(&"the"));
/// assert!(!ENGLISH_STOP_WORDS.contains(&"rust"));
/// ```
pub const ENGLISH_STOP_WORDS: &[&str] = &[
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "ain",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "aren",
    "aren't",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "couldn",
    "couldn't",
    "d",
    "did",
    "didn",
    "didn't",
    "do",
    "does",
    "doesn",
    "doesn't",
    "doing",
    "don",
    "don't",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "hadn",
    "hadn't",
    "has",
    "hasn",
    "hasn't",
    "have",
    "haven",
    "haven't",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "isn",
    "isn't",
    "it",
    "it's",
    "its",
    "itself",
    "just",
    "ll",
    "m",
    "ma",
    "me",
    "mightn",
    "mightn't",
    "more",
    "most",
    "mustn",
    "mustn't",
    "my",
    "myself",
    "needn",
    "needn't",
    "no",
    "nor",
    "not",
    "now",
    "o",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "re",
    "s",
    "same",
    "shan",
    "shan't",
    "she",
    "she's",
    "should",
    "should've",
    "shouldn",
    "shouldn't",
    "so",
    "some",
    "such",
    "t",
    "than",
    "that",
    "that'll",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "ve",
    "very",
    "was",
    "wasn",
    "wasn't",
    "we",
    "were",
    "weren",
    "weren't",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "won",
    "won't",
    "wouldn",
    "wouldn't",
    "y",
    "you",
    "you'd",
    "you'll",
    "you're",
    "you've",
    "your",
    "yours",
    "yourself",
    "yourselves",
];

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stop_words_contains_common_words() {
        assert!(ENGLISH_STOP_WORDS.contains(&"the"));
        assert!(ENGLISH_STOP_WORDS.contains(&"is"));
        assert!(ENGLISH_STOP_WORDS.contains(&"and"));
        assert!(ENGLISH_STOP_WORDS.contains(&"a"));
    }

    #[test]
    fn stop_words_excludes_content_words() {
        assert!(!ENGLISH_STOP_WORDS.contains(&"rust"));
        assert!(!ENGLISH_STOP_WORDS.contains(&"reddit"));
        assert!(!ENGLISH_STOP_WORDS.contains(&"hello"));
    }

    #[test]
    fn stop_words_is_sorted() {
        let mut sorted = ENGLISH_STOP_WORDS.to_vec();
        sorted.sort_unstable();

        assert_eq!(ENGLISH_STOP_WORDS, sorted.as_slice());
    }
}
