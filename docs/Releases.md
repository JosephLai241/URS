# Releases

## v3.1.3 - February TBD, 2021

* Added analytical tools.
    + Word frequencies generator.
    + Wordcloud generator.

## v3.1.2 - February 05, 2021

* Scrapes will now be exported to sub-folders within the date directory.
    + `comments`, `redditors`, and `subreddits` directories are now created for you when you run each scraper. Scrape results will now be stored within these directories.
* Minor code reformatting and refactoring.
    + The forbidden access message that may appear when running the Redditor scraper is now yellow to avoid confusion.
* Updated `README` and `STYLE_GUIDE`. Made a minor change to PRAW credentials guide.
    + Added new Derivative Projects section.
    + Uploaded new demo GIFs.

## v3.1.1 - June 27, 2020

* Added time filters for Subreddit categories (Controversial, Top, Search).
* Updated `README` to reflect new changes.
* Updated style guide.
    + Made minor formatting changes to scripts to reflect new rules.
* Performed DRY code review.


## v3.1.0 - June 22, 2020

* Major code refactor. Applied OOP concepts to existing code and rewrote methods in attempt to improve readability, maintenance, and scalability.
* Scrapes will now be exported to the `scrapes/` directory within a subdirectory corresponding to the date of the scrape. These directories are automatically created for you when you run URS.
* Added log decorators that record what is happening during each scrape, which scrapes were ran, and any errors that might arise during runtime in the log file `scrapes.log`. The log is stored in the same subdirectory corresponding to the date of the scrape.
* Replaced bulky titles with minimalist titles for a cleaner look.
* Added color to terminal output.
* Improved naming convention for scripts.
* Integrating Travis CI and Codecov.
* Updated community documents located in the `.github/` directory: 
    + `BUG_REPORT`
    + `CONTRIBUTING`
    + `FEATURE_REQUEST`
    + `PULL_REQUEST_TEMPLATE`
    + `STYLE_GUIDE`
* Numerous changes to `README`. The most significant change was splitting and storing walkthroughs in `docs/`.

## v3.0.0 - December 28, 2019 - January 15, 2020

* **Beta Release - December 28, 2019**
    + Added JSON export option.
    + Added Redditor scraping.
    + Comments scraping is still under construction.
* **Official Release - December 31, 2019**
    + Comments scraping is now working!
    + Added additional exception handling for creating filenames.
    + Minor code reformatting.
    + Simplified verbose output.
    + Added an additional submission attribute when scraping Redditors.
    + Happy New Year!
* **Final Release - January 15, 2020**
    + Numerous changes to `README`.
    + Fulfilled community standards by adding the following docs:
        * [Contributing Guide][Contributing Guide]
        * [Pull Request Template][Pull Request Template]
        * [Code of Conduct][Code of Conduct]
        * [License][License]
        * Issue templates:
            + [Bug Report][Bug Report]
            + [Feature Request][Feature Request]

## v2.0.0 - July 29, 2019

* Added CLI support.

## v1.0.0 - May 25, 2019

* Its inception.

<!-- COMMUNITY DOCS: Links to the community docs -->
[Bug Report]: https://github.com/JosephLai241/URS/blob/master/.github/ISSUE_TEMPLATE/BUG_REPORT.md
[Code of Conduct]: https://github.com/JosephLai241/URS/blob/master/.github/CODE_OF_CONDUCT.md
[Contributing Guide]: https://github.com/JosephLai241/URS/blob/master/.github/CONTRIBUTING.md
[Feature Request]: https://github.com/JosephLai241/URS/blob/master/.github/ISSUE_TEMPLATE/FEATURE_REQUEST.md
[License]: https://github.com/JosephLai241/URS/blob/master/LICENSE
[Pull Request Template]: https://github.com/JosephLai241/URS/blob/master/.github/PULL_REQUEST_TEMPLATE.md
