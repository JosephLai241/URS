//! `taisun` - The heavy lifter for `URS`.

use pyo3::{prelude::*, types::PyDict, wrap_pymodule};

use comments::{CommentNode, Forest};
use utilities::{is_valid_file, read_help_text};

mod comments;
mod utilities;

/// This module contains utilities for submission comments scraping.
#[pymodule]
fn comments_utils(_python: Python, module: &PyModule) -> PyResult<()> {
    module.add_class::<CommentNode>()?;
    module.add_class::<Forest>()?;

    Ok(())
}

/// This module contains miscellaneous utilities for `URS`.
#[pymodule]
fn utils(_python: Python, module: &PyModule) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(read_help_text, module)?)?;
    module.add_function(wrap_pyfunction!(is_valid_file, module)?)?;

    Ok(())
}

/// `taisun` - The heavy lifter for `URS`.
#[pymodule]
fn taisun(python: Python, module: &PyModule) -> PyResult<()> {
    let comments_utils = wrap_pymodule!(comments_utils);
    let utils = wrap_pymodule!(utils);

    module.add_wrapped(comments_utils)?;
    module.add_wrapped(utils)?;

    let sys = PyModule::import(python, "sys")?;
    let sys_modules: &PyDict = sys.getattr("modules")?.downcast()?;

    sys_modules.set_item("taisun.comments_utils", module.getattr("comments_utils")?)?;
    sys_modules.set_item("taisun.utils", module.getattr("utils")?)?;

    Ok(())
}
