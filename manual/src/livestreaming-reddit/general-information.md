# Livestreaming Reddit via PRAW

These tools may be used to livestream comments or submissions submitted within Subreddits or by Redditors.

**Comments are streamed by default**. To stream submissions instead, include the `--stream-submissions` flag.

**New comments or submissions will continue to display within your terminal until you abort the stream using `Ctrl + C`**.

## File Naming Conventions

The filenames will follow this format:

```
[SUBREDDIT_OR_REDDITOR]-[comments_OR_submissions]-[START_TIME_IN_HOURS_MINUTES_SECONDS]-[DURATION_IN_HOURS_MINUTES_SECONDS].json
```

This file is saved in the main `livestream` directory into the `subreddits` or `redditors` directory depending on which stream was run.

Reddit objects will be written to this JSON file in real time. After aborting the stream, the filename will be updated with the start time and duration.

## Displayed vs. Saved Attributes

Displayed comment and submission attributes have been stripped down to essential fields to declutter the output. Here is a table of what is shown during the stream:

| Comment Attributes           | Submission Attributes |
| ---------------------------- | --------------------- |
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

Comment and submission attributes that are written to file will include the full list of attributes found in the [Table of All Subreddit, Redditor, and Submission Comments Attributes](../scraping-reddit/all-attributes-table.md).
