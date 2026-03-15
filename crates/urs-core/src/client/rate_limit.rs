//! Rate limiting for the Reddit API.
//!
//! Reddit's API enforces rate limits that must be respected. This module parses rate limit headers
//! from API responses and provides utilities for tracking and respecting these limits.
//!
//! # Rate Limit Headers
//!
//! Reddit returns three headers in each response:
//! - `X-Ratelimit-Remaining`: Approximate number of requests remaining
//! - `X-Ratelimit-Reset`: Seconds until the rate limit resets
//! - `X-Ratelimit-Used`: Approximate number of requests used in this period

use std::time::Duration;

use reqwest::header::HeaderMap;
use tracing::debug;

/// Rate limit information extracted from Reddit API response headers.
///
/// This struct captures the current rate limit state and provides methods for determining if
/// requests should be delayed.
#[derive(Debug, Clone, Copy, Default)]
pub struct RateLimitInfo {
    /// Approximate number of requests remaining in the current period.
    pub remaining: f64,
    /// Seconds until the rate limit resets.
    pub reset: u64,
    /// Approximate number of requests used in the current period.
    pub used: u32,
}

impl RateLimitInfo {
    /// The minimum number of remaining requests before we start delaying.
    const LOW_REMAINING_THRESHOLD: f64 = 10.0;

    /// Parses rate limit information from response headers.
    ///
    /// If any headers are missing or unparseable, returns `None`.
    ///
    /// # Arguments
    ///
    /// * `headers` - The response headers from a Reddit API call
    #[must_use]
    pub fn from_headers(headers: &HeaderMap) -> Option<Self> {
        let remaining = headers
            .get("x-ratelimit-remaining")
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.parse::<f64>().ok())?;

        let used = headers
            .get("x-ratelimit-used")
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.parse::<u32>().ok())?;

        let reset = headers
            .get("x-ratelimit-reset")
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.parse::<u64>().ok())?;

        debug!(
            remaining = remaining,
            used = used,
            reset = reset,
            "Parsed rate limit headers"
        );

        Some(Self {
            remaining,
            reset,
            used,
        })
    }

    /// Returns `true` if we're running low on remaining requests.
    #[must_use]
    pub fn is_low(&self) -> bool {
        self.remaining < Self::LOW_REMAINING_THRESHOLD
    }

    /// Returns `true` if we've exhausted our rate limit.
    #[must_use]
    pub fn is_exhausted(&self) -> bool {
        self.remaining <= 0.0
    }

    /// Returns the recommended delay before the next request.
    ///
    /// Returns `None` if no delay is needed. Otherwise, returns a duration based on the current
    /// rate limit state:
    /// - If exhausted: wait until reset
    /// - If low: distribute remaining requests over the reset period
    #[must_use]
    pub fn recommended_delay(&self) -> Option<Duration> {
        if self.is_exhausted() {
            Some(Duration::from_secs(self.reset))
        } else if self.is_low() && self.remaining > 0.0 {
            // Spread remaining requests evenly over the reset period.
            // Use `Duration::from_secs_f64` to avoid any int/float casts.
            let delay_secs = f64::from(u32::try_from(self.reset).unwrap_or(u32::MAX))
                / self.remaining;
            Some(Duration::from_secs_f64(delay_secs))
        } else {
            None
        }
    }
}

/// A rate limiter that tracks API usage and enforces delays.
///
/// This struct maintains the current rate limit state and provides methods for waiting when
/// necessary.
#[derive(Debug, Default)]
pub struct RateLimiter {
    /// The most recent rate limit information.
    info: Option<RateLimitInfo>,
}

impl RateLimiter {
    /// Creates a new rate limiter.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Updates the rate limiter with new information from response headers.
    ///
    /// # Arguments
    ///
    /// * `headers` - The response headers from a Reddit API call
    pub fn update(&mut self, headers: &HeaderMap) {
        if let Some(info) = RateLimitInfo::from_headers(headers) {
            self.info = Some(info);
        }
    }

    /// Returns the current rate limit information, if available.
    #[must_use]
    pub const fn info(&self) -> Option<RateLimitInfo> {
        self.info
    }

    /// Waits if necessary based on the current rate limit state.
    ///
    /// This method should be called before each API request to ensure we don't exceed the rate
    /// limit.
    pub async fn wait_if_needed(&self) {
        if let Some(info) = &self.info {
            if let Some(delay) = info.recommended_delay() {
                debug!(
                    delay_ms = delay.as_millis(),
                    remaining = info.remaining,
                    "Rate limiting: waiting before next request"
                );
                tokio::time::sleep(delay).await;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use reqwest::header::HeaderValue;

    fn make_headers(remaining: &str, used: &str, reset: &str) -> HeaderMap {
        let mut headers = HeaderMap::new();
        headers.insert(
            "x-ratelimit-remaining",
            HeaderValue::from_str(remaining).unwrap(),
        );
        headers.insert("x-ratelimit-used", HeaderValue::from_str(used).unwrap());
        headers.insert("x-ratelimit-reset", HeaderValue::from_str(reset).unwrap());

        headers
    }

    #[test]
    fn rate_limit_info_from_headers() {
        let headers = make_headers("100.5", "50", "300");
        let info = RateLimitInfo::from_headers(&headers).unwrap();

        assert!((info.remaining - 100.5).abs() < f64::EPSILON);
        assert_eq!(info.used, 50);
        assert_eq!(info.reset, 300);
    }

    #[test]
    fn rate_limit_info_missing_header() {
        let headers = HeaderMap::new();
        assert!(RateLimitInfo::from_headers(&headers).is_none());
    }

    #[test]
    fn rate_limit_info_is_low() {
        let info = RateLimitInfo {
            remaining: 5.0,
            used: 95,
            reset: 60,
        };

        assert!(info.is_low());

        let info = RateLimitInfo {
            remaining: 50.0,
            used: 50,
            reset: 60,
        };

        assert!(!info.is_low());
    }

    #[test]
    fn rate_limit_info_is_exhausted() {
        let info = RateLimitInfo {
            remaining: 0.0,
            used: 100,
            reset: 60,
        };

        assert!(info.is_exhausted());

        let info = RateLimitInfo {
            remaining: 1.0,
            used: 99,
            reset: 60,
        };

        assert!(!info.is_exhausted());
    }

    #[test]
    fn rate_limit_recommended_delay_exhausted() {
        let info = RateLimitInfo {
            remaining: 0.0,
            used: 100,
            reset: 60,
        };

        let delay = info.recommended_delay().unwrap();
        assert_eq!(delay, Duration::from_secs(60));
    }

    #[test]
    fn rate_limit_recommended_delay_low() {
        let info = RateLimitInfo {
            remaining: 5.0,
            used: 95,
            reset: 60,
        };

        let delay = info.recommended_delay().unwrap();

        assert_eq!(delay, Duration::from_millis(12000));
    }

    #[test]
    fn rate_limit_recommended_delay_none() {
        let info = RateLimitInfo {
            remaining: 100.0,
            used: 0,
            reset: 600,
        };

        assert!(info.recommended_delay().is_none());
    }
}
