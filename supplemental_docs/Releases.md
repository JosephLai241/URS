# Releases

## v3.2.0 - February 25, 2021

### Added

* User Interface
    + Analytical tools
        * Word frequencies generator.
        * Wordcloud generator.
* Source code
    + CLI
        * Flags
            + `-e` - Display additional example usage.
            + `--check` - Runs a quick check for PRAW credentials and displays the rate limit table after validation.
            + `--rules` - Include the Subreddit's rules in the scrape data (for JSON only). This data is included in the `subreddit_rules` field.
            + `-f` - Word frequencies generator.
            + `-wc` - Wordcloud generator.
            + `--nosave` - Only display the wordcloud; do not save to file.
        * Added metavar for args help message.
        * Added additional verbose feedback if invalid arguments are given.
    + Log decorators
        * Added new decorator to log individual argument errors.
        * Added new decorator to log when no Reddit objects are left to scrape after failing validation check.
        * Added new decorator to log when an invalid file is passed into the analytical tools.
        * Added new decorator to log when the `scrapes` directory is missing, which would cause the new `make_analytics_directory()` method in `DirInit.py` to fail. 
            + This decorator is also defined in the same file to avoid a circular import error.
    + ASCII art
        * Added new art for the word frequencies and wordcloud generators.
        * Added new error art displayed when a problem arises while exporting data.
        * Added new error art displayed when Reddit object validation is completed and there are no objects left to scrape.
        * Added new error art displayed when an invalid file is passed into the analytical tools.
* `README` 
    + Added new Contact section and moved contact badges into it.
        + Apparently it was not obvious enough in previous versions since users did not send emails to the address specifically created for URS-related inquiries.
    + Added new sections for the analytical tools.
    + Updated demo GIFs
        * Moved all GIFs to a separate branch to avoid unnecessary clones.
        * Hosting static images on Imgur.
* Tests
    + Added additional tests for analytical tools.

### Changed

* User interface
    + JSON is now the default export option. `--csv` flag is required to export to CSV instead.
    + Improved JSON structure.
        * PRAW scraping export structure:
            + Scrape details are now included at the top of each exported file in the `scrape_details` field.
                * Subreddit scrapes - Includes `subreddit`, `category`, `n_results_or_keywords`, and `time_filter`.
                * Redditor scrapes - Includes `redditor` and `n_results`.
                * Submission comments scrapes - Includes `submission_title`, `n_results`, and `submission_url`.
            + Scrape data is now stored in the `data` field.
                * Subreddit scrapes - `data` is a list containing submission objects.
                * Redditor scrapes - `data` is an object containing additional nested dictionaries: 
                    + `information` - a dictionary denoting Redditor metadata, 
                    + `interactions` - a dictionary denoting Redditor interactions (submissions and/or comments). Each interaction follows the Subreddit scrapes structure.
                * Submission comments scrapes - `data` is an list containing additional nested dictionaries.
                    + Raw comments contains dictionaries of `comment_id: SUBMISSION_METADATA`.
                    + Structured comments follows the structure seen in raw comments, but includes an extra `replies` field in the submission metadata, holding a list of additional nested dictionaries of `comment_id: SUBMISSION_METADATA`. This pattern repeats down to third level replies.
        * Word frequencies export structure:
            + The original scrape data filepath is included in the `raw_file` field.
            + `data` is a dictionary containing `word: frequency`.
    + Log:
        * `scrapes.log` is now named `urs.log`.
        * Validation of Reddit objects is now included - invalid Reddit objects will be logged as a warning.
        * Rate limit information is now included in the log.
* Source code
    + Moved PRAW scrapers into its own package.
    + Subreddit scraper's "edited" field is now either a boolean (if the post was not edited) or a string (if it was).
        * Previous iterations did not distinguish the different types and would solely return a string.
    + Scrape settings for the basic Subreddit scraper is now cleaned within `Basic.py`, further streamlining conditionals in `Subreddit.py` and `Export.py`.
    + Returning final scrape settings dictionary from all scrapers after execution for logging purposes, further streamlining the `LogPRAWScraper` class in `Logger.py`.
    + Passing the submission URL instead of the exception into the `not_found` list for submission comments scraping.
        * This is a part of a bug fix that is listed in the Fixed section.
    + ASCII art:
        * Modified the args error art to display specific feedback when invalid arguments are passed.
    + Upgraded from relative to absolute imports.
    + Replaced old header comments with docstring comment block.
    + Upgraded method comments to Numpy/Scipy docstring format.
* `README`
    + Moved Releases section into its own document.
    + Deleted all media from master branch.
* Tests
    + Updated absolute imports to match new directory structure.
    + Updated a few tests to match new changes made in the source code.
* Community documents
    + Updated `PULL_REQUEST_TEMPLATE`:
        * Updated section for listing changes that have been made to match new Releases syntax.
        * Wrapped New Dependencies in a code block.
    + Updated `STYLE_GUIDE`:
        * Created new rules for method comments.
    + Added `Releases`:
        * Moved Releases section from main `README` to a separate document.

### Fixed

