```
 __  __  _ __   ____
/\ \/\ \/\`'__\/',__\
\ \ \_\ \ \ \//\__, `\
 \ \____/\ \_\\/\____/
  \/___/  \/_/ \/___/
```

> **U**niversal **R**eddit **S**craper - A comprehensive Reddit scraping command-line tool written in Python.

![GitHub Workflow Status (Python)](https://img.shields.io/github/actions/workflow/status/JosephLai241/URS/python.yml?label=Python&logo=python&logoColor=blue)
![GitHub Workflow Status (Rust)](https://img.shields.io/github/actions/workflow/status/JosephLai241/URS/rust.yml?label=Rust&logo=rust&logoColor=orange)
[![Codecov](https://img.shields.io/codecov/c/gh/JosephLai241/URS?logo=Codecov)][codecov]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/JosephLai241/URS)][releases]
![Total lines](https://img.shields.io/tokei/lines/github/JosephLai241/URS)
![License](https://img.shields.io/github/license/JosephLai241/URS)

# Sponsors

<p align="center">
  <a href="https://dashboard.thordata.com/register?invitation_code=8I13V2C7">
    <img src="https://github.com/user-attachments/assets/67052ea0-d05c-4fd5-998c-f819fd233a8a" />
  </a>
</p>

<p align="center" style="max-width: 500px; margin: auto;">
  <strong>Thordata</strong>’s tools are particularly useful in scenarios that require large-scale web scraping through their 
  <a href="https://www.thordata.com/products/web-scraper/?ls=EDBORvrR&lk=wb">Web Scraper API</a>
  , API-based data extraction, or reliable 
  <a href="https://www.thordata.com/products/residential-proxies/?ls=EDBORvrR&lk=wb">Proxy</a> 
  infrastructure.
  If you plan to use Thordata's tools, you can support the project via this <a href="https://dashboard.thordata.com/register?invitation_code=8I13V2C7">affiliate link</a>.
</p>

## Previous Sponsors

- [lolfilmworks]

# Table of Contents

- [Contact](#contact)
- [Introduction](#introduction)
- [Usage Overview](#usage-overview)
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

# Usage Overview

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

# "Where’s the Manual?"

### [`URS` Manual][urs manual]

This `README` has become too long to comfortably contain all usage information for this tool. Consequently, the information that used to be in this file has been moved to a separate manual created with [mdBook], a Rust command-line tool for creating books from Markdown files.

> **_Note:_** You can also find the link in the About sidebar in this repository.

# Demo GIFs

Here are all the demo GIFs recorded for `URS`.

> **_Note:_** The `nd` command is [`nomad`][nomad], a modern `tree` alternative I wrote in Rust.

## [Subreddit Scraping][subreddit scraping manual link]

![subreddit demo]

## [Redditor Scraping][redditor scraping manual link]

![redditor demo]

## [Submission Comments Scraping][submission comments scraping manual link]

![submission comments demo]

## [Livestreaming Reddit][livestream scraping manual link]

![livestream subreddit demo]

## [Generating Word Frequencies][frequencies scraping manual link]

![frequencies demo]

## [Generating Wordclouds][wordcloud scraping manual link]

![wordcloud demo]

## [Checking PRAW Rate Limits][check praw rate limits manual link]

![check praw rate limits demo]

## [Displaying Directory Tree][display directory tree manual link]

![display directory tree demo]

[check praw rate limits demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/utilities/check_rate_limit_demo.gif
[check praw rate limits manual link]: https://josephlai241.github.io/URS/utilities/rate-limit-checking.html
[codecov]: https://codecov.io/gh/JosephLai241/URS
[contributing manual link]: https://josephlai241.github.io/URS/contributing/before-making-pull-or-feature-requests.html
[display directory tree demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/utilities/tree_demo.gif
[display directory tree manual link]: https://josephlai241.github.io/URS/utilities/tree.html
[frequencies demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/analytical_tools/frequencies_generator_demo.gif
[frequencies scraping manual link]: https://josephlai241.github.io/URS/analytical-tools/frequencies-and-wordclouds.html#generating-word-frequencies
[livestream scraping manual link]: https://josephlai241.github.io/URS/livestreaming-reddit/general-information.html
[livestream subreddit demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/live_scrapers/livestream_subreddit_demo.gif
[lolfilmworks]: https://github.com/lolfilmworks
[mdbook]: https://github.com/rust-lang/mdBook
[nomad]: https://github.com/JosephLai241/nomad
[praw]: https://praw.readthedocs.io/en/stable/
[redditor demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/Redditor_demo.gif
[redditor scraping manual link]: https://josephlai241.github.io/URS/scraping-reddit/redditor.html
[releases]: https://github.com/JosephLai241/URS/releases
[submission comments demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/submission_comments_demo.gif
[submission comments scraping manual link]: https://josephlai241.github.io/URS/scraping-reddit/submission-comments.html
[subreddit demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/Subreddit_demo.gif
[subreddit scraping manual link]: https://josephlai241.github.io/URS/scraping-reddit/subreddit.html
[urs manual]: https://josephlai241.github.io/URS
[urs project email]: mailto:urs_project@protonmail.com
[wordcloud demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/analytical_tools/wordcloud_generator_demo.gif
[wordcloud scraping manual link]: https://josephlai241.github.io/URS/analytical-tools/frequencies-and-wordclouds.html#generating-wordclouds
