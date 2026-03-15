//! Word cloud image generation from word frequency data.
//!
//! This module wraps the `wordcloud-rs` crate to provide a convenient API for generating word
//! cloud visualizations from [`WordFrequencies`].
//!
//! # Example
//!
//! ```no_run
//! use std::path::Path;
//!
//! use urs_core::analytics::{WordCloudGenerator, WordFrequencyAnalyzer};
//!
//! let analyzer = WordFrequencyAnalyzer::new();
//! let freqs = analyzer.analyze_str(&["rust rust rust code code programming"]);
//!
//! let generator = WordCloudGenerator::new();
//! generator.save(&freqs, Path::new("wordcloud.png")).unwrap();
//! ```

use std::path::Path;

use image::RgbaImage;
use wordcloud_rs::{Token, WordCloud};

use super::word_freq::WordFrequencies;
use crate::error::Result;

/// Generates word cloud images from word frequency data.
///
/// Wraps the `wordcloud-rs` crate to provide a simple API for creating word cloud images from
/// [`WordFrequencies`] produced by [`WordFrequencyAnalyzer`](super::WordFrequencyAnalyzer).
///
/// # Example
///
/// ```no_run
/// use std::path::Path;
///
/// use urs_core::analytics::{WordCloudGenerator, WordFrequencyAnalyzer};
///
/// let analyzer = WordFrequencyAnalyzer::new();
/// let freqs = analyzer.analyze_str(&["hello hello world rust rust rust"]);
///
/// let generator = WordCloudGenerator::new().dimensions(800, 600);
/// generator.save(&freqs, Path::new("output.png")).unwrap();
/// ```
#[derive(Debug)]
pub struct WordCloudGenerator {
    /// Output image width in pixels.
    width: usize,
    /// Output image height in pixels.
    height: usize,
}

impl Default for WordCloudGenerator {
    fn default() -> Self {
        Self::new()
    }
}

impl WordCloudGenerator {
    /// Creates a new generator with default dimensions (896x448).
    ///
    /// These defaults match the `wordcloud-rs` library defaults.
    #[must_use]
    pub const fn new() -> Self {
        Self {
            width: 896,
            height: 448,
        }
    }

    /// Sets the output image dimensions.
    ///
    /// # Arguments
    ///
    /// * `width` - Image width in pixels
    /// * `height` - Image height in pixels
    #[must_use]
    pub const fn dimensions(mut self, width: usize, height: usize) -> Self {
        self.width = width;
        self.height = height;

        self
    }

    /// Generates a word cloud image from word frequencies.
    ///
    /// Converts the frequency data into weighted tokens and renders them into an image.
    ///
    /// # Arguments
    ///
    /// * `frequencies` - The word frequency data to visualize
    ///
    /// # Returns
    ///
    /// An RGBA image that can be saved or further processed.
    #[must_use]
    #[allow(clippy::cast_precision_loss)]
    pub fn generate(&self, frequencies: &WordFrequencies) -> RgbaImage {
        let tokens: Vec<(Token, f32)> = frequencies
            .entries()
            .iter()
            .map(|(word, count)| (Token::Text(word.clone()), *count as f32))
            .collect();

        let mut wc = WordCloud::new().dim(self.width, self.height);

        wc.generate(tokens)
    }

    /// Generates a word cloud and saves it to a file.
    ///
    /// The output format is determined by the file extension (`.png`, `.jpg`, etc.).
    ///
    /// # Arguments
    ///
    /// * `frequencies` - The word frequency data to visualize
    /// * `path` - The output file path
    ///
    /// # Errors
    ///
    /// Returns an error if the image cannot be saved.
    pub fn save(&self, frequencies: &WordFrequencies, path: &Path) -> Result<()> {
        let image = self.generate(frequencies);
        image.save(path).map_err(crate::error::Error::Image)?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_dimensions() {
        let generator = WordCloudGenerator::new();

        assert_eq!(generator.width, 896);
        assert_eq!(generator.height, 448);
    }

    #[test]
    fn custom_dimensions() {
        let generator = WordCloudGenerator::new().dimensions(1024, 768);

        assert_eq!(generator.width, 1024);
        assert_eq!(generator.height, 768);
    }

    #[test]
    #[ignore = "word cloud rendering is slow in debug mode"]
    fn generate_produces_image() {
        use crate::analytics::WordFrequencyAnalyzer;

        let analyzer = WordFrequencyAnalyzer::new().no_stop_words();
        let freqs = analyzer.analyze_str(&["rust rust rust code code programming"]);

        let generator = WordCloudGenerator::new().dimensions(256, 128);
        let image = generator.generate(&freqs);

        assert_eq!(image.width(), 256);
        assert_eq!(image.height(), 128);
    }
}
