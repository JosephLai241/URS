# Table of Contents

- [Subreddits](#subreddits)
  - [All Flags](#all-flags)
  - [Basic Usage](#basic-usage)
  - [Filename Naming Conventions](#filename-naming-conventions)
- [Time Filters](#time-filters)
  - [Filename Naming Conventions](#filename-naming-conventions-1)
- [Subreddit Rules and Post Requirements](#subreddit-rules-and-post-requirements)
- [Bypassing the Final Settings Check](#bypassing-the-final-settings-check)

# Subreddits

![Subreddit Demo GIF][subreddit demo]

## All Flags

These are all the flags that may be used when scraping Subreddits.

```
[-r <subreddit> <(h|n|c|t|r|s)> <n_results_or_keywords> [<optional_time_filter>]]
    [-y]
    [--csv]
    [--rules]
```

## Basic Usage

```
poetry run Urs.py -r <subreddit> <(h|n|c|t|r|s)> <n_results_or_keywords>
```

**Supports exporting to CSV.** To export to CSV, include the `--csv` flag.

Specify Subreddits, the submission category, and how many results are returned from each scrape. I have also added a search option where you can search for keywords within a Subreddit.

These are the submission categories:

- Hot
- New
- Controversial
- Top
- Rising
- Search

## Filename Naming Conventions

The file names for all categories except for Search will follow this format:

```
[SUBREDDIT]-[POST_CATEGORY]-[N_RESULTS]-result(s).[FILE_FORMAT]
```

If you searched for keywords, file names will follow this format:

```
[SUBREDDIT]-Search-'[KEYWORDS]'.[FILE_FORMAT]
```

Scrape data is exported to the `subreddits` directory.

> **_NOTE:_** Up to 100 results are returned if you search for keywords within a Subreddit. You will not be able to specify how many results to keep.

# Time Filters

Time filters may be applied to some categories. Here is a table of the categories on which you can apply a time filter as well as the valid time filters.

| Categories    | Time Filters  |
| ------------- | ------------- |
| Controversial | All (default) |
| Search        | Day           |
| Top           | Hour          |
|               | Month         |
|               | Week          |
|               | Year          |

Specify the time filter after the number of results returned or keywords you want to search for:

```
poetry run Urs.py -r <subreddit> <(c|t|s)> <n_results_or_keywords> [<time_filter>]
```

If no time filter is specified, the default time filter `all` is applied. The Subreddit settings table will display `None` for categories that do not offer the additional time filter option.

## Filename Naming Conventions

If you specified a time filter, `-past-[TIME_FILTER]` will be appended to the file name before the file format like so:

```
[SUBREDDIT]-[POST_CATEGORY]-[N_RESULTS]-result(s)-past-[TIME_FILTER].[FILE_FORMAT]
```

Or if you searched for keywords:

```
[SUBREDDIT]-Search-'[KEYWORDS]'-past-[TIME_FILTER].[FILE_FORMAT]
```

# Subreddit Rules and Post Requirements

You can also include the Subreddit's rules and post requirements in your scrape data by including the `--rules` flag. **This is only compatible with JSON**. This data will be included in the `subreddit_rules` field.

If rules are included in your file, `-rules` will be appended to the end of the file name.

# Bypassing the Final Settings Check

After submitting the arguments and Reddit validation, `URS` will display a table of Subreddit scraping settings as a final check before executing. You can include the `-y` flag to bypass this and immediately scrape.

[subreddit demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/Subreddit_demo.gif?raw=true
