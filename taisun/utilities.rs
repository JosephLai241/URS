//! Contains utilities for `URS`.

use pyo3::{pyfunction, PyResult};
use std::{fs::File, io::Read, path::Path};

/// Read help messages from the `help-text/` directory.
#[pyfunction]
pub fn read_help_text(filename: String) -> PyResult<String> {
    let mut file = File::open(Path::new(&format!("../help-text/{filename}")))?;
    let mut text = String::new();
    file.read_to_string(&mut text)?;

    Ok(text)
}
