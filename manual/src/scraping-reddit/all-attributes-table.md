# Subreddit, Redditor, and Submission Comments Attributes

These attributes are included in each scrape.

| Subreddits (submissions) | Redditors                        | Submission Comments |
| ------------------------ | -------------------------------- | ------------------- |
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

\*_Includes additional attributes; see the [Scraping Redditors](./redditor.md) section for more information._
