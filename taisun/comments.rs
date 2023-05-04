//! This module provides computational functions pertaining to submission comments.

use pyo3::{
    exceptions::PyValueError,
    prelude::*,
    types::{PyBool, PyDict, PyString},
};
use serde::{Deserialize, Serialize};

use std::collections::{HashSet, VecDeque};

/// An enum used for the `edited` field in the `CommentNode`. The `edited` field may be a `bool`
/// (`False`) indicating the comment was not edited, or a `String` representing the date of the
/// change.
#[derive(Clone, Debug, Deserialize, Eq, Hash, PartialEq, Serialize)]
#[serde(untagged)]
pub enum BoolOrDate {
    /// Hold a boolean type value.
    Bool(bool),
    /// Hold a string type value.
    Str(String),
}

impl ToPyObject for BoolOrDate {
    /// Convert either the Rust `bool` or `String` into a Python `bool` or `str`.
    fn to_object(&self, py: Python<'_>) -> PyObject {
        match self {
            Self::Bool(boolean) => PyBool::new(py, *boolean).into(),
            Self::Str(string) => PyString::new(py, string).into(),
        }
    }
}

/// A node object that contains comment metadata for the comment `Forest`.
#[derive(Clone, Debug, Deserialize, Eq, Hash, PartialEq, Serialize)]
#[pyclass]
pub struct CommentNode {
    /// This comment's author.
    pub author: String,
    /// The body of the comment, as Markdown.
    pub body: String,
    /// The body of the comment, as HTML.
    pub body_html: String,
    /// The comment's created UTC timestamp.
    pub created_utc: String,
    /// Whether the comment is distinguished.
    pub distinguished: Option<String>,
    /// Whether the comment has been edited. This is set to a UTC timestamp if it has been
    /// edited.
    pub edited: BoolOrDate,
    /// The comment's ID.
    pub id: String,
    /// Whether the comment author is also the author of the submission (OP).
    pub is_submitter: bool,
    /// The submission ID that the comment belongs to.
    pub link_id: String,
    /// The comment's parent ID.
    pub parent_id: String,
    /// The comment's score.
    pub score: i32,
    /// Whether the comment is stickied.
    pub stickied: bool,
    /// The comment's replies.
    #[serde(skip)]
    pub replies: Vec<CommentNode>,
}

#[pymethods]
impl CommentNode {
    /// Create a new `CommentNode`.
    #[new]
    fn new(comment_data: String) -> PyResult<Self> {
        serde_json::from_str(&comment_data).map_or_else(
            |error| {
                Err(PyValueError::new_err(format!(
                    "Could not deserialize comment data to the CommentNode struct! {}",
                    error
                )))
            },
            Ok,
        )
    }

    /// Return this `CommentNode` in a Python `dict`. This overrides the built-in Python `__dict__`
    /// dunder method.
    #[getter]
    fn __dict__(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);

        dict.set_item("author", self.author.clone())?;
        dict.set_item("body", self.body.clone())?;
        dict.set_item("body_html", self.body_html.clone())?;
        dict.set_item("created_utc", self.created_utc.clone())?;
        dict.set_item("distinguished", self.distinguished.clone())?;
        dict.set_item("edited", self.edited.clone())?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("is_submitter", self.is_submitter)?;
        dict.set_item("link_id", self.link_id.clone())?;
        dict.set_item("parent_id", self.parent_id.clone())?;
        dict.set_item("score", self.score)?;
        dict.set_item("stickied", self.stickied)?;
        dict.set_item("replies", self.replies.clone())?;

        Ok(dict.into())
    }

    /// Get this `CommentNode`'s `replies`.
    #[getter]
    fn replies(&self) -> Vec<CommentNode> {
        self.replies.clone()
    }
}

