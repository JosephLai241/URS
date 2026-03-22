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
//! use urs_core::analytics::{ColorScheme, WordCloudGenerator, WordFrequencyAnalyzer};
//!
//! let analyzer = WordFrequencyAnalyzer::new();
//! let freqs = analyzer.analyze_str(&["rust rust rust code code programming"]);
//!
//! let generator = WordCloudGenerator::new()
//!     .color_scheme(ColorScheme::Ocean);
//! generator.save(&freqs, Path::new("wordcloud.png")).unwrap();
//! ```

use std::path::Path;

use image::RgbaImage;
use wordcloud_rs::{Colors, Token, WordCloud};

use super::word_freq::WordFrequencies;
use crate::error::Result;

/// Color scheme for word cloud generation.
///
/// Each variant maps to a [`wordcloud_rs::Colors`] scheme. The default is [`Rainbow`](Self::Rainbow).
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub enum ColorScheme {
    /// Full rainbow spectrum — evenly distributed hues.
    #[default]
    Rainbow,
    /// Monochrome blue.
    Blue,
    /// Cool tones centered on blue/cyan.
    Cool,
    /// Forest tones — greens and browns.
    Forest,
    /// Monochrome green.
    Green,
    /// Ocean tones — blues and greens.
    Ocean,
    /// Monochrome purple.
    Purple,
    /// Sunset tones — reds, oranges, and purples.
    Sunset,
    /// Warm tones centered on red/orange.
    Warm,
}

impl ColorScheme {
    /// All available color schemes, in display order.
    pub const ALL: &[Self] = &[
        Self::Rainbow,
        Self::Blue,
        Self::Cool,
        Self::Forest,
        Self::Green,
        Self::Ocean,
        Self::Purple,
        Self::Sunset,
        Self::Warm,
    ];

    /// Returns the scheme's display name.
    #[must_use]
    pub const fn label(self) -> &'static str {
        match self {
            Self::Rainbow => "Rainbow",
            Self::Blue => "Blue",
            Self::Cool => "Cool",
            Self::Forest => "Forest",
            Self::Green => "Green",
            Self::Ocean => "Ocean",
            Self::Purple => "Purple",
            Self::Sunset => "Sunset",
            Self::Warm => "Warm",
        }
    }

    /// Returns the scheme's slug (used in query params and URLs).
    #[must_use]
    pub const fn slug(self) -> &'static str {
        match self {
            Self::Rainbow => "rainbow",
            Self::Blue => "blue",
            Self::Cool => "cool",
            Self::Forest => "forest",
            Self::Green => "green",
            Self::Ocean => "ocean",
            Self::Purple => "purple",
            Self::Sunset => "sunset",
            Self::Warm => "warm",
        }
    }

    /// Parses a slug string into a `ColorScheme`, defaulting to [`Rainbow`](Self::Rainbow).
    #[must_use]
    pub fn from_slug(s: &str) -> Self {
        match s {
            "blue" => Self::Blue,
            "cool" => Self::Cool,
            "forest" => Self::Forest,
            "green" => Self::Green,
            "ocean" => Self::Ocean,
            "purple" => Self::Purple,
            "sunset" => Self::Sunset,
            "warm" => Self::Warm,
            _ => Self::Rainbow,
        }
    }

    /// Converts this scheme into the `wordcloud_rs::Colors` representation.
    const fn to_wordcloud_colors(self) -> Colors {
        use palette::rgb::Rgb;

        match self {
            Self::Blue => Colors::BiaisedRainbow {
                anchor: Rgb::new(0.15, 0.3, 0.85),
                variance: 15.,
            },
            Self::Cool => Colors::BiaisedRainbow {
                anchor: Rgb::new(0.1, 0.4, 0.9),
                variance: 40.,
            },
            Self::Forest => Colors::BiaisedRainbow {
                anchor: Rgb::new(0.2, 0.6, 0.15),
                variance: 25.,
            },
            Self::Green => Colors::BiaisedRainbow {
                anchor: Rgb::new(0.1, 0.7, 0.3),
                variance: 15.,
            },
            Self::Ocean => Colors::BiaisedRainbow {
                anchor: Rgb::new(0.0, 0.5, 0.7),
                variance: 30.,
            },
            Self::Purple => Colors::BiaisedRainbow {
                anchor: Rgb::new(0.55, 0.1, 0.8),
                variance: 20.,
            },
            Self::Rainbow => Colors::Rainbow {
                luminance: 70.,
                chroma: 100.,
            },
            Self::Sunset => Colors::DoubleSplitCompl {
                anchor: Rgb::new(0.9, 0.3, 0.2),
            },
            Self::Warm => Colors::BiaisedRainbow {
                anchor: Rgb::new(0.9, 0.3, 0.1),
                variance: 40.,
            },
        }
    }
}

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
/// use urs_core::analytics::{ColorScheme, WordCloudGenerator, WordFrequencyAnalyzer};
///
/// let analyzer = WordFrequencyAnalyzer::new();
/// let freqs = analyzer.analyze_str(&["hello hello world rust rust rust"]);
///
/// let generator = WordCloudGenerator::new()
///     .dimensions(800, 600)
///     .color_scheme(ColorScheme::Ocean);
/// generator.save(&freqs, Path::new("output.png")).unwrap();
/// ```
#[derive(Debug)]
pub struct WordCloudGenerator {
    /// Color scheme for word rendering.
    color_scheme: ColorScheme,
    /// Output image height in pixels.
    height: usize,
    /// Output image width in pixels.
    width: usize,
}

