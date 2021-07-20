     __  __  _ __   ____  
    /\ \/\ \/\`'__\/',__\ 
    \ \ \_\ \ \ \//\__, `\
     \ \____/\ \_\\/\____/
      \/___/  \/_/ \/___/... Universal Reddit Scraper 

![GitHub top language](https://img.shields.io/github/languages/top/JosephLai241/URS?logo=Python)
[![PRAW Version](https://img.shields.io/badge/PRAW-7.3.0-red?logo=Reddit)][PRAW]
[![Build Status](https://img.shields.io/github/workflow/status/JosephLai241/URS/Pytest?logo=github)][GitHub Workflow Status]
[![Codecov](https://img.shields.io/codecov/c/gh/JosephLai241/URS?logo=Codecov)][Codecov]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/JosephLai241/URS)][Releases]
![Total lines](https://img.shields.io/tokei/lines/github/JosephLai241/URS)
![License](https://img.shields.io/github/license/JosephLai241/URS)

```
usage: $ Urs.py
     
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
    [-wc <file_path> [<optional_export_format>]
        [--nosave]
```

# Table of Contents

* [Contact](#contact)
* [Introduction](#introduction)
* [Installation](#installation)
    + [Troubleshooting](#troubleshooting)
        * [`ModuleNotFoundError`](#modulenotfounderror)
* [Exporting](#exporting)
    + [Export File Format](#export-file-format)
        * [Exporting to CSV](#exporting-to-csv)
    + [Export Directory Structure](#export-directory-structure)
        * [PRAW Scrapers](#praw-scrapers)
        * [PRAW Livestream Scrapers](#praw-livestream-scrapers)
        * [Analytical Tools](#analytical-tools)
        * [Example Directory Structure](#example-directory-structure)
* [URS Overview](#urs-overview)
    + [Scrape Speeds](#scrape-speeds)
    + [Scraping Reddit via PRAW](#scraping-reddit-via-praw)
        * [Getting Started](#getting-started)
        * [Rate Limits](#rate-limits)
        * [Table of All Subreddit, Redditor, and Submission Comments Attributes](#a-table-of-all-subreddit-redditor-and-submission-comments-attributes)
        * [Available Flags](#available-flags)
        * [Subreddits](#subreddits)
            + [Time Filters](#time-filters)
            + [Subreddit Rules and Post Requirements](#subreddit-rules-and-post-requirements)
            + [Bypassing the Final Settings Check](#bypassing-the-final-settings-check)
        * [Redditors](#redditors)
        * [Submission Comments](#submission-comments)
            + [Number of Comments Returned](#number-of-comments-returned)
            + [Structured Comments](#structured-comments)
            + [Raw Comments](#raw-comments)
    + [Livestreaming Reddit via PRAW](#livestreaming-reddit-via-praw)
        * [Displayed vs. Saved Attributes](#displayed-vs-saved-attributes)
        * [Available Flags](#available-flags-1)
        * [Livestreaming Subreddits](#livestreaming-subreddits)
        * [Livestreaming Redditors](#livestreaming-redditors)
        * [Do Not Save Livestream to File](#do-not-save-livestream-to-file)
    + [Analytical Tools](#analytical-tools-1)
        * [Target Fields](#target-fields)
        * [File Names](#file-names)
        * [Available Flags](#available-flags-2)
        * [Generating Word Frequencies](#generating-word-frequencies)
        * [Generating Wordclouds](#generating-wordclouds)
            + [Display Wordcloud Instead of Saving](#display-wordcloud-instead-of-saving)
    + [Utilities](#utilities)
        * [Display Directory Tree](#display-directory-tree)
        * [Check PRAW Rate Limits](#check-praw-rate-limits)
* [Sponsors](#sponsors)
* [Contributors](#contributors)
* [Contributing](#contributing)
    + [Before Making Pull or Feature Requests](#before-making-pull-or-feature-requests)
    + [Building on Top of URS](#building-on-top-of-urs)
    + [Making Pull or Feature Requests](#making-pull-or-feature-requests)
* [Derivative Projects](#derivative-projects)
    + [skiwheelr/URS](#skiwheelrurs)
* Supplemental Documents
    + [How to get Reddit API Credentials for PRAW][How to get Reddit API Credentials for PRAW]
    + [Error Messages][Error Messages]
    + [2-Factor Authentication][2-Factor Authentication]
    + [Releases/Changelog][Releases/Changelog]
    + [Some Linux Tips][Some Linux Tips]
    + [The Forest][The Forest]

# Contact

Whether you are using URS for enterprise or personal use, I am very interested in hearing about your use case and how it has helped you achieve a goal. 

Additionally, please send me an email if you would like to [contribute](#contributing), have questions, or want to share something you have built on top of it. 

You can send me an email or leave a note by clicking on either of these badges. I look forward to hearing from you!

[![Email](https://img.shields.io/badge/Email-urs__project%40protonmail.com-informational?logo=ProtonMail)][URS Project Email]
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-blue)][Say Thanks!]

# Introduction

This is a comprehensive Reddit scraping tool that integrates multiple features:

* Scrape Reddit via [`PRAW`][PRAW] (the official Python Reddit API Wrapper)
    + Scrape Subreddits
    + Scrape Redditors
    + Scrape submission comments
* Livestream Reddit via `PRAW`
    + Livestream comments submitted within Subreddits or by Redditors
    + Livestream submissions submitted within Subreddits or by Redditors
* Analytical tools for scraped data
    + Generate frequencies for words that are found in submission titles, bodies, and/or comments
    + Generate a wordcloud from scrape results

See the [Getting Started](#getting-started) section to get your API credentials.

# Installation

> ***NOTE:* Requires Python 3.7+**

```
git clone --depth=1 https://github.com/JosephLai241/URS.git
cd URS
pip3 install . -r requirements.txt
```

## Troubleshooting

### `ModuleNotFoundError`

You may run into an error that looks like this:

```
Traceback (most recent call last):
  File "/home/joseph/URS/urs/./Urs.py", line 30, in <module>
    from urs.utils.Logger import LogMain
ModuleNotFoundError: No module named 'urs'
```

This means you will need to add the `URS` directory to your `PYTHONPATH`. [Here is a link that explains how to do so for each operating system][Export PYTHONPATH Help].

# Exporting

## Export File Format

**All files except for those generated by the wordcloud tool are exported to JSON by default**. Wordcloud files are exported to PNG by default. 

URS supports exporting to CSV as well, but JSON is the more versatile option.

### Exporting to CSV

You will have to include the `--csv` flag to export to CSV.

You can only export to CSV when using:

+ The Subreddit scrapers
+ The word frequencies generator

These tools are also suitable for CSV format and are optimized to do so if you want to use that format instead.

The `--csv` flag is ignored if it is present while using any of the other scrapers.

## Export Directory Structure

All exported files are saved within the `scrapes` directory and stored in a sub-directory labeled with the date. Many more sub-directories may be created in the date directory. Sub-directories are only created when its respective tool is run. For example, if you only use the Subreddit scraper, only the `subreddits` directory is created.

### PRAW Scrapers

The `subreddits`, `redditors`, or `comments` directories may be created.

### PRAW Livestream Scrapers

The `livestream` directory is created when you run any of the livestream scrapers. Within it, the `subreddits` or `redditors` directories may be created.

### Analytical Tools

The `analytics` directory is created when you run any of the analytical tools. Within it, the `frequencies` or `wordclouds` directories may be created. See the [Analytical Tools](#analytical-tools-1) section for more information.

### Example Directory Structure

This is the [samples][Samples] directory structure generated by the [tree command][tree].

```
scrapes/
└── 06-02-2021
    ├── analytics
    │   ├── frequencies
    │   │   ├── comments
    │   │   │   └── What’s something from the 90s you miss_-all.json
    │   │   ├── livestream
    │   │   │   └── subreddits
    │   │   │       └── askreddit-comments-20_44_11-00_01_10.json
    │   │   └── subreddits
    │   │       └── cscareerquestions-search-'job'-past-year-rules.json
    │   └── wordcloud
    │       ├── comments
    │       │   └── What’s something from the 90s you miss_-all.png
    │       ├── livestream
    │       │   └── subreddits
    │       │       └── askreddit-comments-20_44_11-00_01_10.png
    │       └── subreddits
    │           └── cscareerquestions-search-'job'-past-year-rules.png
    ├── comments
    │   └── What’s something from the 90s you miss_-all.json
    ├── livestream
    │   └── subreddits
    │       ├── askreddit-comments-20_44_11-00_01_10.json
    │       └── askreddit-submissions-20_46_12-00_01_52.json
    ├── redditors
    │   └── spez-5-results.json
    ├── subreddits
    │   ├── askreddit-hot-10-results.json
    │   └── cscareerquestions-search-'job'-past-year-rules.json
    └── urs.log
```

# URS Overview

## Scrape Speeds

Your internet connection speed is the primary bottleneck that will establish the scrape duration; however, there are additional bottlenecks such as:

* The number of results returned for Subreddit or Redditor scraping.
* The submission's popularity (total number of comments) for submission comments scraping.

## Scraping Reddit via PRAW

### Getting Started

It is very quick and easy to get Reddit API credentials. Refer to [my guide to get your credentials][How to get Reddit API Credentials for PRAW], then update the environment variables located in `.env`.

### Rate Limits

Yes, PRAW has rate limits. These limits are proportional to how much karma you have accumulated - the higher the karma, the higher the rate limit. This has been implemented to mitigate spammers and bots that utilize PRAW.

Rate limit information for your account is displayed in a small table underneath the successful login message each time you run any of the PRAW scrapers. I have also added a `--check` flag if you want to quickly view this information.

URS will display an error message as well as the rate limit reset date if you have used all your available requests.

There are a couple ways to circumvent rate limits:

* Scrape intermittently
* Use an account with high karma to get your PRAW credentials
* Scrape less results per run

Available requests are refilled if you use the PRAW scrapers intermittently, which might be the best solution. This can be especially helpful if you have automated URS and are not looking at the output on each run.

### A Table of All Subreddit, Redditor, and Submission Comments Attributes

These attributes are included in each scrape. 

| Subreddits (submissions) | Redditors                        | Submission Comments |
|--------------------------|----------------------------------|---------------------|
| `author`                 | `comment_karma`                  | `author`            |
| `created_utc`            | `created_utc`                    | `body`              |
| `distinguished`          | `fullname`                       | `body_html`         |
| `edited`                 | `has_verified_email`             | `created_utc`       |
| `id`                     | `icon_img`                       | `distinguished`     |
| `is_original_content`    | `id`                             | `edited`            |
| `is_self`                | `is_employee`                    | `id`                |
| `link_flair_text`        | `is_friend`                      | `is_submitter`      |
| `locked`                 | `is_mod`                         | `link_id`           |
| `name`                   | `is_gold`                        | `parent_id`         |
| `num_comments`           | `link_karma`                     | `score`             |
| `nsfw`                   | `name`                           | `stickied`          |
| `permalink`              | `subreddit`                      |                     |
| `score`                  | \*`trophies`                     |                     |
| `selftext`               | \*`comments`                     |                     |
| `spoiler`                | \*`controversial`                |                     |
| `stickied`               | \*`downvoted` (may be forbidden) |                     |
| `title`                  | \*`gilded`                       |                     |
| `upvote_ratio`           | \*`gildings` (may be forbidden)  |                     |
| `url`                    | \*`hidden` (may be forbidden)    |                     |
|                          | \*`hot`                          |                     |
|                          | \*`moderated`                    |                     |
|                          | \*`multireddits`                 |                     |
|                          | \*`new`                          |                     |
|                          | \*`saved` (may be forbidden)     |                     |
|                          | \*`submissions`                  |                     |
|                          | \*`top`                          |                     |
|                          | \*`upvoted` (may be forbidden)   |                     |

\*Includes additional attributes; see [Redditors](#redditors) section for more information. 

### Available Flags

```
[-r <subreddit> <(h|n|c|t|r|s)> <n_results_or_keywords> [<optional_time_filter>]] 
    [-y]
    [--csv]
    [--rules]
[-u <redditor> <n_results>] 
[-c <submission_url> <n_results>]
    [--raw] 
[-b]
    [--csv]
```

---

### Subreddits

![Subreddit Demo GIF][Subreddit Demo]

\*This GIF is uncut.

**Usage:** `$ ./Urs.py -r SUBREDDIT (H|N|C|T|R|S) N_RESULTS_OR_KEYWORDS` 

**Supported export formats:** JSON and CSV. To export to CSV, include the `--csv` flag.

You can specify Subreddits, the submission category, and how many results are returned from each scrape. I have also added a search option where you can search for keywords within a Subreddit.

These are the submission categories:

* Hot
* New
* Controversial
* Top
* Rising
* Search

The file names for all categories except for Search will follow this format: 

`"[SUBREDDIT]-[POST_CATEGORY]-[N_RESULTS]-result(s).[FILE_FORMAT]"`

If you searched for keywords, file names will follow this format:

`"[SUBREDDIT]-Search-'[KEYWORDS]'.[FILE_FORMAT]"`

Scrape data is exported to the `subreddits` directory.

> ***NOTE:*** Up to 100 results are returned if you search for keywords within a Subreddit. You will not be able to specify how many results to keep.

### Time Filters

Time filters may be applied to some categories. Here is a table of the categories on which you can apply a time filter as well as the valid time filters.

| Categories    | Time Filters  | 
|---------------|---------------|
| Controversial | All (default) |
| Top           | Day           |
| Search        | Hour          |
|               | Month         | 
|               | Week          |
|               | Year          |

Specify the time filter after the number of results returned or keywords you want to search for.

**Usage:** `$ ./Urs.py -r SUBREDDIT (C|T|S) N_RESULTS_OR_KEYWORDS OPTIONAL_TIME_FILTER`

If no time filter is specified, the default time filter `all` is applied. The Subreddit settings table will display `None` for categories that do not offer the additional time filter option.

If you specified a time filter, `-past-[TIME_FILTER]` will be appended to the file name before the file format like so: 

`"[SUBREDDIT]-[POST_CATEGORY]-[N_RESULTS]-result(s)-past-[TIME_FILTER].[FILE_FORMAT]"` 

Or if you searched for keywords:

`"[SUBREDDIT]-Search-'[KEYWORDS]'-past-[TIME_FILTER].[FILE_FORMAT]"`

### Subreddit Rules and Post Requirements

You can also include the Subreddit's rules and post requirements in your scrape data by including the `--rules` flag. **This only works when exporting to JSON**. This data will be included in the `subreddit_rules` field.

If rules are included in your file, `-rules` will be appended to the end of the file name.

### Bypassing the Final Settings Check

After submitting the arguments and Reddit validation, URS will display a table of Subreddit scraping settings as a final check before executing. You can include the `-y` flag to bypass this and immediately scrape.

---

### Redditors

![Redditor Demo GIF][Redditor Demo]

\*This GIF has been cut for demonstration purposes.

**Usage:** `$ ./Urs.py -u REDDITOR N_RESULTS` 

**Supported export formats:** JSON.

You can also scrape Redditor profiles and specify how many results are returned.

Redditor information will be included in the `information` field and includes the following attributes:

| Redditor Information |
|----------------------|
| `comment_karma`      |
| `created_utc`        |
| `fullname`           |
| `has_verified_email` |
| `icon_img`           |
| `id`                 |
| `is_employee`        |
| `is_friend`          |
| `is_mod`             |
| `is_gold`            |
| `link_karma`         |
| `name`               |
| `subreddit`          |
| `trophies`           |

Redditor interactions will be included in the `interactions` field. Here is a table of all Redditor interaction attributes that are also included, how they are sorted, and what type of Reddit objects are included in each.

| Attribute Name | Sorted By/Time Filter                       | Reddit Objects           |
|----------------|---------------------------------------------|--------------------------|
| Comments       | Sorted By: New                              | Comments                 |
| Controversial  | Time Filter: All                            | Comments and submissions |
| Downvoted      | Sorted By: New                              | Comments and submissions |
| Gilded         | Sorted By: New                              | Comments and submissions |
| Gildings       | Sorted By: New                              | Comments and submissions |
| Hidden         | Sorted By: New                              | Comments and submissions |
| Hot            | Determined by other Redditors' interactions | Comments and submissions |
| Moderated      | N/A                                         | Subreddits               |
| Multireddits   | N/A                                         | Multireddits             |
| New            | Sorted By: New                              | Comments and submissions |
| Saved          | Sorted By: New                              | Comments and submissions |
| Submissions    | Sorted By: New                              | Submissions              |
| Top            | Time Filter: All                            | Comments and submissions |
| Upvoted        | Sorted By: New                              | Comments and submissions |

These attributes contain comments or submissions. Subreddit attributes are also included within both. 

This is a table of all attributes that are included for each Reddit object:

| Subreddits              | Comments        | Submissions           | Multireddits       | Trophies      |
|-------------------------|-----------------|-----------------------|--------------------|---------------|
| `can_assign_link_flair` | `body`          | `author`              | `can_edit`         | `award_id`    |
| `can_assign_user_flair` | `body_html`     | `created_utc`         | `copied_from`      | `description` |
| `created_utc`           | `created_utc`   | `distinguished`       | `created_utc`      | `icon_40`     |
| `description`           | `distinguished` | `edited`              | `description_html` | `icon_70`     |
| `description_html`      | `edited`        | `id`                  | `description_md`   | `name`        |
| `display_name`          | `id`            | `is_original_content` | `display_name`     | `url`         |
| `id`                    | `is_submitter`  | `is_self`             | `name`             |               |
| `name`                  | `link_id`       | `link_flair_text`     | `nsfw`             |               |
| `nsfw`                  | `parent_id`     | `locked`              | `subreddits`       |               |
| `public_description`    | `score`         | `name`                | `visibility`       |               |
| `spoilers_enabled`      | `stickied`      | `num_comments`        |                    |               |
| `subscribers`           | *`submission`   | `nsfw`                |                    |               |
| `user_is_banned`        | `subreddit_id`  | `permalink`           |                    |               |
| `user_is_moderator`     |                 | `score`               |                    |               |
| `user_is_subscriber`    |                 | `selftext`            |                    |               |
|                         |                 | `spoiler`             |                    |               |
|                         |                 | `stickied`            |                    |               |
|                         |                 | *`subreddit`          |                    |               |
|                         |                 | `title`               |                    |               |
|                         |                 | `upvote_ratio`        |                    |               |
|                         |                 | `url`                 |                    |               |

\* Contains additional metadata.

The file names will follow this format: 

`"[USERNAME]-[N_RESULTS]-result(s).json"` 

Scrape data is exported to the `redditors` directory.

> ***NOTE:*** If you are not allowed to access a Redditor's lists, PRAW will raise a 403 HTTP Forbidden exception and the program will just append `"FORBIDDEN"` underneath that section in the exported file. 

> ***NOTE:*** The number of results returned are applied to all attributes. I have not implemented code to allow users to specify different number of results returned for individual attributes. 

---

### Submission Comments

![Submission Comments Demo GIF][Submission Comments Demo]

\*This GIF has been cut for demonstration purposes.

**Usage:** `$ ./Urs.py -c SUBMISSION_URL N_RESULTS` 

**Supported export formats:** JSON.

You can also scrape comments from submissions and specify the number of results returned.

Submission metadata will be included in the `submission_metadata` field and includes the following attributes:

| Submission Attributes |
|-----------------------|
| `author`              |
| `created_utc`         |
| `distinguished`       |
| `edited`              |
| `is_original_content` |
| `is_self`             |
| `link_flair_text`     |
| `locked`              |
| `nsfw`                |
| `num_comments`        |
| `permalink`           |
| `score`               |
| `selftext`            |
| `spoiler`             |
| `stickied`            |
| `subreddit`           |
| `title`               |
| `upvote_ratio`        |

If the submission contains a gallery, the attributes `gallery_data` and `media_metadata` will be included.

Comments are written to the `comments` field. They are sorted by "Best", which is the default sorting option when you visit a submission.

PRAW returns submission comments in level order, which means scrape speeds are proportional to the submission's popularity.

The file names will generally follow this format: 

`"[POST_TITLE]-[N_RESULTS]-result(s).json"` 

Scrape data is exported to the `comments` directory.

### Number of Comments Returned

You can scrape all comments from a submission by passing in `0` for `N_RESULTS`. Subsequently, `[N_RESULTS]-result(s)` in the file name will be replaced with `all`. 

Otherwise, specify the number of results you want returned. If you passed in a specific number of results, the structured export will return up to `N_RESULTS` top level comments and include all of its replies.

### Structured Comments

**This is the default export style.** Structured scrapes resemble comment threads on Reddit. This style takes just a little longer to export compared to the raw format because URS uses [depth-first search][Depth-First Search] to create the comment `Forest` after retrieving all comments from a submission.

If you want to learn more about how it works, refer to [this additional document where I describe how I implemented the `Forest`][The Forest].

### Raw Comments

Raw scrapes do not resemble comment threads, but returns all comments on a submission in level order: all top-level comments are listed first, followed by all second-level comments, then third, etc.

You can export to raw format by including the `--raw` flag. `-raw` will also be appended to the end of the file name.

## Livestreaming Reddit via PRAW

These tools may be used to livestream comments or submissions submitted within Subreddits or by Redditors. 

**Comments are streamed by default**. To stream submissions instead, include the `--stream-submissions` flag.

**New comments or submissions will continue to display within your terminal until you abort the stream using `Ctrl + C`**. 

The filenames will follow this format:

`[SUBREDDIT_OR_REDDITOR]-[comments_OR_submissions]-[START_TIME_IN_HOURS_MINUTES_SECONDS]-[DURATION_IN_HOURS_MINUTES_SECONDS].json`

This file is saved in the main `livestream` directory into the `subreddits` or `redditors` directory depending on which stream was run.

Reddit objects will be written to this JSON file in real time. After aborting the stream, the filename will be updated with the start time and duration.

### Displayed vs. Saved Attributes

Displayed comment and submission attributes have been stripped down to essential fields to declutter the output. Here is a table of what is shown during the stream:

| Comment Attributes           | Submission Attributes |
|------------------------------|-----------------------|
| `author`                     | `author`              |
| `body`                       | `created_utc`         |
| `created_utc`                | `is_self`             |
| `is_submitter`               | `link_flair_text`     |
| `submission_author`          | `nsfw`                |
| `submission_created_utc`     | `selftext`            |
| `submission_link_flair_text` | `spoiler`             |
| `submission_nsfw`            | `stickied`            |
| `submission_num_comments`    | `title`               |
| `submission_score`           | `url`                 |
| `submission_title`           |                       |
| `submission_upvote_ratio`    |                       |
| `submission_url`             |                       |

Comment and submission attributes that are written to file will include the full list of attributes found in the [Table of All Subreddit, Redditor, and Submission Comments Attributes](#a-table-of-all-subreddit-redditor-and-submission-comments-attributes).

### Available Flags

```
[-lr <subreddit>]
[-lu <redditor>]

    [--nosave]
    [--stream-submissions]
```

---

### Livestreaming Subreddits

![Livestream Subreddit Demo GIF][Livestream Subreddit Demo]

\*This GIF has been cut for demonstration purposes.

**Usage:** `$ ./Urs.py -lr SUBREDDIT`

**Supported export formats:** JSON.

**Default stream objects:** Comments. To stream submissions instead, include the `--stream-submissions` flag.

You can livestream comments or submissions that are created within a Subreddit.

Reddit object information will be displayed in a [PrettyTable][PrettyTable] as they are submitted. 

> ***NOTE:*** PRAW may not be able to catch all new submissions or comments within a high-volume Subreddit, as mentioned in [these disclaimers located in the "Note" boxes][Subreddit Stream Disclaimer]. 

---

### Livestreaming Redditors

*Livestream demo was not recorded for Redditors because its functionality is identical to the Subreddit livestream.*

**Usage:** `$ ./Urs.py -lu REDDITOR` 

**Supported export formats:** JSON.

**Default stream objects:** Comments. To stream submissions instead, include the `--stream-submissions` flag.

You can livestream comments or submissions that are created by a Redditor.

Reddit object information will be displayed in a PrettyTable as they are submitted.

---

### Do Not Save Livestream to File

Include the `--nosave` flag if you do not want to save the livestream to file.

## Analytical Tools

This suite of tools can be used *after* scraping data from Reddit. Both of these tools analyze the frequencies of words found in submission titles and bodies, or comments within JSON scrape data.

There are a few ways you can quickly get the correct filepath to the scrape file:

* Drag and drop the file into the terminal. 
* Partially type the path and rely on tab completion support to finish the full path for you.

Running either tool will create the `analytics` directory within the date directory. **This directory is located in the same directory in which the scrape data resides**. For example, if you run the frequencies generator on February 16th for scrape data that was captured on February 14th, `analytics` will be created in the February 14th directory. Command history will still be written in the February 16th `urs.log`.

The sub-directories `frequencies` or `wordclouds` are created in `analytics` depending on which tool is run. These directories mirror the directories in which the original scrape files reside. For example, if you run the frequencies generator on a Subreddit scrape, the directory structure will look like this:

```
analytics/
└── frequencies
    └── subreddits
        └── SUBREDDIT_SCRAPE.json
```

A shortened export path is displayed once URS has completed exporting the data, informing you where the file is saved within the `scrapes` directory. You can open `urs.log` to view the full path.

### Target Fields

The data varies depending on the scraper, so these tools target different fields for each type of scrape data:

| Scrape Data         | Targets                           |
|---------------------|-----------------------------------|
| Subreddit           | `selftext`, `title`               |
| Redditor            | `selftext`, `title`, `body`       |
| Submission Comments | `body`                            |
| Livestream          | `selftext` and `title`, or `body` |

For Subreddit scrapes, data is pulled from the `selftext` and `title` fields for each submission (submission title and body).

For Redditor scrapes, data is pulled from all three fields because both submission and comment data is returned. The `title` and `body` fields are targeted for submissions, and the `selftext` field is targeted for comments.

For submission comments scrapes, data is only pulled from the `body` field of each comment.

For livestream scrapes, comments or submissions may be included depending on user settings. The `selftext` and `title` fields are targeted for submissions, and the `body` field is targeted for comments.

### File Names

File names are identical to the original scrape data so that it is easier to distinguish which analytical file corresponds to which scrape.

### Available Flags

```
[-f <file_path>]
    [--csv]
[-wc <file_path> [<optional_export_format>]]
    [--nosave]
```

---

### Generating Word Frequencies

![Frequencies Demo GIF][Frequencies Demo]

\*This GIF is uncut.

**Usage:** `$ ./Urs.py -f FILE_PATH` 

**Supported export formats:** JSON and CSV. To export to CSV, include the `--csv` flag.

You can generate a dictionary of word frequencies created from the words within the target fields. These frequencies are sorted from highest to lowest.

Frequencies export to JSON by default, but this tool also works well in CSV format.

Exported files will be saved to the `analytics/frequencies` directory.

---

### Generating Wordclouds

![Wordcloud Demo GIF][Wordcloud Demo]

\*This GIF is uncut.

**Usage:** `$ ./Urs.py -wc FILE_PATH`

**Supported export formats:** eps, jpeg, jpg, pdf, png (default), ps, rgba, tif, tiff.

Taking word frequencies to the next level, you can generate wordclouds based on word frequencies. This tool is independent of the frequencies generator - you do not need to run the frequencies generator before creating a wordcloud. 

PNG is the default format, but you can also export to any of the options listed above by including the format as the second flag argument.

**Usage:** `$ ./Urs.py -wc FILE_PATH OPTIONAL_EXPORT_FORMAT` 

Exported files will be saved to the `analytics/wordclouds` directory.

### Display Wordcloud Instead of Saving

Wordclouds are saved to file by default. If you do not want to keep a file, include the `--nosave` flag to only display the wordcloud.

## Utilities

This section briefly outlines the utilities included with URS.

### Available Flags

```
[-t [<optional_date>]]
[--check]
```

---

### Display Directory Tree

![Display Directory Tree Demo GIF][Display Directory Tree Demo]

**Usage:** `$ ./Urs.py -t`

If no date is provided, you can quickly view the directory structure for the current date. This is a quick alternative to the [`tree`][tree] command.

You can also display a different day's scrapes by providing a date after the `-t` flag. 

**Usage:** `$ ./Urs.py -t OPTIONAL_DATE`

The following date formats are supported:

* `MM-DD-YYYY`
* `MM/DD/YYYY`

An error is displayed if URS was not run on the entered date (if the date directory is not found within the `scrapes` directory).

### Check PRAW Rate Limits

![Check PRAW Rate Limits Demo GIF][Check PRAW Rate Limits Demo]

**Usage:** `$ ./Urs.py --check`

You can quickly check the rate limits for your account by using this flag. 

# Sponsors

This is a shout-out section for my patrons - thank you so much for sponsoring this project!

* [lolfilmworks][lolfilmworks]

# Contributing

**See the [Contact](#contact) section for ways to reach me.**

## Before Making Pull or Feature Requests

Consider the scope of this project before submitting a pull or feature request. URS stands for Universal Reddit Scraper. Two important aspects are listed in its name - *universal* and *scraper*.

I will not approve feature or pull requests that deviate from its sole purpose. This may include scraping a specific aspect of Reddit or [adding functionality that allows you to post a comment with URS][Commenting Feature Request]. Adding either of these requests will no longer allow URS to be universal or merely a scraper. However, I am more than happy to approve requests that enhance the current scraping capabilities of URS.

## Building on Top of URS

Although I will not approve requests that deviate from the project scope, feel free to reach out if you have built something on top of URS or have made modifications to scrape something specific on Reddit. I will add your project to the [Derivative Projects](#derivative-projects) section!

## Making Pull or Feature Requests

You can suggest new features or changes by going to the [Issues tab][Issues] and fill out the Feature Request template. If there is a good reason for a new feature, I will consider adding it.

You are also more than welcome to create a pull request - adding additional features, improving runtime, or refactoring existing code. If it is approved, I will merge the pull request into the master branch and credit you for contributing to this project.

# Contributors

| Date           | User                                                      | Contribution                                                                                                               |
|----------------|-----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| March 11, 2020 | [ThereGoesMySanity][ThereGoesMySanity] | Created a [pull request][ThereGoesMySanity Pull Request] adding 2FA information to README |
| October 6, 2020 | [LukeDSchenk][LukeDSchenk] | Created a [pull request][LukeDSchenk Pull Request] fixing "[Errno 36] File name too long" issue, making it impossible to save comment scrapes with long titles |
| October 10, 2020 | [IceBerge421][IceBerge421] | Created a [pull request][IceGerge421 Pull Request] fixing a cloning error occuring on Windows machines due to illegal file name characters, `"`, found in two scrape samples |

# Derivative Projects

This is a showcase for projects that are built on top of URS!

## [skiwheelr/URS][skiwheelr Project Link]

Contains a bash script built on URS which counts ticker mentions in Subreddits, subsequently cURLs all the relevant links in parallel, and counts the mentions of those.

![skiwheelr screenshot][skiwheelr screenshot]

<!-- BADGES: Links for the badges at the top of the README -->
[Codecov]: https://codecov.io/gh/JosephLai241/URS
[PRAW]: https://pypi.org/project/praw/
[Releases]: https://github.com/JosephLai241/URS/releases
[Say Thanks!]: https://saythanks.io/to/jlai24142%40gmail.com
<!-- [Travis CI Build Status]: https://travis-ci.com/github/JosephLai241/URS -->
[GitHub Workflow Status]: https://github.com/JosephLai241/URS/actions/workflows/pytest.yml
[URS Project Email]: mailto:urs_project@protonmail.

<!-- PRAW LINKS -->
[Subreddit Stream Disclaimer]: https://praw.readthedocs.io/en/latest/code_overview/other/subredditstream.html#praw.models.reddit.subreddit.SubredditStream

<!-- PRAW SCRAPER DEMO GIFS -->
[Subreddit Demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/Subreddit_demo.gif
[Redditor Demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/Redditor_demo.gif
[Submission Comments Demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/submission_comments_demo.gif

<!-- PRAW LIVESTREAM DEMO GIFS -->
[Livestream Subreddit Demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/live_scrapers/livestream_subreddit_demo.gif

<!-- ANALYTICAL TOOLS DEMO GIFS -->
[Frequencies Demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/analytical_tools/frequencies_generator_demo.gif
[Wordcloud Demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/analytical_tools/wordcloud_generator_demo.gif

<!-- UTILITIES DEMO GIFS -->
[Display Directory Tree Demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/utilities/tree_demo.gif
[Check PRAW Rate Limits Demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/utilities/check_rate_limit_demo.gif

<!-- GITHUB LINKS: Links around the URS repo on GitHub -->
[Issues]: https://github.com/JosephLai241/URS/issues
[Commenting Feature Request]: https://github.com/JosephLai241/URS/issues/17

<!-- SEPARATE DOCS: Links to documents located in the docs/ directory -->
[2-Factor Authentication]: https://github.com/JosephLai241/URS/blob/master/docs/Two-Factor%20Authentication.md
[Error Messages]: https://github.com/JosephLai241/URS/blob/master/docs/Error%20Messages.md
[How to get Reddit API Credentials for PRAW]: https://github.com/JosephLai241/URS/blob/master/docs/How%20to%20Get%20PRAW%20Credentials.md
[Releases/Changelog]: https://github.com/JosephLai241/URS/blob/master/docs/Releases.md
[Some Linux Tips]: https://github.com/JosephLai241/URS/blob/master/docs/Some%20Linux%20Tips.md
[The Forest]: https://github.com/JosephLai241/URS/blob/master/docs/The%20Forest.md

<!-- SAMPLES: Links to the samples directory -->
[Samples]: https://github.com/JosephLai241/URS/tree/samples

<!-- SPONSORS: Links to sponsors -->
[lolfilmworks]: https://github.com/lolfilmworks

<!-- CONTRIBUTORS LINKS: Links to contributor profile and pull request -->
<!-- ThereGoesMySanity: Links for user ThereGoesMySanity and pull request -->
[ThereGoesMySanity]: https://github.com/ThereGoesMySanity
[ThereGoesMySanity Pull Request]: https://github.com/JosephLai241/URS/pull/9
<!-- LukeDSchenk: Links for user LukeDSchenk and pull request -->
[LukeDSchenk]: https://github.com/LukeDSchenk
[LukeDSchenk Pull Request]: https://github.com/JosephLai241/URS/pull/19
<!-- IceBerge421: Links for user IceBerge421 and pull request -->
[IceBerge421]: https://github.com/IceBerge421
[IceGerge421 Pull Request]: https://github.com/JosephLai241/URS/pull/20

<!-- DERIVATIVE PROJECTS LINKS: Links to projects that were built on top of URS -->
[skiwheelr Project Link]: https://github.com/skiwheelr/URS
[skiwheelr screenshot]: https://i.imgur.com/ChHdAZv.png

<!-- ADDITIONAL LINKS: A space for useful links -->
[Export PYTHONPATH Help]: https://bic-berkeley.github.io/psych-214-fall-2016/using_pythonpath.html#setting-pythonpath-more-permanently
[tree]: http://mama.indstate.edu/users/ice/tree
[Depth-First Search]: https://www.interviewcake.com/concept/java/dfs
[PrettyTable]: https://pypi.org/project/prettytable/
