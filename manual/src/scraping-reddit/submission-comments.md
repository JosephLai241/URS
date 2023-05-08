# Table of Contents

- [Submission Comments](#submission-comments)
  - [All Flags](#all-flags)
  - [Usage](#usage)
  - [File Naming Conventions](#file-naming-conventions)
  - [Number of Comments Returned](#number-of-comments-returned)
  - [Structured Comments](#structured-comments)
  - [Raw Comments](#raw-comments)

# Submission Comments

![Submission Comments Demo GIF][submission comments demo]

\*_This GIF has been cut for demonstration purposes._

## All Flags

These are all the flags that may be used when scraping submission comments.

```
[-c <submission_url> <n_results>]
    [--raw]
```

## Usage

```
poetry run Urs.py -c <submission_url> <n_results>
```

Submission metadata will be included in the `submission_metadata` field and includes the following attributes:

- `author`
- `created_utc`
- `distinguished`
- `edited`
- `is_original_content`
- `is_self`
- `link_flair_text`
- `locked`
- `nsfw`
- `num_comments`
- `permalink`
- `score`
- `selftext`
- `spoiler`
- `stickied`
- `subreddit`
- `title`
- `upvote_ratio`

If the submission contains a gallery, the attributes `gallery_data` and `media_metadata` will be included.

Comments are written to the `comments` field. They are sorted by "Best", which is the default sorting option when you visit a submission.

PRAW returns submission comments in level order, which means scrape speeds are proportional to the submission's popularity.

## File Naming Conventions

The file names will generally follow this format:

```
[POST_TITLE]-[N_RESULTS]-result(s).json
```

Scrape data is exported to the `comments` directory.

## Number of Comments Returned

You can scrape all comments from a submission by passing in `0` for `<n_results>`. Subsequently, `[N_RESULTS]-result(s)` in the file name will be replaced with `all`.

Otherwise, specify the number of results you want returned. If you passed in a specific number of results, the structured export will return up to `<n_results>` top level comments and include all of its replies.

## Structured Comments

**This is the default export style.** Structured scrapes resemble comment threads on Reddit. This style takes just a little longer to export compared to the raw format because `URS` uses [depth-first search][depth-first search] to create the comment `Forest` after retrieving all comments from a submission.

If you want to learn more about how it works, refer to [The Forest](../implementation-details/the-forest.md), where I describe how I implemented the `Forest`, and [Speeding up Python With Rust](../implementation-details/speeding-up-python-with-rust.md) to learn about how I drastically improved the performance of the `Forest` by rewriting it in Rust.

## Raw Comments

Raw scrapes do not resemble comment threads, but returns all comments on a submission in level order: all top-level comments are listed first, followed by all second-level comments, then third, etc.

You can export to raw format by including the `--raw` flag. `-raw` will also be appended to the end of the file name.

[depth-first search]: https://www.interviewcake.com/concept/java/dfs
[submission comments demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/submission_comments_demo.gif?raw=true