impl Default for WordCloudGenerator {
    fn default() -> Self {
        Self::new()
    }
}

impl WordCloudGenerator {
    /// Creates a new generator with default settings (2048x1024, Rainbow colors).
    #[must_use]
    pub const fn new() -> Self {
        Self {
            color_scheme: ColorScheme::Rainbow,
            height: 1024,
            width: 2048,
        }
    }

    /// Sets the color scheme.
    #[must_use]
    pub const fn color_scheme(mut self, scheme: ColorScheme) -> Self {
        self.color_scheme = scheme;
        self
    }

    /// Sets the output image dimensions.
    ///
    /// # Arguments
    ///
    /// * `width` - Image width in pixels
    /// * `height` - Image height in pixels
    #[must_use]
    pub const fn dimensions(mut self, width: usize, height: usize) -> Self {
        self.height = height;
        self.width = width;

        self
    }

    /// Generates a word cloud image from word frequencies.
    ///
    /// Converts the frequency data into weighted tokens and renders them into an image using the
    /// configured color scheme and dimensions.
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

        let mut wc = WordCloud::new()
            .dim(self.width, self.height)
            .colors(self.color_scheme.to_wordcloud_colors());

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

        assert_eq!(generator.width, 2048);
        assert_eq!(generator.height, 1024);
    }

    #[test]
    fn custom_dimensions() {
        let generator = WordCloudGenerator::new().dimensions(1024, 768);

        assert_eq!(generator.width, 1024);
        assert_eq!(generator.height, 768);
    }

    #[test]
    fn default_color_scheme() {
        let generator = WordCloudGenerator::new();

        assert_eq!(generator.color_scheme, ColorScheme::Rainbow);
    }

    #[test]
    fn custom_color_scheme() {
        let generator = WordCloudGenerator::new().color_scheme(ColorScheme::Ocean);

        assert_eq!(generator.color_scheme, ColorScheme::Ocean);
    }

    #[test]
    fn color_scheme_slug_roundtrip() {
        for scheme in ColorScheme::ALL {
            assert_eq!(ColorScheme::from_slug(scheme.slug()), *scheme);
        }
    }

    #[test]
    fn color_scheme_unknown_slug_defaults_to_rainbow() {
        assert_eq!(ColorScheme::from_slug("unknown"), ColorScheme::Rainbow);
        assert_eq!(ColorScheme::from_slug(""), ColorScheme::Rainbow);
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
