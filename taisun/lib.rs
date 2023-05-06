//! `taisun` - The heavy lifter for `URS`.

use pyo3::{prelude::*, types::PyDict};

use comments::{CommentNode, Forest};

mod comments;

/// This module contains utilities for submission comments scraping.
#[pymodule]
fn comments_utils(_python: Python, module: &PyModule) -> PyResult<()> {
    module.add_class::<CommentNode>()?;
    module.add_class::<Forest>()?;

    Ok(())
}

/// `taisun` - The heavy lifter for `URS`.
#[pymodule]
fn taisun(python: Python, module: &PyModule) -> PyResult<()> {
    let comments_utils = pyo3::wrap_pymodule!(comments_utils);
    module.add_wrapped(comments_utils)?;

    let sys = PyModule::import(python, "sys")?;
    let sys_modules: &PyDict = sys.getattr("modules")?.downcast()?;
    sys_modules.set_item("taisun.comments_utils", module.getattr("comments_utils")?)?;

    Ok(())
}
