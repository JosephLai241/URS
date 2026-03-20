//! Relative timestamp formatting for Reddit data.
//!
//! Converts Unix timestamps (as `f64`) to human-readable relative time strings like "2 hours ago"
//! or "3 days ago".

use std::time::{SystemTime, UNIX_EPOCH};

/// Formats a Unix timestamp as a relative time string.
///
/// # Arguments
///
/// * `created_utc` - Unix timestamp as a float (e.g. `1742140245.0`)
///
/// # Returns
///
/// A human-readable relative time string (e.g. "2 hours ago", "3 days ago").
#[must_use]
pub fn relative_time(created_utc: f64) -> String {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs_f64())
        .unwrap_or(0.0);

    let diff = now - created_utc;
    format_duration(diff)
}

/// Formats a Unix timestamp as an absolute datetime string.
///
/// # Arguments
///
/// * `created_utc` - Unix timestamp as a float
///
/// # Returns
///
/// A formatted datetime string (e.g. "2026-03-16 14:30:45 UTC").
#[must_use]
#[allow(dead_code, clippy::cast_possible_truncation)]
pub fn absolute_time(created_utc: f64) -> String {
    let secs = created_utc as i64;
    let dt = chrono::DateTime::from_timestamp(secs, 0);

    dt.map_or_else(
        || "unknown".to_string(),
        |d| d.format("%Y-%m-%d %H:%M:%S UTC").to_string(),
    )
}

/// Formats a timestamp specifically for livestream events (HH:MM:SS).
///
/// # Arguments
///
/// * `created_utc` - Unix timestamp as a float
///
/// # Returns
///
/// A time-only string (e.g. "14:30:45").
#[must_use]
#[allow(clippy::cast_possible_truncation)]
pub fn time_only(created_utc: f64) -> String {
    let secs = created_utc as i64;
    let dt = chrono::DateTime::from_timestamp(secs, 0);

    dt.map_or_else(
        || "??:??:??".to_string(),
        |d| d.format("%H:%M:%S").to_string(),
    )
}

const MINUTE: u64 = 60;
const HOUR: u64 = 60 * MINUTE;
const DAY: u64 = 24 * HOUR;
const WEEK: u64 = 7 * DAY;
const MONTH: u64 = 30 * DAY;
const YEAR: u64 = 365 * DAY;

/// Formats a duration in seconds to a human-readable string.
#[allow(clippy::cast_possible_truncation, clippy::cast_sign_loss)]
fn format_duration(seconds: f64) -> String {
    if seconds < 0.0 {
        return "just now".to_string();
    }

    let secs = seconds as u64;

    if secs < MINUTE {
        "just now".to_string()
    } else if secs < HOUR {
        let mins = secs / MINUTE;
        if mins == 1 {
            "1 minute ago".to_string()
        } else {
            format!("{mins} minutes ago")
        }
    } else if secs < DAY {
        let hours = secs / HOUR;
        if hours == 1 {
            "1 hour ago".to_string()
        } else {
            format!("{hours} hours ago")
        }
    } else if secs < WEEK {
        let days = secs / DAY;
        if days == 1 {
            "1 day ago".to_string()
        } else {
            format!("{days} days ago")
        }
    } else if secs < MONTH {
        let weeks = secs / WEEK;
        if weeks == 1 {
            "1 week ago".to_string()
        } else {
            format!("{weeks} weeks ago")
        }
    } else if secs < YEAR {
        let months = secs / MONTH;
        if months == 1 {
            "1 month ago".to_string()
        } else {
            format!("{months} months ago")
        }
    } else {
        let years = secs / YEAR;
        if years == 1 {
            "1 year ago".to_string()
        } else {
            format!("{years} years ago")
        }
    }
}

