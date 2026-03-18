//! Markdown rendering for Reddit comment/post bodies.
//!
//! Wraps `pulldown-cmark` to convert Reddit-flavored Markdown to HTML.
//! Falls back to pre-rendered `body_html` from the Reddit API when available.

use pulldown_cmark::{Options, Parser, html};

/// Renders Markdown text to HTML.
///
/// Enables tables, strikethrough, and autolinks for Reddit compatibility.
///
/// # Arguments
///
/// * `markdown` - The Markdown source text
///
/// # Returns
///
/// The rendered HTML string.
#[must_use]
pub fn render(markdown: &str) -> String {
    let options =
        Options::ENABLE_TABLES | Options::ENABLE_STRIKETHROUGH | Options::ENABLE_SMART_PUNCTUATION;

    let parser = Parser::new_ext(markdown, options);
    let mut html_output = String::with_capacity(markdown.len() * 2);
    html::push_html(&mut html_output, parser);

    html_output
}

/// Returns rendered HTML for a comment body.
///
/// Prefers `body_html` from the Reddit API when it's non-empty, otherwise renders `body` as Markdown.
///
/// # Arguments
///
/// * `body` - The Markdown body text
/// * `body_html` - The pre-rendered HTML from Reddit (may contain HTML entities)
#[must_use]
pub fn render_comment(body: &str, body_html: &str) -> String {
    if body_html.is_empty() {
        render(body)
    } else {
        decode_reddit_html(body_html)
    }
}

/// Decodes Reddit's HTML-encoded `body_html` field.
///
/// Reddit wraps `body_html` in `<!-- SC_OFF --><div class="md">...</div><!-- SC_ON -->` and
/// HTML-encodes certain characters. This function strips the wrapper, decodes entities, and
/// rewrites relative Reddit URLs (e.g. `/r/rust`, `/u/spez`) to absolute URLs so they don't
/// resolve against the local browse server.
#[must_use]
fn decode_reddit_html(html: &str) -> String {
    let decoded = html
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("&quot;", "\"")
        .replace("&#39;", "'");

    rewrite_relative_reddit_urls(&decoded)
}

/// Rewrites relative URLs in Reddit HTML to absolute `https://www.reddit.com` URLs.
///
/// All relative paths in Reddit's `body_html` are Reddit URLs (subreddits, users, messages, wiki
/// pages, etc.), so any `href="/..."` is rewritten.
fn rewrite_relative_reddit_urls(html: &str) -> String {
    html.replace("href=\"/", "href=\"https://www.reddit.com/")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn render_basic_markdown() {
        let result = render("**bold** and *italic*");
        assert!(result.contains("<strong>bold</strong>"));
        assert!(result.contains("<em>italic</em>"));
    }

    #[test]
    fn render_link() {
        let result = render("[click here](https://example.com)");
        assert!(result.contains("<a href=\"https://example.com\">click here</a>"));
    }

    #[test]
    fn render_comment_prefers_body_html() {
        let result = render_comment("**bold**", "<p><b>bold</b></p>");
        assert_eq!(result, "<p><b>bold</b></p>");
    }

    #[test]
    fn render_comment_falls_back_to_markdown() {
        let result = render_comment("**bold**", "");
        assert!(result.contains("<strong>bold</strong>"));
    }

    #[test]
    fn decode_html_entities() {
        let input = "&lt;p&gt;Hello &amp; world&lt;/p&gt;";
        let result = decode_reddit_html(input);
        assert_eq!(result, "<p>Hello & world</p>");
    }

    #[test]
    fn rewrite_subreddit_links() {
        let input = r#"<a href="/r/rust">r/rust</a>"#;
        let result = rewrite_relative_reddit_urls(input);
        assert_eq!(
            result,
            r#"<a href="https://www.reddit.com/r/rust">r/rust</a>"#
        );
    }

    #[test]
    fn rewrite_user_links() {
        let input = r#"<a href="/u/spez">u/spez</a>"#;
        let result = rewrite_relative_reddit_urls(input);
        assert_eq!(
            result,
            r#"<a href="https://www.reddit.com/u/spez">u/spez</a>"#
        );
    }

    #[test]
    fn rewrite_message_compose_links() {
        let input = r#"<a href="/message/compose/?to=/r/cscareerquestions">contact mods</a>"#;
        let result = rewrite_relative_reddit_urls(input);
        assert_eq!(
            result,
            r#"<a href="https://www.reddit.com/message/compose/?to=/r/cscareerquestions">contact mods</a>"#
        );
    }

    #[test]
    fn preserve_absolute_urls() {
        let input = r#"<a href="https://example.com/r/test">link</a>"#;
        let result = rewrite_relative_reddit_urls(input);
        assert_eq!(result, input);
    }

    #[test]
    fn rewrite_multiple_links() {
        let input = r#"See <a href="/r/rust">r/rust</a> and <a href="/u/ferris">u/ferris</a>"#;
        let result = rewrite_relative_reddit_urls(input);
        assert_eq!(
            result,
            r#"See <a href="https://www.reddit.com/r/rust">r/rust</a> and <a href="https://www.reddit.com/u/ferris">u/ferris</a>"#
        );
    }
}
