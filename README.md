     __  __  _ __   ____
    /\ \/\ \/\`'__\/',__\
    \ \ \_\ \ \ \//\__, `\
     \ \____/\ \_\\/\____/
      \/___/  \/_/ \/___/

> **U**niversal **R**eddit **S**craper - A comprehensive Reddit scraping command-line tool written in Python.

![GitHub Workflow Status (Python)](https://img.shields.io/github/actions/workflow/status/JosephLai241/URS/python.yml?label=Python&logo=python&logoColor=blue)
![GitHub Workflow Status (Rust)](https://img.shields.io/github/actions/workflow/status/JosephLai241/URS/rust.yml?label=Rust&logo=rust&logoColor=orange)
[![Codecov](https://img.shields.io/codecov/c/gh/JosephLai241/URS?logo=Codecov)][codecov]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/JosephLai241/URS)][releases]
![Total lines](https://img.shields.io/tokei/lines/github/JosephLai241/URS)
![License](https://img.shields.io/github/license/JosephLai241/URS)

```
[-h]
[-e]
[-v]

[-t [<optional_date>]]
[--check]

[-r <subreddit> <(h|n|c|t|r|s)> <n_results_or_keywords> [<optional_time_filter>]]
    [-y]
    [--csv]
    [--rules]
[-u <redditor> <n_results>]
[-c <submission_url> <n_results>]
    [--raw]
[-b]
    [--csv]

[-lr <subreddit>]
[-lu <redditor>]

    [--nosave]
    [--stream-submissions]

[-f <file_path>]
    [--csv]
[-wc <file_path> [<optional_export_format>]]
    [--nosave]
```

# Table of Contents

- [Contact](#contact)
- [Introduction](#introduction)
- ["Where’s the Manual?"](#wheres-the-manual)
  - [`URS` Manual](#urs-manual)
- [Demo GIFs](#demo-gifs)
  - [Subreddit Scraping](#subreddit-scraping)
  - [Redditor Scraping](#redditor-scraping)
  - [Submission Comments Scraping](#submission-comments-scraping)
  - [Livestreaming Reddit](#livestreaming-reddit)
  - [Generating Word Frequencies](#generating-word-frequencies)
  - [Generating Wordclouds](#generating-wordclouds)
  - [Checking PRAW Rate Limits](#checking-praw-rate-limits)
  - [Displaying Directory Tree](#displaying-directory-tree)
- [Sponsors](#sponsors)

# Contact

Whether you are using `URS` for enterprise or personal use, I am very interested in hearing about your use case and how it has helped you achieve a goal. Additionally, please send me an email if you would like to [contribute][contributing manual link], have questions, or want to share something you have built on top of it.

You can send me an email by clicking on the badge. I look forward to hearing from you!

[![ProtonMail](https://img.shields.io/badge/ProtonMail-urs__project%40protonmail.com-informational?logo=protonmail)][urs project email]

# Introduction

This is a comprehensive Reddit scraping tool that integrates multiple features:

- Scrape Reddit via [`PRAW`][praw] (the official Python Reddit API Wrapper)
  - Scrape Subreddits
  - Scrape Redditors
  - Scrape submission comments
- Livestream Reddit via `PRAW`
  - Livestream comments submitted within Subreddits or by Redditors
  - Livestream submissions submitted within Subreddits or by Redditors
- Analytical tools for scraped data
  - Generate frequencies for words that are found in submission titles, bodies, and/or comments
  - Generate a wordcloud from scrape results

# "Where’s the Manual?"

### [`URS` Manual][urs manual]

This `README` has become too long to comfortably contain all usage information for this tool. Consequently, the information that used to be in this file has been moved to a separate manual created with [mdBook][mdbook], a Rust command-line tool for creating books from Markdown files.

> **_Note:_** You can also find the link in the About sidebar in this repository.

# Demo GIFs

Here are all the demo GIFs recorded for `URS`.

> **_Note:_** The `nd` command is [`nomad`][nomad], a modern `tree` alternative I wrote in Rust.

## [Subreddit Scraping][subreddit scraping manual link]

![subreddit demo][subreddit demo]

## [Redditor Scraping][redditor scraping manual link]

![redditor demo][redditor demo]

## [Submission Comments Scraping][submission comments scraping manual link]

![submission comments demo][submission comments demo]

## [Livestreaming Reddit][livestream scraping manual link]

![livestream subreddit demo][livestream subreddit demo]

## [Generating Word Frequencies][frequencies scraping manual link]

![frequencies demo][frequencies demo]

## [Generating Wordclouds][wordcloud scraping manual link]

![wordcloud demo][wordcloud demo]

## [Checking PRAW Rate Limits][check praw rate limits manual link]

![check praw rate limits demo][check praw rate limits demo]

## [Displaying Directory Tree][display directory tree manual link]

![display directory tree demo][display directory tree demo]

# Sponsors

This is a shout-out section for my patrons - thank you so much for sponsoring this project!

- [lolfilmworks][lolfilmworks]

<!--Manual links-->

[check praw rate limits manual link]: https://josephlai241.github.io/URS/utilities/rate-limit-checking.html
[contributing manual link]: https://josephlai241.github.io/URS/contributing/before-making-pull-or-feature-requests.html
[display directory tree manual link]: https://josephlai241.github.io/URS/utilities/tree.html
[frequencies scraping manual link]: https://josephlai241.github.io/URS/analytical-tools/frequencies-and-wordclouds.html#generating-word-frequencies
[livestream scraping manual link]: https://josephlai241.github.io/URS/livestreaming-reddit/general-information.html
[redditor scraping manual link]: https://josephlai241.github.io/URS/scraping-reddit/redditor.html
[submission comments scraping manual link]: https://josephlai241.github.io/URS/scraping-reddit/submission-comments.html
[subreddit scraping manual link]: https://josephlai241.github.io/URS/scraping-reddit/subreddit.html
[urs manual]: https://josephlai241.github.io/URS
[wordcloud scraping manual link]: https://josephlai241.github.io/URS/analytical-tools/frequencies-and-wordclouds.html#generating-wordclouds

<!-- PRAW SCRAPER DEMO GIFS -->

[check praw rate limits demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/utilities/check_rate_limit_demo.gif
[display directory tree demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/utilities/tree_demo.gif
[frequencies demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/analytical_tools/frequencies_generator_demo.gif
[livestream subreddit demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/live_scrapers/livestream_subreddit_demo.gif
[redditor demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/Redditor_demo.gif
[submission comments demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/submission_comments_demo.gif
[subreddit demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/Subreddit_demo.gif
[wordcloud demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/analytical_tools/wordcloud_generator_demo.gif

<!--Contact links-->

[urs project email]: mailto:urs_project@protonmail.com

<!--Miscellaneous links-->

[codecov]: https://codecov.io/gh/JosephLai241/URS
[mdbook]: https://github.com/rust-lang/mdBook
[nomad]: https://github.com/JosephLai241/nomad
[praw]: https://praw.readthedocs.io/en/stable/
[releases]: https://github.com/JosephLai241/URS/releases

<!--Sponsors links-->

[lolfilmworks]: https://github.com/lolfilmworks
