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

[praw]: https://pypi.org/project/praw/