/// Formats an account age from `created_utc` to a human-readable string.
///
/// # Arguments
///
/// * `created_utc` - Unix timestamp when the account was created
///
/// # Returns
///
/// A string like "12 year account" or "6 month account".
#[must_use]
#[allow(clippy::cast_possible_truncation, clippy::cast_sign_loss)]
pub fn account_age(created_utc: f64) -> String {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs_f64())
        .unwrap_or(0.0);

    let diff = now - created_utc;
    let days = (diff / 86400.0) as u64;

    if days >= 365 {
        let years = days / 365;
        if years == 1 {
            "1 year account".to_string()
        } else {
            format!("{years} year account")
        }
    } else if days >= 30 {
        let months = days / 30;
        if months == 1 {
            "1 month account".to_string()
        } else {
            format!("{months} month account")
        }
    } else if days == 1 {
        "1 day account".to_string()
    } else {
        format!("{days} day account")
    }
}

/// Formats a Unix timestamp as a human-readable date (e.g. "March 15, 2020").
#[must_use]
#[allow(clippy::cast_possible_truncation)]
pub fn format_date(created_utc: f64) -> String {
    const MONTHS: [&str; 12] = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ];

    let secs = created_utc as i64;
    // Days since Unix epoch.
    let mut days = secs / 86400;
    let mut year = 1970i32;

    loop {
        let days_in_year = if year % 4 == 0 && (year % 100 != 0 || year % 400 == 0) {
            366
        } else {
            365
        };
        if days < days_in_year {
            break;
        }
        days -= days_in_year;
        year += 1;
    }

    let is_leap = year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
    let month_days = [
        31,
        if is_leap { 29 } else { 28 },
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ];

    let mut month = 0;
    for (i, &md) in month_days.iter().enumerate() {
        if days < md {
            month = i;
            break;
        }
        days -= md;
    }

    let day = days + 1;

    format!("{} {day}, {year}", MONTHS[month])
}

/// Formats a number with commas (e.g. 1234567 -> "1,234,567").
#[must_use]
pub fn format_number(n: i64) -> String {
    if n < 0 {
        return format!("-{}", format_number(-n));
    }

    let s = n.to_string();
    let mut result = String::with_capacity(s.len() + s.len() / 3);
    for (i, c) in s.chars().enumerate() {
        if i > 0 && (s.len() - i) % 3 == 0 {
            result.push(',');
        }
        result.push(c);
    }

    result
}

/// Formats a score for compact display (e.g. 1200 -> "1.2k").
#[must_use]
pub fn format_score(score: i32) -> String {
    let abs = score.unsigned_abs();
    let sign = if score < 0 { "-" } else { "" };

    if abs >= 1_000_000 {
        format!("{sign}{:.1}M", f64::from(abs) / 1_000_000.0)
    } else if abs >= 10_000 {
        format!("{sign}{:.0}k", f64::from(abs) / 1_000.0)
    } else if abs >= 1_000 {
        format!("{sign}{:.1}k", f64::from(abs) / 1_000.0)
    } else {
        format!("{sign}{abs}")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn format_duration_just_now() {
        assert_eq!(format_duration(0.0), "just now");
        assert_eq!(format_duration(30.0), "just now");
        assert_eq!(format_duration(-5.0), "just now");
    }

    #[test]
    fn format_duration_minutes() {
        assert_eq!(format_duration(60.0), "1 minute ago");
        assert_eq!(format_duration(120.0), "2 minutes ago");
        assert_eq!(format_duration(3599.0), "59 minutes ago");
    }

    #[test]
    fn format_duration_hours() {
        assert_eq!(format_duration(3600.0), "1 hour ago");
        assert_eq!(format_duration(7200.0), "2 hours ago");
    }

    #[test]
    fn format_duration_days() {
        assert_eq!(format_duration(86400.0), "1 day ago");
        assert_eq!(format_duration(172_800.0), "2 days ago");
    }

    #[test]
    fn format_score_compact() {
        assert_eq!(format_score(0), "0");
        assert_eq!(format_score(999), "999");
        assert_eq!(format_score(1200), "1.2k");
        assert_eq!(format_score(10_500), "10k");
        assert_eq!(format_score(-1200), "-1.2k");
    }

    #[test]
    fn format_number_with_commas() {
        assert_eq!(format_number(0), "0");
        assert_eq!(format_number(999), "999");
        assert_eq!(format_number(1000), "1,000");
        assert_eq!(format_number(1_234_567), "1,234,567");
        assert_eq!(format_number(-5000), "-5,000");
    }
}
