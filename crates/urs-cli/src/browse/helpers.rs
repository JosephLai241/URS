//! Shared utility functions for the browse web server.
//!
//! Provides HTML escaping, template rendering helpers, error page generation,
//! breadcrumb construction, JSON syntax highlighting, and the SPA shell wrapper.

use askama::Template;
use axum::http::StatusCode;
use axum::response::{Html, IntoResponse, Response};

use super::loader;
use super::server::AppState;
use super::templates::{BreadcrumbItem, ErrorFragment, ShellTemplate};

/// Converts a template to an axum HTML response.
pub fn into_html_response<T: Template>(template: T) -> Response {
    match template.render() {
        Ok(html) => Html(html).into_response(),
        Err(e) => {
            tracing::error!(error = %e, "Template render error");
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("Render error: {e}"),
            )
                .into_response()
        }
    }
}

/// Renders any askama template to an HTML string, falling back to an error message.
pub fn render_template<T: Template>(template: T) -> String {
    template.render().unwrap_or_else(|e| {
        tracing::error!(error = %e, "Template render error");
        format!("<h1>500</h1><p>Render error: {e}</p>")
    })
}

/// Renders an error fragment to an HTML string.
pub fn error_html(status: u16, message: &str) -> String {
    let template = ErrorFragment {
        message: message.to_string(),
        status,
    };
    template
        .render()
        .unwrap_or_else(|_| format!("<h1>{status}</h1><p>{message}</p>"))
}

/// Creates an error response, wrapping in shell for direct access.
pub fn error_response(status: u16, message: &str, is_htmx: bool, state: &AppState) -> Response {
    let html = error_html(status, message);
    let status_code = StatusCode::from_u16(status).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR);

    if is_htmx {
        (status_code, Html(html)).into_response()
    } else {
        wrap_in_shell(state, &html, status_code)
    }
}

/// Wraps a content HTML string in the full SPA shell for direct URL access.
pub fn wrap_in_shell(state: &AppState, content_html: &str, status: StatusCode) -> Response {
    let sidebar_entries = loader::scan_directory(&state.scrapes_dir, "").unwrap_or_default();
    let template = ShellTemplate {
        content_html: content_html.to_string(),
        scrape_enabled: state.client.is_some(),
        sidebar_entries,
        username: state.username.as_deref().map(String::from),
    };

    match template.render() {
        Ok(html) => (status, Html(html)).into_response(),
        Err(e) => {
            tracing::error!(error = %e, "Shell template render error");

            (
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("Render error: {e}"),
            )
                .into_response()
        }
    }
}

/// Builds breadcrumb items from a file path.
pub fn build_breadcrumbs(file_path: &str) -> Vec<BreadcrumbItem> {
    file_path
        .split('/')
        .filter(|p| !p.is_empty())
        .map(|part| BreadcrumbItem {
            label: part.to_string(),
            href: None,
        })
        .collect()
}

/// Basic JSON syntax highlighting. Wraps tokens in `<span>` classes.
#[allow(clippy::format_push_string)]
pub fn syntax_highlight_json(json: &str) -> String {
    let mut result = String::with_capacity(json.len() * 2);
    let mut chars = json.chars().peekable();

    while let Some(c) = chars.next() {
        match c {
            '"' => {
                let mut s = String::new();
                s.push('"');

                let mut escaped = false;
                for ch in chars.by_ref() {
                    s.push(ch);
                    if escaped {
                        escaped = false;
                    } else if ch == '\\' {
                        escaped = true;
                    } else if ch == '"' {
                        break;
                    }
                }

                // Check if this is a key (followed by ':').
                let is_key = chars
                    .clone()
                    .find(|ch| !ch.is_whitespace())
                    .is_some_and(|ch| ch == ':');

                let class = if is_key { "json-key" } else { "json-string" };

                result.push_str(&format!(
                    "<span class=\"{class}\">{}</span>",
                    html_escape(&s)
                ));
            }
            c if c.is_ascii_digit() || c == '-' => {
                let mut num = String::new();
                num.push(c);

                while let Some(&ch) = chars.peek() {
                    if ch.is_ascii_digit()
                        || ch == '.'
                        || ch == 'e'
                        || ch == 'E'
                        || ch == '+'
                        || ch == '-'
                    {
                        num.push(ch);
                        chars.next();
                    } else {
                        break;
                    }
                }

                // Only treat as number if it parses (otherwise it's a minus sign, etc.).
                if num.parse::<f64>().is_ok() {
                    result.push_str(&format!("<span class=\"json-number\">{num}</span>"));
                } else {
                    result.push_str(&html_escape(&num));
                }
            }
            't' | 'f' => {
                let mut word = String::new();
                word.push(c);

                while let Some(&ch) = chars.peek() {
                    if ch.is_ascii_alphabetic() {
                        word.push(ch);
                        chars.next();
                    } else {
                        break;
                    }
                }

                if word == "true" || word == "false" {
                    result.push_str(&format!("<span class=\"json-bool\">{word}</span>"));
                } else {
                    result.push_str(&word);
                }
            }
            'n' => {
                let mut word = String::new();
                word.push(c);

                while let Some(&ch) = chars.peek() {
                    if ch.is_ascii_alphabetic() {
                        word.push(ch);
                        chars.next();
                    } else {
                        break;
                    }
                }

                if word == "null" {
                    result.push_str("<span class=\"json-null\">null</span>");
                } else {
                    result.push_str(&word);
                }
            }
            '[' | ']' | '{' | '}' => {
                result.push_str(&format!("<span class=\"json-bracket\">{c}</span>"));
            }
            '<' => result.push_str("&lt;"),
            '>' => result.push_str("&gt;"),
            '&' => result.push_str("&amp;"),
            _ => result.push(c),
        }
    }

    result
}

/// Escapes HTML special characters.
pub fn html_escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#39;")
}
