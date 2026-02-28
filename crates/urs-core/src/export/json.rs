//! This module provides utilities for exporting data to JSON format.

use std::io::Write;
use std::path::Path;

use serde::Serialize;

use crate::error::Result;

/// Exporter for JSON format.
#[derive(Debug, Default)]
pub struct JsonExporter;

impl JsonExporter {
    /// Creates a new JSON exporter.
    #[must_use]
    pub fn new() -> Self {
        Self
    }

    /// Exports data to a JSON file.
    ///
    /// # Arguments
    ///
    /// * `data` - The data to export (must be serializable)
    /// * `path` - The output file path
    ///
    /// # Errors
    ///
    /// Returns an error if serialization or file writing fails.
    pub fn export_to_file<T: Serialize>(&self, data: &T, path: &Path) -> Result<()> {
        let json = serde_json::to_string_pretty(data)?;
        let mut file = std::fs::File::create(path)?;
        file.write_all(json.as_bytes())?;

        Ok(())
    }

    /// Exports data to a JSON string.
    ///
    /// # Arguments
    ///
    /// * `data` - The data to export (must be serializable)
    ///
    /// # Errors
    ///
    /// Returns an error if serialization fails.
    pub fn export_to_string<T: Serialize>(&self, data: &T) -> Result<String> {
        let json = serde_json::to_string_pretty(data)?;
        Ok(json)
    }

    /// Exports data to a compact JSON string (no pretty printing).
    ///
    /// # Arguments
    ///
    /// * `data` - The data to export (must be serializable)
    ///
    /// # Errors
    ///
    /// Returns an error if serialization fails.
    pub fn export_compact<T: Serialize>(&self, data: &T) -> Result<String> {
        let json = serde_json::to_string(data)?;
        Ok(json)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn export_to_string_basic() {
        let exporter = JsonExporter::new();
        let data = vec!["a", "b", "c"];

        let json = exporter.export_to_string(&data).unwrap();

        assert!(json.contains("\"a\""));
        assert!(json.contains("\"b\""));
        assert!(json.contains("\"c\""));
    }

    #[test]
    fn export_to_string_hashmap() {
        let exporter = JsonExporter::new();
        let mut data = HashMap::new();
        data.insert("key", "value");

        let json = exporter.export_to_string(&data).unwrap();

        assert!(json.contains("\"key\""));
        assert!(json.contains("\"value\""));
    }

    #[test]
    fn export_compact_no_whitespace() {
        let exporter = JsonExporter::new();
        let data = vec![1, 2, 3];

        let json = exporter.export_compact(&data).unwrap();

        assert_eq!(json, "[1,2,3]");
    }
}