impl ToPyObject for CommentNode {
    /// Convert the `CommentNode` into a Python `Object`.
    fn to_object(&self, py: Python<'_>) -> PyObject {
        let dict = PyDict::new(py);

        dict.set_item("author", self.author.clone())
            .expect("Could not set the author attribute in the PyObject!");
        dict.set_item("body", self.body.clone())
            .expect("Could not set the body attribute in the PyObject!");
        dict.set_item("body_html", self.body_html.clone())
            .expect("Could not set the body_html attribute in the PyObject!");
        dict.set_item("created_utc", self.created_utc.clone())
            .expect("Could not set the created_utc attribute in the PyObject!");
        dict.set_item("distinguished", self.distinguished.clone())
            .expect("Could not set the distinguished attribute in the PyObject!");
        dict.set_item("edited", self.edited.clone())
            .expect("Could not set the edited attribute in the PyObject!");
        dict.set_item("id", self.id.clone())
            .expect("Could not set the id attribute in the PyObject!");
        dict.set_item("is_submitter", self.is_submitter)
            .expect("Could not set the is_submitter attribute in the PyObject!");
        dict.set_item("link_id", self.link_id.clone())
            .expect("Could not set the link_id attribute in the PyObject!");
        dict.set_item("parent_id", self.parent_id.clone())
            .expect("Could not set the parent_id attribute in the PyObject!");
        dict.set_item("score", self.score)
            .expect("Could not set the score attribute in the PyObject!");
        dict.set_item("stickied", self.stickied)
            .expect("Could not set the stickied attribute in the PyObject!");
        dict.set_item("replies", self.replies.clone())
            .expect("Could not set the replies attribute in the PyObject!");

        dict.into()
    }
}

/// The comment `Forest` - a data structure that resembles comment threads as seen on Reddit.
#[derive(Debug, Deserialize, Serialize)]
#[pyclass]
pub struct Forest {
    /// The root of the forest.
    pub root: CommentNode,
}

#[pymethods]
impl Forest {
    /// Create a new `Forest`.
    #[new]
    fn new(submission_id: String) -> PyResult<Self> {
        let root = CommentNode {
            author: "".to_string(),
            body: "".to_string(),
            body_html: "".to_string(),
            created_utc: "".to_string(),
            distinguished: None,
            edited: BoolOrDate::Bool(false),
            id: submission_id,
            is_submitter: true,
            link_id: "".to_string(),
            parent_id: "".to_string(),
            score: 0,
            stickied: false,
            replies: vec![],
        };

        Ok(Self { root })
    }

    /// An iterative implementation of depth-first search that inserts a new comment into the
    /// `Forest`.
    fn _dfs_insert(&mut self, new_comment: CommentNode) {
        let root_id = &self.root.id.clone();

        let mut stack: VecDeque<&mut CommentNode> = VecDeque::new();
        stack.push_front(&mut self.root);

        let mut visited: HashSet<String> = HashSet::new();
        visited.insert(root_id.to_string());

        let target_id = &new_comment
            .parent_id
            .split('_')
            .last()
            .unwrap_or(&new_comment.parent_id)
            .to_string();

        let mut found = false;

        while !found {
            if let Some(comment_node) = stack.pop_front() {
                for reply in comment_node.replies.iter_mut() {
                    if target_id == &reply.id {
                        reply.replies.push(new_comment.clone());
                        found = true;
                    } else {
                        let child_id = reply.id.clone();

                        if !visited.contains(child_id.as_str()) {
                            stack.push_front(reply);
                            visited.insert(child_id);
                        }
                    }
                }
            }
        }
    }

    /// Plant a new comment in the `Forest`.
    fn seed_comment(&mut self, new_comment: CommentNode) {
        let parent_id = &new_comment
            .parent_id
            .split('_')
            .last()
            .unwrap_or(&new_comment.parent_id)
            .to_string();

        if parent_id == &self.root.id {
            self.root.replies.push(new_comment);
        } else {
            self._dfs_insert(new_comment);
        }
    }

    /// Return an array of `CommentNode`s in the form of a `String`. This enables
    /// Python to `json.loads()` this string to convert the `Forest` into a Python
    /// native type.
    #[getter]
    fn comments(&self) -> String {
        serde_json::to_string(&self.root.replies).unwrap_or("None".to_string())
    }

    /// Returns the `root` of the `Forest`.
    #[getter]
    fn root(&self) -> CommentNode {
        self.root.clone()
    }
}
