"""
Rust vs. Python
===============

This script demonstrates the performance differences between a module written in
Rust, and a Python-native module.

Here, we are testing an iterative implementation of a depth-first search algorithm
that is used to create structured comments.

The included JSON file, "What old video games do you still play regularly_-all-raw.json",
is an unmodified export of a very popular r/AskReddit thread. This JSON file contains
56,107 unstructured comments, all of which will be passed through the same iterative
depth-first search algorithm implemented in Rust and Python.
"""

import json
import os
import signal
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Any, Dict, List

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    RenderableColumn,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)
from taisun.comments_utils import CommentNode, Forest

done_event = Event()


def handle_sigint(_signum, _frame) -> None:
    """
    Handle a SIGINT signal from the user (ie. `<Ctrl + C>`).
    """

    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)


progress = Progress(
    SpinnerColumn(spinner_name="noise"),
    TextColumn("[{task.fields[color]}]{task.fields[label]}", justify="right"),
    BarColumn(bar_width=None),
    MofNCompleteColumn(),
    RenderableColumn(renderable="|"),
    TimeElapsedColumn(),
)


class PyCommentNode:
    """
    Defining a node object that stores comment metadata for the comments tree.
    """

    def __init__(self, metadata: Dict[str, Any]) -> None:
        """
        Set the node's comment data.

        :param dict[str, Any] metadata: A `dict[str, Any]` containing comment metadata.
        """

        for key, value in metadata.items():
            self.__setattr__(key, value)

        self.replies = []


class PyForest:
    """
    Methods to nurture the comment forest.
    """

    def __init__(self, submission_id: str) -> None:
        """
        Initialize the collective root.

        :param str submission_id: The submission's ID.
        """

        self.root = PyCommentNode({"id": submission_id})

    def _dfs_insert(self, new_comment: PyCommentNode) -> None:
        """
        An iterative implementation of depth-first search to insert a new comment
        into a comment tree.

        :param PyCommentNode new_comment: A new `PyCommentNode` to insert into the
            collective comment tree.
        """

        stack = []
        stack.append(self.root)

        visited = set()
        visited.add(self.root.id)

        found = False
        while not found:
            current_comment = stack.pop(0)

            for reply in current_comment.replies:
                if new_comment.parent_id.split("_", 1)[1] == reply.id:
                    reply.replies.append(new_comment)
                    found = True
                else:
                    if reply.id not in visited:
                        stack.insert(0, reply)
                        visited.add(reply.id)

    def seed(self, new_comment: PyCommentNode) -> None:
        """
        Insert a new `PyCommentNode` into a comment tree within the Forest.

        :param PyCommentNode new_comment: A new `PyCommentNode` to insert into the
            collective comment tree.
        """

        parent_id = new_comment.parent_id.split("_", 1)[1]

        if parent_id == getattr(self.root, "id"):
            self.root.replies.append(new_comment)
        else:
            self._dfs_insert(new_comment)


class EncodeNode(json.JSONEncoder):
    """
    Methods to serialize CommentNodes for JSON export.
    """

    def default(self, obj: Any) -> Dict[str, Any]:
        """
        Override the default JSONEncoder `default()` method.

        :param Any obj: A `CommentNode` to convert into a `dict[str, Any]`.

        :returns: A `dict[str, Any]` containing `CommentNode` data.
        :rtype: `dict[str, Any]`
        """

        return obj.__dict__


def run_python_test(task_id: TaskID, submission_comments: List[Dict[str, Any]]) -> None:
    """
    Run the Python implementation of depth-first search.

    :param list[dict[str, Any]] submission_comments: A `list[dict[str, Any]]`
        containing submission comments extracted from the provided JSON file.
    """

    progress.start_task(task_id)

    forest = PyForest("ifomdz")

    for comment in submission_comments:
        if done_event.is_set():
            return

        comment_node = PyCommentNode(comment)
        forest.seed(comment_node)

        progress.update(task_id, advance=1)

    export_path = "../demo-results/python_comments.json"
    with open(export_path, "w", encoding="utf-8") as python_file:
        json.dump(forest.root.replies, python_file, cls=EncodeNode, indent=2)


def run_rust_test(task_id: TaskID, submission_comments: List[Dict[str, Any]]) -> None:
    """
    Run the Rust implementation of depth-first search.

    :param list[dict[str, Any]] submission_comments: A `list[dict[str, Any]]`
        containing submission comments extracted from the provided JSON file.
    """

    progress.start_task(task_id)

    forest = Forest("ifomdz")

    for comment in submission_comments:
        if done_event.is_set():
            return

        comment_node = CommentNode(json.dumps(comment))
        forest.seed_comment(comment_node)

        progress.update(task_id, advance=1)

    export_path = "../demo-results/rust_comments.json"
    with open(export_path, "w", encoding="utf-8") as rust_file:
        json.dump(forest.root.replies, rust_file, cls=EncodeNode, indent=2)


def main() -> None:
    """
    Run the Rust vs. Python depth-first search performance tests.
    """

    results_directory_path = "../demo-results"
    if not os.path.isdir(results_directory_path):
        os.makedirs(results_directory_path)

    file_path = (
        "../samples/What old video games do you still play regularly_-all-raw.json"
    )

    try:
        with open(file_path, "r", encoding="utf-8") as submission_json:
            submission_comments = json.load(submission_json).get("data").get("comments")

            total_comments = len(submission_comments)

            with progress:
                with ThreadPoolExecutor(max_workers=2) as pool:
                    python_task_id = progress.add_task(
                        "Seed Forest",
                        color="bold blue",
                        label="Seeding Forest | 🐍",
                        total=total_comments,
                    )
                    rust_task_id = progress.add_task(
                        "Seed Forest",
                        color="bold dark_orange3",
                        label="Seeding Forest | 🦀",
                        total=total_comments,
                    )

                    pool.submit(run_python_test, python_task_id, submission_comments)
                    pool.submit(run_rust_test, rust_task_id, submission_comments)

    except Exception as e:
        print(f"SOMETHING FUCKED UP: {e}")


if __name__ == "__main__":
    main()
