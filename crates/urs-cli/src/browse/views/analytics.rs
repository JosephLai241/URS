//! Analytics view rendering for scraped Reddit data.
//!
//! Produces word frequency tables and inline word cloud images from parsed scrape data.

use base64::Engine;
use base64::engine::general_purpose::STANDARD;
use image::ImageFormat;
use urs_core::analytics::{ColorScheme, WordCloudGenerator, WordFrequencyAnalyzer};

use crate::browse::helpers::render_template;
use crate::browse::loader::ScrapeData;
use crate::browse::templates::{
    AnalyticsFragment, BreadcrumbItem, ColorSchemeOption, WordFreqEntry,
};
use crate::commands::analyze::analyze_scrape_data;

/// Minimum word length for analytics in the browse view.
const MIN_WORD_LENGTH: usize = 3;

/// Renders the analytics view for a scrape file.
pub fn render_analytics_html(
    data: &ScrapeData,
    file_path: &str,
    breadcrumbs: Vec<BreadcrumbItem>,
) -> String {
    let analyzer = WordFrequencyAnalyzer::new().min_word_length(MIN_WORD_LENGTH);
    let frequencies = analyze_scrape_data(&analyzer, data);

    let max_count = frequencies.top_n(1).first().map_or(1, |(_, count)| *count);

    #[allow(clippy::cast_precision_loss)]
    let entries: Vec<WordFreqEntry> = frequencies
        .entries()
        .iter()
        .map(|(word, count)| WordFreqEntry {
            count: *count,
            percentage: (*count as f32 / max_count as f32) * 100.0,
            word: word.clone(),
        })
        .collect();

    let wordcloud_base64 = generate_wordcloud_base64(&frequencies);

    let color_schemes: Vec<ColorSchemeOption> = ColorScheme::ALL
        .iter()
        .map(|s| ColorSchemeOption {
            label: s.label().to_string(),
            selected: *s == ColorScheme::Rainbow,
            slug: s.slug().to_string(),
        })
        .collect();

    let template = AnalyticsFragment {
        breadcrumbs,
        color_schemes,
        entries,
        file_path: file_path.to_string(),
        total_count: frequencies.total_count(),
        unique_count: frequencies.unique_count(),
        wordcloud_base64,
    };

    render_template(template)
}

/// Generates a word cloud and returns it as a base64-encoded PNG string.
///
/// Returns an empty string if generation fails (e.g., no words to render).
#[allow(clippy::cast_precision_loss)]
fn generate_wordcloud_base64(frequencies: &urs_core::analytics::WordFrequencies) -> String {
    if frequencies.unique_count() == 0 {
        return String::new();
    }

    let generator = WordCloudGenerator::new();
    let image = generator.generate(frequencies);

    let mut buffer = std::io::Cursor::new(Vec::new());
    if image.write_to(&mut buffer, ImageFormat::Png).is_err() {
        tracing::warn!("Failed to encode word cloud image as PNG");
        return String::new();
    }

    STANDARD.encode(buffer.into_inner())
}
