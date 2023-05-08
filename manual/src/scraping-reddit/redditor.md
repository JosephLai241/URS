# Table of Contents

- [Redditors](#redditors)
  - [All Flags](#all-flags)
  - [Usage](#usage)
  - [Redditor Interaction Attributes](#redditor-interaction-attributes)
  - [Reddit Object Attributes](#reddit-object-attributes)
  - [File Naming Conventions](#file-naming-conventions)

# Redditors

![Redditor Demo GIF][redditor demo]

\*_This GIF has been cut for demonstration purposes._

> **_NOTE:_** If you are not allowed to access a Redditor's lists, PRAW will raise a 403 HTTP Forbidden exception and the program will just append `"FORBIDDEN"` underneath that section in the exported file.

## All Flags

These are all the flags that may be used when scraping Redditors.

```
[-u <redditor> <n_results>]
```

> **_NOTE:_** The number of results returned are applied to all attributes. I have not implemented code to allow users to specify different number of results returned for individual attributes.

## Usage

```
poetry run Urs.py -u <redditor> <n_results>
```

Redditor information will be included in the `information` field and includes the following attributes:

- `comment_karma`
- `created_utc`
- `fullname`
- `has_verified_email`
- `icon_img`
- `id`
- `is_employee`
- `is_friend`
- `is_mod`
- `is_gold`
- `link_karma`
- `name`
- `subreddit`
- `trophies`

## Redditor Interaction Attributes

Redditor interactions will be included in the `interactions` field. Here is a table of all Redditor interaction attributes that are also included, how they are sorted, and what type of Reddit objects are included in each.

| Attribute Name | Sorted By/Time Filter                       | Reddit Objects           |
| -------------- | ------------------------------------------- | ------------------------ |
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

## Reddit Object Attributes

This is a table of all attributes that are included for each Reddit object:

| Subreddits              | Comments        | Submissions           | Multireddits       | Trophies      |
| ----------------------- | --------------- | --------------------- | ------------------ | ------------- |
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
| `subscribers`           | \*`submission`  | `nsfw`                |                    |               |
| `user_is_banned`        | `subreddit_id`  | `permalink`           |                    |               |
| `user_is_moderator`     |                 | `score`               |                    |               |
| `user_is_subscriber`    |                 | `selftext`            |                    |               |
|                         |                 | `spoiler`             |                    |               |
|                         |                 | `stickied`            |                    |               |
|                         |                 | \*`subreddit`         |                    |               |
|                         |                 | `title`               |                    |               |
|                         |                 | `upvote_ratio`        |                    |               |
|                         |                 | `url`                 |                    |               |

\* Contains additional metadata.

## File Naming Conventions

The file names will follow this format:

```
[USERNAME]-[N_RESULTS]-result(s).json
```

Scrape data is exported to the `redditors` directory.

[redditor demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/praw_scrapers/static_scrapers/Redditor_demo.gif?raw=true
