     __  __  _ __   ____  
    /\ \/\ \/\`'__\/',__\ 
    \ \ \_\ \ \ \//\__, `\
     \ \____/\ \_\\/\____/
      \/___/  \/_/ \/___/... Universal Reddit Scraper 

![GitHub top language](https://img.shields.io/github/languages/top/JosephLai241/URS?style=for-the-badge&logo=Python&logoColor=white)
[![PRAW Version](https://img.shields.io/badge/PRAW-7.0.0-red?style=for-the-badge&logo=reddit&logoColor=white)][PRAW]
[![Build Status](https://img.shields.io/travis/JosephLai241/URS?style=for-the-badge&logo=travis-ci&logoColor=white)][Travis CI Build Status]
[![Codecov](https://img.shields.io/codecov/c/gh/JosephLai241/URS?logo=codecov&logoColor=white&style=for-the-badge)][Codecov]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/JosephLai241/URS?style=for-the-badge)][Releases]
![License](https://img.shields.io/github/license/JosephLai241/URS?style=for-the-badge)
[![Email](https://img.shields.io/badge/Email-urs__project%40protonmail.com-informational?style=for-the-badge&logo=ProtonMail&logoColor=white)][URS Project Email]
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-blue?style=for-the-badge)][Say Thanks!]

<p align="center"> 
    <img src="https://github.com/JosephLai241/URS/blob/master/.github/Screenshots/Demo%20GIFs/DEMO.gif">
</p>

## Table of Contents

* [Introduction](#introduction)
* [Contributing](#contributing)
* [URS Overview](#urs-overview)
    + [Getting Started](#getting-started)
    + [Table of All Subreddit, Redditor, and Submission Comments Attributes](#a-table-of-all-subreddit-redditor-and-submission-comments-attributes)
    + [Subreddits](#subreddits)
    + [Redditors](#redditors)
    + [Submission Comments](#submission-comments)
    + [Exporting](#exporting)
* [Some Linux Tips](#some-linux-tips)
* [Contributors](#contributors)
* [Releases](#releases)
* Supplemental Documents
    + [How to get Reddit API Credentials for PRAW][How to get Reddit API Credentials for PRAW]
    + [Error Messages and Rate Limit Information][Error Messages and Rate Limit Info]
    + [2-Factor Authentication][2-Factor Authentication]

# Introduction

This is a universal Reddit scraper that can scrape Subreddits, Redditors, and comments from submissions. 

Written in Python and utilizes the official Reddit API ([ `PRAW` ][PRAW]).

Run `pip install -r requirements.txt` to get all project dependencies. 

You will need your own Reddit account and API credentials for PRAW. See the [Getting Started](#getting-started) section for more information. 

***NOTE:*** `PRAW` is currently supported on Python 3.5+. This project was tested with Python 3.8.2. 

**Whether you are using URS for enterprise or personal use, I am very interested in hearing about your use cases and how it has helped you achieve a goal. Please send me an email or leave a note by clicking on the Email or Say Thanks! badge. I look forward to hearing from you!**

# Contributing

I am currently looking for contributors who have experience with:

* Unit testing using `pytest`
* Packaging Python projects and deploying to PyPI
* Deploying documentation to ReadTheDocs

If you are interested in contributing, please send me an email at the address listed in the email badge!

___

Version 3.0.0 is most likely the last major iteration of URS, but I will continue to build upon it as I learn more about computer science.

You can suggest new features or changes by going to the Issues tab and filling out the Feature Request template. If there are good suggestions and a good reason for adding a feature, I will consider adding it.

You are also more than welcome to create a pull request, adding additional features, improving runtime, or streamlining existing code. If the pull request is approved, I will merge the pull request into the master branch and credit you for contributing to this project.

Make sure you follow the contributing guidelines when creating a pull request. See the [Contributing][Contributing Guide] document for more information. 

# URS Overview

Scrape speeds may vary depending on the number of results returned for Subreddit or Redditor scraping, or the submission's popularity (total number of comments) for submission comments scraping. It is also impacted by your internet connection speed. 

All exported files are saved within the `scrapes/` directory and stored in a sub-directory labeled with the date. These directories are automatically created when you run URS. 

## Getting Started

Refer to [my guide][How to get Reddit API Credentials for PRAW] to get Reddit API credentials, then update the `API` dictionary located in `Credentials.py`

## A Table of All Subreddit, Redditor, and Submission Comments Attributes

These attributes are included in each scrape. 

| Subreddits    | Redditors                      | Submission Comments |
|---------------|--------------------------------|---------------------|
| Title         | Name                           | Parent ID           |
| Flair         | Fullname                       | Comment ID          |
| Date Created  | ID                             | Author              |
| Upvotes       | Date Created                   | Date Created        |
| Upvote Ratio  | Comment Karma                  | Upvotes             |
| ID            | Link Karma                     | Text                |
| Is Locked?    | Is Employee?                   | Edited?             |
| NSFW?         | Is Friend?                     | Is Submitter?       |
| Is Spoiler?   | Is Mod?                        | Stickied?           |
| Stickied?     | Is Gold?                       |                     |
| URL           | \*Submissions                  |                     |
| Comment Count | \*Comments                     |                     |
| Text          | \*Hot                          |                     |
| &nbsp;        | \*New                          |                     |
| &nbsp;        | \*Controversial                |                     |
| &nbsp;        | \*Top                          |                     |
| &nbsp;        | \*Upvoted (may be forbidden)   |                     |
| &nbsp;        | \*Downvoted (may be forbidden) |                     |
| &nbsp;        | \*Gilded                       |                     |
| &nbsp;        | \*Gildings (may be forbidden)  |                     |
| &nbsp;        | \*Hidden (may be forbidden)    |                     |
| &nbsp;        | \*Saved (may be forbidden)     |                     |

\*Includes additional attributes; see [Redditors](#redditors) section for more information. 

## Subreddits

![Subreddit Demo GIF][Subreddit Demo]

\* This GIF is uncut.

`$ ./Urs.py -r SUBREDDIT [H|N|C|T|R|S] N_RESULTS_OR_KEYWORDS --FILE_FORMAT` 

You can specify Subreddits, the submission category, and how many results are returned from each scrape. I have also added a search option where you can search for keyword(s) within a Subreddit and URS will get all submissions that are returned from the search.

Some categories include additional time filters. Here is a table of how each is sorted.

| Category      | Sorted By/Time Filter | 
|---------------|-----------------------|
| Controversial | Time filter: All      |
| Search        | Sorted by: Relevance  |
| Top           | Time filter: All      |

These are the submission categories:

* Hot
* New
* Controversial
* Top
* Rising
* Search

***NOTE:*** All results are returned if you search for something within a Subreddit. You will not be able to specify how many results to keep. 

The file names will follow this format: `"r-[SUBREDDIT]-[POST_CATEGORY]-[N_RESULTS]-result(s).[FILE_FORMAT]"` 

If you searched for keywords, file names are formatted as such: `"r-[SUBREDDIT]-Search-'[KEYWORDS]'.[FILE_FORMAT]"` 

## Redditors

![Redditor Demo GIF][Redditor Demo]

\* This GIF has been cut for demonstration purposes.

`$ ./Urs.py -u USER N_RESULTS --FILE_FORMAT` 

**Designed for JSON only.**

You can also scrape Redditor profiles and specify how many results are returned.

Some Redditor attributes are sorted differently. Here is a table of how each is sorted.

| Attribute Name | Sorted By/Time Filter                       |
|----------------|---------------------------------------------|
| Comments       | Sorted by: New                              |
| Controversial  | Time filter: All                            |
| Gilded         | Sorted by: New                              |
| Hot            | Determined by other Redditors' interactions |
| New            | Sorted by: New                              |
| Submissions    | Sorted by: New                              |
| Top            | Time filter: All                            |

Of these Redditor attributes, the following will include additional attributes:

| Submissions, Hot, New, Controversial, Top, Upvoted, Downvoted, Gilded, Gildings, Hidden, and Saved | Comments                                     |
|----------------------------------------------------------------------------------------------------|----------------------------------------------|
| Title                                                                                              | Date Created                                 |
| Date Created                                                                                       | Score                                        |
| Upvotes                                                                                            | Text                                         |
| Upvote Ratio                                                                                       | Parent ID                                    |
| ID                                                                                                 | Link ID                                      |
| NSFW?                                                                                              | Edited?                                      |
| Text                                                                                               | Stickied?                                    |
| &nbsp;                                                                                             | Replying to (title of submission or comment) |
| &nbsp;                                                                                             | In Subreddit (Subreddit name)                |

***NOTE:*** If you are not allowed to access a Redditor's lists, PRAW will raise a 403 HTTP Forbidden exception and the program will just append a "FORBIDDEN" underneath that section in the exported file. 

***NOTE:*** The number of results returned are applied to all attributes. I have not implemented code to allow users to specify different number of results returned for individual attributes. 

The file names will follow this format: `"u-[USERNAME]-[N_RESULTS]-result(s).[FILE_FORMAT]"` 

## Submission Comments

![Structured Comments Demo GIF][Structured Comments Demo]
![Raw Comments Demo GIF][Raw Comments Demo]

\* These GIFs have been cut for demonstration purposes.

`$ ./Urs.py -c URL N_RESULTS --FILE_FORMAT` 

**Designed for JSON only.**

You can also scrape comments from submissions and specify the number of results returned. 

Comments are sorted by "Best", which is the default sorting option when you visit a submission.

There are two ways you can scrape comments: structured or raw. This is determined by the number you pass into `N_RESULTS`:

| Scrape Type | N_RESULTS      |
|-------------|----------------|
| Structured  | N_RESULTS >= 1 |
| Raw         | N_RESULTS = 0  |

Structured scrapes resemble comment threads on Reddit and will include down to third-level comment replies. 

Raw scrapes do not resemble comment threads, but returns all comments on a submission in level order: all top-level comments are listed first, followed by all second-level comments, then third, etc.

Of all scrapers included in this program, this usually takes the longest to execute. PRAW returns submission comments in level order, which means scrape speeds are proportional to the submission's popularity.

***NOTE:*** You cannot specify the number of raw comments returned. The program with scrape all comments from the submission. 

The file names will follow this format: `"c-[POST_TITLE]-[N_RESULTS]-result(s).[FILE_FORMAT]"` 

## Exporting

URS supports exporting to either CSV or JSON.

Here are my recommendations for scrape exports.

| Scraper         | File Format |
|-----------------|-------------|
| Subreddit/Basic | CSV or JSON |
| Redditor        | JSON        |
| Comments        | JSON        |

Subreddit scrapes will work well with either format.

JSON is the more practical option for Redditor and submission comments scraping, which is why I have designed these scrapers to work best in this format. 

It is much easier to read the scrape results since Redditor scraping returns attributes that include additional submission or comment attributes. 

Comments scraping is especially easier to read because structured exports look similar to threads on Reddit. You can process all the information pertaining to a comment much quicker compared to CSV. 

You can still export Redditor data and submission comments to CSV, but you will be disappointed with the results.

### See the [samples][Samples] for scrapes ran on June 14, 2020.

# Some Linux Tips

* You can further simplify running the program by making the program executable: `sudo chmod +x Urs.py` 
* Make sure the shebang at the top of `Urs.py` matches the location in which your Python3 is installed. You can use `which python` and then `python --version` to check. The default shebang is `#!/usr/bin/python`. 
* Now you will only have to prepend `./` to run URS. 
  + `./Urs.py ...` 
* Troubleshooting
  + You will have to set the fileformat to UNIX if you run URS with `./` and are greeted with a bad interpreter error. I did this using Vim. 

	``` 
    $ vim Urs.py
    :set fileformat=unix
    :wq!
    ```

# Contributors

| Date           | User                                                      | Contribution                                                                                                               |
|----------------|-----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| March 11, 2020 | [ThereGoesMySanity][ThereGoesMySanity] | Created a [pull request][ThereGoesMySanity Pull Request] adding 2FA information to Readme |

# Releases

| Release Date | Version | Changelog | 
|--------------|---------|-----------|
| **May 25, 2019** | URS v1.0 | <ul> <li>Its inception.</li> </ul> |
| **July 29, 2019** | URS v2.0 | <ul> <li>Now **includes CLI support**!</li> </ul> |
| **December 28, 2019** | URS v3.0 (beta) | <ul> <li>Added **JSON** export.</li> <li>Added **Redditor Scraping**.</li> <li>Comments scraping is still under construction.</li> </ul> | 
| **December 31, 2019** | URS v3.0 (Official) | <ul> <li>**Comments scraping is now working**!</li> <li>**Added additional exception handling** for creating filenames.</li> <li>Minor code reformatting.</li> <li>**Simplified verbose output**.</li> <li>**Added an additional submission attribute** when scraping Redditors.</li> <li>Happy New Year!</li> </ul> |
| **January 15, 2020** | URS v3.0 (Final Release) | <ul> <li>Numerous changes to Readme.</li> <li>Minor code reformatting.</li> <li>**Fulfilled community standards** by adding the following docs:</li> <ul> <li>[Contributing Guide][Contributing Guide]</li> <li>[Pull Request Template][Pull Request Template]</li> <li>Issue templates:</li> <ul> <li>[Bug Report][Bug Report]</li> <li>[Feature Request][Feature Request]</li> </ul> <li>[Code of Conduct][Code of Conduct]</li> <li>[License][License]</li> </ul> </ul> |
| **June 21, 2020** | URS v3.1.0 | <ul> <li>***Major*** code refactor. **Applied OOP concepts** to existing code and rewrote methods in attempt to **improve readability, maintenance, and scalability**.</li> <li>**New in 3.1.0**:</li> <ul> <li>**Scrapes will now be exported to the `scrapes/` directory** within a subdirectory corresponding to the date of the scrape. These directories are automatically created for you when you run URS.</li> <li>Added **log decorators** that record what is happening during each scrape, which scrapes were ran, and any errors that might arise during runtime in the log file `scrapes.log`. The log is stored in the same subdirectory corresponding to the date of the scrape.</li> <li>**Replaced bulky titles with minimalist titles** for a cleaner look.</li> <li>**Added color to terminal output**.</li> </ul> <li>**Improved naming convention** for scripts.</li> <li>Integrating **Travis CI** and **Codecov**.</li> <li>Updated community documents located in the `.github/` directory: `BUG_REPORT`, `CONTRIBUTING`, `FEATURE_REQUEST`, `PULL_REQUEST_TEMPLATE`, and `STYLE_GUIDE`</li> <li>Numerous changes to Readme. The most significant change was **splitting and storing walkthroughs in `docs/`**.</li> </ul> | 

<!-- BADGES: Links for the badges at the top of the README -->
[Codecov]: https://codecov.io/gh/JosephLai241/URS
[PRAW]: https://pypi.org/project/praw/
[Releases]: https://github.com/JosephLai241/URS/releases
[Say Thanks!]: https://saythanks.io/to/jlai24142%40gmail.com
[Travis CI Build Status]: https://travis-ci.org/github/JosephLai241/URS
[URS Project Email]: mailto:urs_project@protonmail.

<!-- DEMO GIFS: Links to demo GIFS -->
[Main Demo]: https://github.com/JosephLai241/URS/blob/master/.github/Screenshots/Demo%20GIFs/DEMO.gif
[Subreddit Demo]: https://github.com/JosephLai241/URS/blob/master/.github/Screenshots/Demo%20GIFs/Subreddit_demo.gif
[Redditor Demo]: https://github.com/JosephLai241/URS/blob/master/.github/Screenshots/Demo%20GIFs/Redditor_demo.gif
[Structured Comments Demo]: https://github.com/JosephLai241/URS/blob/master/.github/Screenshots/Demo%20GIFs/Comments_structured_demo.gif
[Raw Comments Demo]: https://github.com/JosephLai241/URS/blob/master/.github/Screenshots/Demo%20GIFs/Comments_raw_demo.gif

<!-- SEPARATE DOCS: Links to documents located in the docs/ directory -->
[2-Factor Authentication]: https://github.com/JosephLai241/URS/blob/master/docs/Two-Factor%20Authentication.md
[Error Messages and Rate Limit Info]: https://github.com/JosephLai241/URS/blob/master/docs/Error%20Messages.md
[How to get Reddit API Credentials for PRAW]: https://github.com/JosephLai241/URS/blob/master/docs/How%20to%20Get%20PRAW%20Credentials.md

<!-- SAMPLES: Links to the samples directory -->
[Samples]: https://github.com/JosephLai241/URS/tree/master/samples/scrapes/06-14-2020

<!-- COMMUNITY DOCS: Links to the community docs -->
[Bug Report]: https://github.com/JosephLai241/URS/blob/master/.github/ISSUE_TEMPLATE/BUG_REPORT.md
[Code of Conduct]: https://github.com/JosephLai241/URS/blob/master/.github/CODE_OF_CONDUCT.md
[Contributing Guide]: https://github.com/JosephLai241/URS/blob/master/.github/CONTRIBUTING.md
[Feature Request]: https://github.com/JosephLai241/URS/blob/master/.github/ISSUE_TEMPLATE/FEATURE_REQUEST.md
[License]: https://github.com/JosephLai241/URS/blob/master/LICENSE
[Pull Request Template]: https://github.com/JosephLai241/URS/blob/master/.github/PULL_REQUEST_TEMPLATE.md

<!-- ThereGoesMySanity: Links for user ThereGoesMySanity's account and pull request -->
[ThereGoesMySanity]: https://github.com/ThereGoesMySanity
[ThereGoesMySanity Pull Request]: https://github.com/JosephLai241/URS/pull/9
