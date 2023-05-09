//! Contains utilities for `URS`.

use pyo3::{pyfunction, PyResult};
use std::{
    fs::{self, File},
    io::Read,
    path::Path,
};

/// Read help messages from the `help-text/` directory.
#[pyfunction]
pub fn read_help_text(filename: String) -> PyResult<String> {
    let mut file = File::open(Path::new(&format!("../help-text/{filename}")))?;
    let mut text = String::new();
    file.read_to_string(&mut text)?;

    Ok(text)
}

/// Quickly check if a filepath points to a valid file.
#[pyfunction]
pub fn is_valid_file(filename: String) -> PyResult<bool> {
    if let Ok(metadata) = fs::metadata(Path::new(&filename)) {
        Ok(metadata.is_file())
    } else {
        Ok(false)
    }
}
