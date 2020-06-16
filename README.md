     __  __  _ __   ____  
    /\ \/\ \/\`'__\/',__\ 
    \ \ \_\ \ \ \//\__, `\
     \ \____/\ \_\\/\____/
      \/___/  \/_/ \/___/ 

![GitHub top language](https://img.shields.io/github/languages/top/JosephLai241/Universal-Reddit-Scraper?style=for-the-badge&logo=Python&logoColor=white)
[![Build Status](https://img.shields.io/travis/JosephLai241/Universal-Reddit-Scraper?style=for-the-badge&logo=travis-ci&logoColor=white)](https://travis-ci.org/JosephLai241/Universal-Reddit-Scraper)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/JosephLai241/Universal-Reddit-Scraper?style=for-the-badge)
![GitHub contributors](https://img.shields.io/github/contributors/JosephLai241/Universal-Reddit-Scraper?style=for-the-badge)
![License](https://img.shields.io/github/license/JosephLai241/Universal-Reddit-Scraper?style=for-the-badge)
[![Email](https://img.shields.io/badge/Email-urs__project%40protonmail.com-informational?style=for-the-badge&logo=ProtonMail&logoColor=white)](mailto:urs_project@protonmail.com)
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-blue?style=for-the-badge)](https://saythanks.io/to/jlai24142%40gmail.com)

## Table of Contents

* [Introduction](#introduction)
* [Information for URS v3.1.0b1 (Beta) Release](#information-for-urs-v3.1.0b1-Release)
* [URS v3.1.0 Official Release TODO list](#urs-v3.1.0-official-release-todo-list)
* [URS Overview](#urs-overview)
  + [Table of All Subreddit, Redditor, and Submission Comments Attributes](#a-table-of-all-subreddit-redditor-and-submission-comments-attributes)
  + [Subreddits](#subreddits)
  + [Redditors](#redditors)
  + [Submission Comments](#submission-comments)
  + [Exporting](#exporting)
* [How to get Reddit API Credentials for PRAW](#how-to-get-reddit-api-credentials-for-PRAW) UPDATE LINK IN DOCS/
* [In-Depth Walkthrough](#walkthrough) UPDATE LINK IN DOCS/
* [2-Factor Authentication](#2-factor-authentication) UPDATE LINK IN DOCS/
* [Some Linux Tips](#some-linux-tips)
* [Contributing](#contributing)
* [Contributors](#contributors)
* [Releases](#releases)

# Introduction

This is a universal Reddit scraper that can scrape Subreddits, Redditors, and comments from submissions. 

Written in Python and utilizes the official Reddit API ([ `PRAW` ](https://pypi.org/project/praw/)).

Run `pip install -r requirements.txt` to get all project dependencies. 

You will need your own Reddit account and API credentials for PRAW. I have included a tutorial on how to do this below. 

***NOTE:*** `PRAW` is currently supported on Python 3.5+. This project was tested with Python 3.8.2. 

## Information for URS v3.1.0b1 (Beta) Release

**The beta is merely missing unit tests for Travis CI and Codecov**. All other functionality detailed in the [Releases](#releases) section of the README have been implemented and tested without unit tests.

I will continue merging unit tests to `tests/` for however long it takes me to learn more about unit testing, continuous integration, and finish writing the tests. 

I think there are some aspects of URS that I will not be able to write unit tests for because it would be impractical, e.g., testing user validation would expose my personal PRAW credentials. I will not be writing a test for that function unless there is a way to test and push the code to Github without including my credentials. 

Please open a new issue with the `suggestion` label if you have any suggestions for getting around this issue or best unit testing practices. I will be using the `pytest` testing framework.

The TODO list below details what is missing and needs to be finished before the official v3.1.0 release.

## URS v3.1.0 Official Release TODO list

### Overview

* Finish unit tests
* Finish integrating Travis CI
* Update Codecov through Travis CI and add coverage badge
* Update docs
    * Update the following in README: 
        + Add demo GIF at the top of the README
        + Doc links in the ToC
    * Update screenshots in In-Depth Walkthrough
    * Review and update community docs
        + Update style guide
* Set up ReadTheDocs documentation
* Finish packaging URS
* Deploy URS to PyPI

### Details

* Continuous Integration and Coverage
    + Finish writing unit tests
    + Travis CI
        * ~~Sign up for Travis CI~~
        * ~~Add URS repo~~
        * ~~Add build badge to README~~'
        * ~~Create `.travis.yml` config file~~
            + Codecov integration
                * `before_install`
                    + `python --version`
                    + `pip install -U pip`
                    + `pip install -U pytest`
                    + `pip install codecov`
                * `install`
                    + Change script to `pip install ".[test]" .`? (install package and test dependencies)
                * `after_success`
                    + `codecov` (submit coverage)
    + Codecov
        * Sign up for Codecov
        * Add URS repo
        * Add coverage badge to README
* ReadTheDocs
    + ~~Sign up for ReadTheDocs~~
    + Learn how to generate docs (Sphinx or manual docs?)
    + Rewrite README in .rst?
    + Restructure `docs/` so that RTD can build my documentation
* Github Docs
    + Replace old screenshots in In-Depth Walkthrough
    + Add demo GIF under ASCII art title
    + Update links in ToC
    + Review and update community docs
        * Update style guide as well
* Finish packaging URS
    + `setup.py`
        * Change Development Status Classifier in `setup.py` once 3.1.0 is completed
        * Add `download_url` from the new tag (copy link address of tar.gz link)
        * Add `install_requires` to define all dependencies 
    + When everything is finalized, deploy to PyPI
        * ~~Sign up for PyPI~~
        * Complete `setup.py` and any other related documents/scripts for packaging
        * Create new API token
        * Install and upload URS with `twine`

**Whether you are using URS for enterprise or personal use, I am very interested in hearing about your use cases and how it has helped you achieve a goal. Please send me an email or leave a note by clicking on the Email or Say Thanks! badge. I look forward to hearing from you!**

# URS Overview

Scrape speeds may vary depending on the number of results returned for Subreddit or Redditor scraping, or the submission's popularity (total number of comments) for submission comments scraping. It is also impacted by your internet connection speed. 

All exported files are saved within the `scrapes/` directory and stored in a sub-directory labeled with the date. These directories are automatically created when you run URS. 

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

`$ ./Urs.py -r SUBREDDIT [H|N|C|T|R|S] N_RESULTS_OR_KEYWORDS --FILE_FORMAT` 

You can specify Subreddits, the submission category, and how many results are returned from each scrape. I have also added a search option where you can search for keyword(s) within a Subreddit and URS will get all submissions that are returned from the search.

Some categories include additional time filters. Here is a table of how each is sorted.

| Category      | Sorted By/Time Filter | 
|---------------|-----------------------|
| Controversial | Time filter: all      |
| Search        | Sorted by: Relevance  |
| Top           | Time filter: all      |

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

`$ ./Urs.py -u USER N_RESULTS --FILE_FORMAT` 

**Designed for JSON only. Exporting to CSV is not recommended, but it will still work.**

You can also scrape Redditor profiles and specify how many results are returned.

Some Redditor attributes are sorted differently. Here is a table of how each is sorted.

| Attribute Name | Sorted By/Time Filter                       |
|----------------|---------------------------------------------|
| Comments       | Sorted by: new                              |
| Controversial  | Time filter: all                            |
| Gilded         | Sorted by: new                              |
| Hot            | Determined by other Redditors' interactions |
| New            | Sorted by: new                              |
| Submissions    | Sorted by: new                              |
| Top            | Time filter: all                            |

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

`$ ./Urs.py -c URL N_RESULTS --FILE_FORMAT` 

**Designed for JSON only. Exporting to CSV is not recommended, but it will still work.**

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

### See [samples/]() for scrapes ran on June 14, 2020. UPDATE LINK TO SAMPLES/

### See [In-Depth Walkthrough]() for a more detailed guide with screenshots. UPDATE LINK TO DOCS/

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

# Contributing

I believe the current features should satisfy users who need to scrape Reddit; however, I will continue adding small features as I learn more about computer science.

You can suggest new features or changes by going to the Issues tab, creating a new issue, and tagging it as an enhancement. If there are good suggestions and a good reason for adding a feature, I will consider adding it. 

You are also more than welcome to create a pull request, adding additional features, improving runtime, or streamlining existing code. If the pull request is approved, I will merge the pull request into the master branch and credit you for contributing to this project.

Make sure you follow the contributing guidelines when creating a pull request. See the [Contributing](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/CONTRIBUTING.md) document for more information. 

# Contributors

| Date           | User                                                      | Contribution                                                                                                               |
|----------------|-----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| March 11, 2020 | [ThereGoesMySanity](https://github.com/ThereGoesMySanity) | Created a [pull request](https://github.com/JosephLai241/Universal-Reddit-Scraper/pull/9) adding 2FA information to Readme |

# Releases

| Release Date | Version | Changelog | 
|--------------|---------|-----------|
| **May 25, 2019** | URS v1.0 | <ul> <li>Its inception.</li> </ul> |
| **July 29, 2019** | URS v2.0 | <ul> <li>Now **includes CLI support**!</li> </ul> |
| **December 28, 2019** | URS v3.0 (beta) | <ul> <li>Added **JSON** export.</li> <li>Added **Redditor Scraping**.</li> <li>Comments scraping is still under construction.</li> </ul> | 
| **December 31, 2019** | URS v3.0 (Official) | <ul> <li>**Comments scraping is now working**!</li> <li>**Added additional exception handling** for creating filenames.</li> <li>Minor code reformatting.</li> <li>**Simplified verbose output**.</li> <li>**Added an additional submission attribute** when scraping Redditors.</li> <li>Happy New Year!</li> </ul> |
| **January 15, 2020** | URS v3.0 (Final Release) | <ul> <li>Numerous changes to Readme.</li> <li>Minor code reformatting.</li> <li>**Fulfilled community standards** by adding the following docs:</li> <ul> <li>[Contributing Guidelines](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/CONTRIBUTING.md)</li> <li>[Pull Request Template](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/PULL_REQUEST_TEMPLATE.md)</li> <li>Issue templates:</li> <ul> <li>[Bug Report](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/ISSUE_TEMPLATE/BUG_REPORT.md)</li> <li>[Feature Request](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/ISSUE_TEMPLATE/FEATURE_REQUEST.md)</li> </ul> <li>[Code of Conduct](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/CODE_OF_CONDUCT.md)</li> <li>[License](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/LICENSE)</li> </ul> </ul> |
| **TBD** | URS v3.1.0b1 (beta) | <ul> <li>***Major*** code refactor. **Applied OOP concepts** to existing code and rewrote methods in attempt to **improve readability, maintenance, and scalability**.</li> <li>**Scrapes will now be exported to the `scrapes/` directory** within a subdirectory corresponding to the date of the scrape. These directories are automatically created for you when you run URS.</li> <li>Added **log decorators** that record what is happening during each scrape, which scrapes were ran, and any errors that might arise during runtime in the log file `scrapes.log`. The log is stored in the same subdirectory corresponding to the date of the scrape.</li> <li>**Replaced bulky titles with minimalist titles** for a cleaner look.</li> <li>**Added color to terminal output**.</li> <li>**Improved naming convention** for scripts.</li> <li>Integrating **Travis CI**.</li> <ul> <li>***In the process of adding unit tests for Travis and Codecov (`pytest` + `codecov` ).***</li> </ul> <li>***UPDATE COMMUNITY DOCS WHEN DONE REFACTORING.***</li> <li>Numerous changes to Readme. The most significant change was splitting and **storing walkthroughs in `docs/`**.</li> <ul> <li>Might have to restructure `docs/` for ReadTheDocs build. </ul> </ul> | 
