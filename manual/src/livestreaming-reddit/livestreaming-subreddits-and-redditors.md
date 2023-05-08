# Livestreaming Subreddits

![Livestream Subreddit Demo GIF][livestream subreddit demo]

\*_This GIF has been cut for demonstration purposes._

## All Flags

These are all the flags that may be used when livestreaming Subreddits.

```
[-lr <subreddit>]
    [--nosave]
    [--stream-submissions]
```

## Usage

```
poetry run Urs.py -lr <subreddit>
```

**Default stream objects:** Comments. To stream submissions instead, include the `--stream-submissions` flag.

You can livestream comments or submissions that are created within a Subreddit.

Reddit object information will be displayed in a [PrettyTable][prettytable] as they are submitted.

> **_NOTE:_** PRAW may not be able to catch all new submissions or comments within a high-volume Subreddit, as mentioned in [these disclaimers located in the "Note" boxes][subreddit stream disclaimer].

# Livestreaming Redditors

_Livestream demo was not recorded for Redditors because its functionality is identical to the Subreddit livestream._

## All Flags

These are all the flags that may be used when livestreaming Redditors.

```
[-lu <redditor>]
    [--nosave]
    [--stream-submissions]
```

## Usage

```
poetry run Urs.py -lu <redditor>
```

**Default stream objects:** Comments. To stream submissions instead, include the `--stream-submissions` flag.

You can livestream comments or submissions that are created by a Redditor.

Reddit object information will be displayed in a PrettyTable as they are submitted.

# Do Not Save Livestream to File

Include the `--nosave` flag if you do not want to save the livestream to file.

[livestream subreddit demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/live_scrapers/livestream_subreddit_demo.gif?raw=true
[prettytable]: https://pypi.org/project/prettytable/
[subreddit stream disclaimer]: https://praw.readthedocs.io/en/latest/code_overview/other/subredditstream.html#praw.models.reddit.subreddit.SubredditStream
