# Rust vs. Python Demo

This branch contains a Python script demonstrating the performance differences between a module written in Rust, and one written in native Python.

# "What happens when I run this demo?"

I have included a JSON file containing 56,107 unstructured comments that were scraped from [this r/AskReddit post][askreddit post]. The demo will run both Rust and Python implementations concurrently and display a progress bar for each task. The far right columns contain the number of comments processed and the total number of comments to process as well as the time elapsed.

Here is a screenshot of one particular run:

![Rust vs Python demo screenshot][rust vs python demo screenshot]

> This test was run on a 2021 MacBook Pro with the binned M1 Pro chip.

# Running the Demo

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
cd python/
poetry run python rust_vs_python.py
```

[askreddit post]: https://www.reddit.com/r/AskReddit/comments/ifomdz/what_old_video_games_do_you_still_play_regularly/
[rust vs python demo screenshot]: https://i.imgur.com/pTXblAV.png
