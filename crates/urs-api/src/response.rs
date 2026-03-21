//! Standard JSON response envelope for API endpoints.
//!
//! All successful responses are wrapped in an [`ApiResponse`] envelope that provides a consistent
//! structure with an optional item count.

use axum::Json;
use axum::response::IntoResponse;
use serde::Serialize;

/// A JSON response envelope wrapping the response data.
///
/// # Fields
///
/// * `data` - The response payload
/// * `count` - Optional item count, included when the data is a collection
///
/// # Example JSON
///
/// ```json
/// {
///     "data": [ ... ],
///     "count": 25
/// }
/// ```
#[derive(Debug, Serialize)]
pub struct ApiResponse<T> {
    /// Optional count of items in the response.
    #[serde(skip_serializing_if = "Option::is_none")]
    count: Option<usize>,
    /// The response payload.
    data: T,
}

impl<T: Serialize> ApiResponse<T> {
    /// Creates a response with just the data and no count.
    #[must_use]
    pub const fn new(data: T) -> Self {
        Self { count: None, data }
    }

    /// Creates a response with the data and an item count.
    #[must_use]
    pub const fn with_count(data: T, count: usize) -> Self {
        Self {
            count: Some(count),
            data,
        }
    }
}

impl<T: Serialize> IntoResponse for ApiResponse<T> {
    fn into_response(self) -> axum::response::Response {
        Json(self).into_response()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn response_without_count_omits_field() {
        let resp = ApiResponse::new("hello");
        let json = serde_json::to_value(&resp).unwrap();

        assert_eq!(json["data"], "hello");
        assert!(json.get("count").is_none());
    }

    #[test]
    fn response_with_count_includes_field() {
        let resp = ApiResponse::with_count(vec![1, 2, 3], 3);
        let json = serde_json::to_value(&resp).unwrap();

        assert_eq!(json["data"], serde_json::json!([1, 2, 3]));
        assert_eq!(json["count"], 3);
    }
}