* Source code
    + PRAW scraper settings
        * **Bug:** Invalid Reddit objects (Subreddits, Redditors, or submissions) and their respective scrape settings would be added to the scrape settings dictionary even after failing validation.
        * **Behavior:** URS would try to scrape invalid Reddit objects, then throw an error mid-scrape because it is unable to pull data via PRAW. 
        + **Fix:** Returning the invalid objects list from each scraper into `GetPRAWScrapeSettings.get_settings()` to circumvent this issue.
    + Basic Subreddit scraper
        * **Bug:** The time filter `all` would be applied to categories that do not support time filter use, resulting in errors while scraping.
        * **Behavior:** URS would throw an error when trying to export the file, resulting in a failed run.
        * **Fix:** Added a conditional to check if the category allows for a time filter, and applies either the `all` time filter or `None` accordingly.

### Deprecated

* User interface
    + Removed the `--json` flag since it is now the default export option.

## v3.1.2 - February 05, 2021

### Added

* User interface
    + Scrapes will now be exported to sub-folders within the date directory.
        * `comments`, `redditors`, and `subreddits` directories are now created for you when you run each scraper. Scrape results will now be stored within these directories.
* `README`
    + Added new Derivative Projects section.

### Changed

* Source code
    + Minor code reformatting and refactoring.
    + The forbidden access message that may appear when running the Redditor scraper is now yellow to avoid confusion.
* Updated `README` and `STYLE_GUIDE`. 
    + Uploaded new demo GIFs.
* Made a minor change to PRAW credentials guide.

## v3.1.1 - June 27, 2020

### Added

* User interface
    + Added time filters for Subreddit categories (Controversial, Top, Search).

### Changed

* Source code
    + Changed how arguments are processed in the CLI.
    + Performed DRY code review.
* `README`
    + Updated `README` to reflect new changes.
* Community documents
    + Updated `STYLE_GUIDE`.
        * Made minor formatting changes to scripts to reflect new rules.

## v3.1.0 - June 22, 2020

### Added

* User interface
    + Scrapes will now be exported to the `scrapes/` directory within a subdirectory corresponding to the date of the scrape. These directories are automatically created for you when you run URS.

* Source code
    + Major code refactor. Applied OOP concepts to existing code and rewrote methods in attempt to improve readability, maintenance, and scalability.
    + Added log decorators that record what is happening during each scrape, which scrapes were ran, and any errors that might arise during runtime in the log file `scrapes.log`. The log is stored in the same subdirectory corresponding to the date of the scrape.
    + Added color to terminal output.
    + Integrating Travis CI and Codecov.

### Changed

* Source code
    + Replaced bulky titles with minimalist titles for a cleaner look.
    + Improved naming convention for scripts.
* Community documents
    + Updated the following documents:
        * `BUG_REPORT`
        * `CONTRIBUTING`
        * `FEATURE_REQUEST`
        * `PULL_REQUEST_TEMPLATE`
        * `STYLE_GUIDE`
* `README`
    + Numerous changes, the most significant change was splitting and storing walkthroughs in `docs/`.

## v3.0.0 - December 28, 2019 - January 15, 2020

* **Final Release - January 15, 2020**
    + **Added**
        + Community documents
            + Fulfilled community standards by adding the following docs:
                * [Contributing Guide][Contributing Guide]
                * [Pull Request Template][Pull Request Template]
                * [Code of Conduct][Code of Conduct]
                * [License][License]
                * Issue templates:
                    + [Bug Report][Bug Report]
                    + [Feature Request][Feature Request]
    + **Changed**
        * `README`
            + Numerous changes.
* **Official Release - December 31, 2019**
    + **Added**
        * User interface
            + Comments scraping is now working!
            + Added additional exception handling for creating filenames.
            + Added an additional submission attribute when scraping Redditors.
    + **Changed**
        * User interface
            + Simplified verbose output.
        * Source code
            + Minor code reformatting.
    + Happy New Year!
* **Beta Release - December 28, 2019**
    + **Added**
        * User interface
            + Added JSON export option.
            + Added Redditor scraping.
    + Comments scraping is still under construction.

## v2.0.0 - July 29, 2019

### Added

* User interface
    + Added CLI support.

## v1.0.0 - May 25, 2019

* Its inception.

<!-- COMMUNITY DOCS: Links to the community docs -->
[Bug Report]: https://github.com/JosephLai241/URS/blob/master/.github/ISSUE_TEMPLATE/BUG_REPORT.md
[Code of Conduct]: https://github.com/JosephLai241/URS/blob/master/.github/CODE_OF_CONDUCT.md
[Contributing Guide]: https://github.com/JosephLai241/URS/blob/master/.github/CONTRIBUTING.md
[Feature Request]: https://github.com/JosephLai241/URS/blob/master/.github/ISSUE_TEMPLATE/FEATURE_REQUEST.md
[License]: https://github.com/JosephLai241/URS/blob/master/LICENSE
[Pull Request Template]: https://github.com/JosephLai241/URS/blob/master/.github/PULL_REQUEST_TEMPLATE.md
