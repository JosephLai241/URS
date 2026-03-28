//! Shared helper functions for TUI rendering.
//!
//! Provides JSON value formatting, relative time formatting, and text wrapping utilities used
//! across the UI drawing modules.

use chrono::Utc;

/// Formats a `serde_json::Value` as a human-readable string for display.
pub(super) fn format_json_value(value: &serde_json::Value) -> String {
    match value {
        serde_json::Value::Array(arr) => {
            if arr.is_empty() {
                "[]".to_string()
            } else {
                serde_json::to_string(arr).unwrap_or_else(|_| format!("[{} items]", arr.len()))
            }
        }
        serde_json::Value::Bool(b) => b.to_string(),
        serde_json::Value::Null => "null".to_string(),
        serde_json::Value::Number(n) => n.to_string(),
        serde_json::Value::Object(obj) => {
            if obj.is_empty() {
                "{}".to_string()
            } else {
                serde_json::to_string(obj).unwrap_or_else(|_| format!("{{{} fields}}", obj.len()))
            }
        }
        serde_json::Value::String(s) => s.replace('\n', " ↵ "),
    }
}

/// Formats a UTC timestamp as a human-readable relative time string.
///
/// # Arguments
///
/// * `created_utc` - The UTC timestamp as seconds since epoch
#[must_use]
pub fn format_relative_time(created_utc: f64) -> String {
    let now = Utc::now().timestamp();
    let created = epoch_f64_to_i64(created_utc);
    let diff = (now - created).max(0);

    let secs: u64 = diff.unsigned_abs();

    if secs < 60 {
        format!("{secs}s ago")
    } else if secs < 3600 {
        format!("{}m ago", secs / 60)
    } else if secs < 86_400 {
        format!("{}h ago", secs / 3600)
    } else {
        format!("{}d ago", secs / 86_400)
    }
}

/// Converts an epoch timestamp from `f64` (as Reddit returns) to `i64`.
///
/// Reddit timestamps are positive integers well within `i64` range, so the truncation from `f64`
/// (52-bit mantissa) to `i64` (63-bit) is lossless for all realistic values.
#[allow(clippy::cast_possible_truncation)]
const fn epoch_f64_to_i64(epoch: f64) -> i64 {
    epoch as i64
}

/// Computes how many visual lines a string occupies when wrapped at `max_width` characters.
///
/// Returns at least 1 (even for empty strings).
pub(super) fn wrapped_line_count(s: &str, max_width: usize) -> usize {
    if max_width == 0 || s.is_empty() {
        return 1;
    }
    let char_count = s.chars().count();

    char_count.div_ceil(max_width).max(1)
}
