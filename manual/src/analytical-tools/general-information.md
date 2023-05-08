# Analytical Tools

This suite of tools can be used _after_ scraping data from Reddit. Both of these tools analyze the frequencies of words found in submission titles and bodies, or comments within JSON scrape data.

There are a few ways you can quickly get the correct filepath to the scrape file:

- Drag and drop the file into the terminal.
- Partially type the path and rely on tab completion support to finish the full path for you.

Running either tool will create the `analytics` directory within the date directory. **This directory is located in the same directory in which the scrape data resides**. For example, if you run the frequencies generator on February 16th for scrape data that was captured on February 14th, `analytics` will be created in the February 14th directory. Command history will still be written in the February 16th `urs.log`.

The sub-directories `frequencies` or `wordclouds` are created in `analytics` depending on which tool is run. These directories mirror the directories in which the original scrape files reside. For example, if you run the frequencies generator on a Subreddit scrape, the directory structure will look like this:

```
analytics/
└── frequencies
    └── subreddits
        └── SUBREDDIT_SCRAPE.json
```

A shortened export path is displayed once `URS` has completed exporting the data, informing you where the file is saved within the `scrapes` directory. You can open `urs.log` to view the full path.

# Target Fields

The data varies depending on the scraper, so these tools target different fields for each type of scrape data:

| Scrape Data         | Targets                           |
| ------------------- | --------------------------------- |
| Subreddit           | `selftext`, `title`               |
| Redditor            | `selftext`, `title`, `body`       |
| Submission Comments | `body`                            |
| Livestream          | `selftext` and `title`, or `body` |

For Subreddit scrapes, data is pulled from the `selftext` and `title` fields for each submission (submission title and body).

For Redditor scrapes, data is pulled from all three fields because both submission and comment data is returned. The `title` and `body` fields are targeted for submissions, and the `selftext` field is targeted for comments.

For submission comments scrapes, data is only pulled from the `body` field of each comment.

For livestream scrapes, comments or submissions may be included depending on user settings. The `selftext` and `title` fields are targeted for submissions, and the `body` field is targeted for comments.

# File Names

File names are identical to the original scrape data so that it is easier to distinguish which analytical file corresponds to which scrape.
