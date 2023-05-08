# Speeding Up Python with Rust

**Created:** May 05, 2023

# Table of Contents

- [Introduction](#introduction)
- [Some Reasons Why I Love Rust](#some-reasons-why-i-love-rust)
  - [Great Performance Without Sacrificing Memory Safety](#great-performance-without-sacrificing-memory-safety)
  - [All Bases Covered](#all-bases-covered)
  - [Compiler Error Messages Are Actually Useful](#compiler-error-messages-are-actually-useful)
  - [Fantastic Developer Ecosystem](#fantastic-developer-ecosystem)
- [Controllable Bottlenecks in `URS`](#controllable-bottlenecks-in-urs)
- [Depth-First Search](#depth---first-search)
- [Submission Comments Returned by PRAW](#submission-comments-returned-by-praw)
- [Translating Python to Rust](#translating-python-to-rust)
- [The Performance Increase](#the-performance-increase)
  - [Rust vs. Python Demo](#rust-vs-python-demo)

# Introduction

I was only proficient in Python when I initially created `URS` in 2019. Four years later, I have accumulated experience with a variety of programming languages such as JavaScript, Java, Go, and Rust. Of all the languages I have tried, I have found Rust was the only one that does everything better than all other programming languages, learning curve notwithstanding.

This document briefly details how I wrote a Python module in Rust to improve the performance of the submission comments scraper, particularly when creating the structured comments JSON format.

# Some Reasons Why I Love Rust

I will try to keep this section short, but here are a few major reasons why I love Rust. Feel free to skip this section.

## Great Performance Without Sacrificing Memory Safety

The performance you get from Rust programs are as fast as, or even faster, than those written in C or C++. The difference is Rust offers a unique way for developers to manage memory and makes it less likely for a program to have memory leaks. You have to make a conscious decision to make your Rust program _not_ memory safe. On the other hand, it is extremely easy to accidentally mess up memory management in C or C++, causing all kinds of bad shit to happen.

## All Bases Covered

Assuming you have followed good Rust development practices, you do not need to risk running into a runtime error when you deploy your application because you have already handled what should happen if something within your application fails. This means there is (typically) no unexpected behavior, which means it is less likely to crash and, if used in a professional setting, you are less likely to be called into work to fix something during the weekend just because something crashed.

Getting used to this paradigm has had a net positive on the way I write code, especially in dynamically interpreted programming languages such as Python and JavaScript. I have become more aware of where runtime errors may potentially occur and try my best to handle them in advance.

## Compiler Error Messages Are Actually Useful

The title says it all -- the error messages you see when you get compiler errors are actually useful and will clearly tell you exactly where the error is, why it happened, and what you need to do to fix it. None of that lengthy, useless bullshit you might see from an error raised in a JavaScript or Java program, for example.

Here is an example of an error message you might see when compiling a Rust program:

![useful Rust compiler error message][rust error message]

Now compare it to this:

![JavaScript is fucking garbage][shitty javascript error message]

All I can say (on Rust's behalf) is:

[![you've seen my work, it speaks for itself](https://i.imgur.com/jXqo8PC.png)][black ops ripper taunt]

> Click the screenshot to play.

## Fantastic Developer Ecosystem

`cargo` is an amazing CLI tool, making it incredibly easy to manage Rust projects. Here are some of the most notable features:

- Managing (adding/modifying/removing) dependencies
- Compiling your project
- Formatting and linting code
- Generating documentation from the docstrings you have written within your code
- Publishing your project to [crates.io][crates.io] and documentation to [docs.rs][docs.rs]

Additionally, the `Cargo.toml` file makes it very easy to set project metadata. Thankfully Python's [`Poetry`][poetry] brings a `cargo`-esque experience to Python projects, making the old `setup.py` + `requirements.txt` project format feel very outdated (which it is, as `pyproject.toml` is now the new standard way to specify project metadata per [PEP 621][pep 621]).

Upgrading Rust is also a very simple `rustup upgrade` command in the terminal.

---

I will leave the list at that for now, but I strongly encourage anyone who is looking to learn something new to [learn Rust][the rust book].

# Controllable Bottlenecks in `URS`

Diving into the practical reasons as to why I rewrote parts of `URS` in Rust, we first have to consider performance bottlenecks that I can optimize.

The biggest bottlenecks for how fast `URS` can scrape Reddit are the user's internet connection speed and the number of results returned when scraping Subreddits, Redditors, or submission comments. Unfortunately those variables are out of my control, so there is nothing I can do to optimize on that end. However, I _can_ optimize the speed of which the raw data returned from the Reddit API is processed.

The depth-first search algorithm that is used when exporting structured comments is the most obvious performance bottleneck, which is why I rewrote this functionality in Rust.

# Depth-First Search

Here's a quick refresher for the algorithm. Depth-first search is a search algorithm that traverses depth-first within a tree to find the target node, traversing deep into a node before moving on to the next in the tree. Here is a GIF visualizing the algorithm's steps:

![depth-first search demo GIF][depth-first search gif]

The time complexity for this algorithm is `O(V + E)`, where `V` is the number of vertices and `E` is the number of edges in the tree, since the algorithm explores each vertex and edge exactly one time.

# Submission Comments Returned by `PRAW`

Submission comments are returned by `PRAW` in order level. This means we get a **_P H A T_** list of comments containing all top-level comments first, followed by second-level comments, third-level comments, so on and so forth. Refer to the ["How `PRAW` Comments Are Linked" section in The Forest](./the-forest.html#how-praw-comments-are-linked) to see an example of what I am describing.

The more comments are processed while creating the structured JSON via the depth-first search algorithm, the more deeply nested those comments are within the existing comment thread structure.

It would be ideal to have this algorithm run as fast as possible, especially for Reddit submissions that contain a substantial number of comments, such as some r/AskReddit threads.

# Translating Python to Rust

I was able to write a Python module in Rust via the [`PyO3`][pyo3] crate, using [`maturin`][maturin] to compile my Rust code and install it into my Python virtual environment. Refer to the linked documentation to learn more about how you can integrate Rust with your own Python project.

I will not explain every single line of the Python to Rust translation since a Rust/`PyO3`/`maturin` tutorial is not within the scope of this document, but I will paste the depth-first search algorithm to showcase the nearly direct 1-to-1 translation between the two languages.

Here is the code for the original Python implementation:

```python
class Forest():
    def _dfs_insert(self, new_comment: CommentNode) -> None:
        stack = []
        stack.append(self.root)

        visited = set()
        visited.add(self.root)

        found = False
        while not found:
            current_comment = stack.pop(0)

            for reply in current_comment.replies:
                if new_comment.parent_id.split("_", 1)[1] == reply.id:
                    reply.replies.append(new_comment)
                    found = True
                else:
                    if reply not in visited:
                        stack.insert(0, reply)
                        visited.add(reply)

    def seed(self, new_comment: CommentNode) -> None:
        parent_id = new_comment.parent_id.split("_", 1)[1]

        if parent_id == getattr(self.root, "id"):
            self.root.replies.append(new_comment)
        else:
            self._dfs_insert(new_comment)
```

Here is the Rust translation:

```rust
impl Forest {
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
}
```

> Refer to the [`taisun/`][taisun] directory to view the full Rust implementation.

# The Performance Increase

I have no words for how much faster the Rust implementation is compared to the original Python implementation. All I can do is provide you with this screenshot and let you interpret the results for yourself. The timestamp in the far right column is the time elapsed in `HH:MM:SS`.

![DAMN BOI RUST FAST BOI THAT'S A FAST ASS BOI DAMN screenshot][damn that rust fast]

> I hope the emojis make it obvious which progress bar corresponds to which implementation, but just to be extra clear: 🐍 = Python, 🦀 = Rust.

> This test was run on a 2021 MacBook Pro with the binned M1 Pro chip.

## Rust vs. Python Demo

You do not have to take my word for it -- I have put together a small demo located on the [`rust-demo` branch][rust demo branch] in the repository.

The demo branch includes a JSON file which contains 56,107 unstructured comments scraped from [this r/AskReddit post][r/askreddit post with hella comments]. The demo Python script will read the unstructured comments from the JSON file and run the depth-first search algorithm in both Python and Rust concurrently. Progress bars for each task will visualize the progress made with each implementation and display the time elapsed at the far right column.

Run the following commands to install and run the demo:

```
git clone -b rust-demo https://github.com/JosephLai241/URS.git --depth=1
poetry install

# You do not need to run the following command if the virtualenv is already
# activated.
#
# If this command fails/does not activate the virtualenv, run
# `source .venv/bin/activate` to activate the virtualenv created by `Poetry`.
poetry shell

maturin develop --release
poetry run python rust_vs_python.py
```

[black ops ripper taunt]: https://www.youtube.com/embed/AgY5WyYo5no?start=1&end=5
[crates.io]: https://crates.io
[damn that rust fast]: https://i.imgur.com/pTXblAV.png
[depth-first search gif]: https://upload.wikimedia.org/wikipedia/commons/7/7f/Depth-First-Search.gif
[docs.rs]: https://docs.rs
[maturin]: https://www.maturin.rs/tutorial.html
[poetry]: https://python-poetry.org/
[pep 621]: https://peps.python.org/pep-0621/
[pyo3]: https://pyo3.rs/v0.12.3/
[r/askreddit post with hella comments]: https://www.reddit.com/r/AskReddit/comments/ifomdz/what_old_video_games_do_you_still_play_regularly/
[rust demo branch]: https://github.com/JosephLai241/URS/tree/rust-demo
[rust error message]: https://blog.rust-lang.org/images/2020-05-15-five-years-of-rust/borrow-error-1.43.0.png
[shitty javascript error message]: https://i.stack.imgur.com/QX9zY.png
[taisun]: https://github.com/JosephLai241/URS/tree/master/taisun
[the rust book]: https://doc.rust-lang.org/book/
