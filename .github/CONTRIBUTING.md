# Contributing Guide

Thank you for using the Universal Reddit Scraper! Since I was the only one developing URS, I have spent a lot of time creating it, and it has drastically evolved since its first iteration. 

### How URS Was Born

I initially created a Reddit scraper hard-coded to scrape Subreddits related to penetration testing, which is a field that I am studying. I sent the program to my friend [Luke Schenk](https://github.com/LukeDSchenk) since he is also pursuing pentesting, and he suggested that I could make a Reddit scraper that could scrape any Subreddit that I fed to the program, and URS 1.0 was born. Later on, Luke also introduced me to argparse, which is used to create command-line interface applications, so CLI support was added, spawning URS 2.0. CLI support made adding exporting to JSON, Redditor scraping, as well as post comments scraping functionality much easier to integrate, so URS 3.0 incorporated all of these new functions. I decided to end URS releases at 3.0 because the scraper can now scrape Subreddits, Redditors, and comments on posts, truly becoming a universal Reddit scraper.

### So What's Next?

Although I believe the current features (of URS 3.0) will satisfy users who need to scrape Reddit, I have not incorporated all the features that [PRAW](https://pypi.org/project/praw/) has to offer. New features are more than welcome! Just submit a pull request and fill out the pull request template located in the `assets` branch of this repository. 

Please keep all changes consistent with the name of this project. This means that the code submitted in pull requests will not be hard-coded to scrape specific Subreddits, Redditors, or Comments within Reddit. This is a *universal* Reddit scraper, so its users should be able to pass Reddit objects that they would like to scrape, rather than specific items that are integrated in the program.

# Table of Contents 

 - [Code of Conduct](#code-of-conduct)
 - [Important Resources](#important-resources)
 - [Questions](#questions)
 - [Feature Requests](#feature-requests)
 - [Reporting Bugs](#reporting-bugs)
 - [Improving Documentation](#improving-documentation)
 - [Contributing Code](#contributing-code)
	- [Style and Code Guidelines](#style-and-code-guidelines)
	- [Finding an Issue!](#finding-an-issue)
	- [Getting Started](#getting-started)
	- [Finding an Issue](#finding-an-issue)
 - [Pull Request Process](#pull-request-process)
	- [Addressing Feedback](#addressing-feedback)
 - [Community](#community)
	- [Real World Use of This Program](#real-world-use-of-this-program)


## Code of Conduct

Code of Conduct may be added in the future.

## Important Resources

 - [PRAW](https://praw.readthedocs.io/en/latest/)
 - [Argparse](https://pypi.org/project/argparse/)

## Questions

Please submit questions in the `issues` tab and apply the `question` label.

## Feature Requests

Please submit feature requests in the `issues` tab and apply the `enhancement` label.

Please provide the feature you would like to see, why you need it, and how it will work. Discuss your ideas transparently and get community feedback before proceeding.

Major Changes that you wish to contribute to the project should be discussed first in an GitHub issue that clearly outlines the changes and benefits of the feature.

Small Changes can directly be crafted and submitted to the GitHub Repository as a Pull Request. See the section about Pull Request Submission Guidelines, and for detailed information the core development documentation.

## Reporting Bugs

Please report bugs requests in the `issues` tab and apply the `bug` label.

Before you submit your issue, please [search the issue archive](https://github.com/JosephLai241/Universal-Reddit-Scraper/issues?q=is%3Aissue+is%3Aclosed) - maybe your question or issue has already been identified or addressed.

**Be sure to include a screenshot or a code block of the *entire* traceback of the error.**

## Improving Documentation

Should you have a suggestion for the documentation, you can open an issue with an `enhancement` label and outline the problem or improvement you have - however, creating the doc fix yourself is much better!

For large fixes, please build and test the documentation before submitting the PR to be sure you haven't accidentally introduced any layout or formatting issues.

For new features, please include screenshots of the feature running in a terminal within the `Walkthrough` section of the Readme.

## Contributing Code

The dependencies for this project are listed in the `requirements.txt` file. The versions of argparse and PRAW in `requirements.txt` are what I used when I tested this program.

### Style and Code Guidelines

Comments or code should be wrapped at 80 characters in length, if possible.

`if/elif/else` blocks should have no blank lines within the block. `try/except` blocks follow the same style.

Each function or global variable requires a comment above it explain what the function does or what the variable is used for.

Initialize each comment with three hashes:

```
### This is an example of the comment format
```

If a new feature is added and new functions are introduced, try to format functions so that the run order executes from top to bottom.

```
This is an example of what a new function block should look like:


#===============================================================================
#			[Function/Feature Name Here] Functions
#===============================================================================
def func_1():
	First function to run...
def func_2():
	Second function to run...
def func_3():
	Third function to run...
```

Working on your first open source project or pull request? Her are some helpful tutorials:

* [How to Contribute to an Open Source Project on GitHub][2]
* [Make a Pull Request][3]
* [First Timers Only][4]

### Getting Started

Install dependencies with `pip install -r requirements.txt` or `pip3 install -r requirements.txt` depending on your system.

You will need to fork the main repository to work on your changes. Simply navigate to the GitHub page and click the "Fork" button at the top. Once you've forked the repository, you can clone your new repository and start making edits.

In git it is best to isolate each topic or feature into a “topic branch”. While individual commits allow you control over how small individual changes are made to the code, branches are a great way to group a set of commits all related to one feature together, or to isolate different efforts when you might be working on multiple topics at the same time.

While it takes some experience to get the right feel about how to break up commits, a topic branch should be limited in scope to a single issue

```
# Checkout the master branch - you want your new branch to come from master
git checkout master

# Create a new branch named newfeature (give your branch its own simple informative name)
git branch newfeature

# Switch to your new branch
git checkout newfeature
```

For more information on the GitHub fork and pull-request processes, [please see this helpful guide][5].

### Finding an Issue

The list of outstanding feature requests and bugs can be found on our on our [GitHub issue tracker][6]. Pick an issue that you think you can accomplish and add a comment that you are attempting to do it.

Bugs can be submitted in the `Issues` tab.

> `starter` labeled issues are deemed to be good low-hanging fruit for newcomers to the project
> `help-wanted` labeled issues may be more difficult than `starter` and may include new feature development

## Pull Request Process

When you are ready to generate a pull request, either for preliminary review, or for consideration of merging into the project you must first push your local topic branch back up to GitHub:

```
git push origin newfeature
```

Once you've committed and pushed all of your changes to GitHub, go to the page for your fork on GitHub, select your development branch, and click the pull request button. If you need to make any adjustments to your pull request, just push the updates to your branch. Your pull request will automatically track the changes on your development branch and update.

1. Fill out the `PULL_REQUEST_TEMPLATE.md`, including a summary of changes, indicating the type of change, listing all changes individually, describing how you tested the new change(s), and going through the checklist to ensure you followed the development guidelines and produced quality code.

2. Update the README.md with details of changes and include a walkthrough accommodated by screenshots.
   
3. Increase the version numbers in `requirements.txt`, if applicable, and the README.md to the new version that this
   Pull Request would represent.
   
4. You may merge the Pull Request in once you have the sign-off from me.

### Addressing Feedback

Once a PR has been submitted, your changes will be reviewed and constructive feedback may be provided. Feedback isn't meant as an attack, but to help make sure the highest-quality code makes it into my project. Changes will be approved once required feedback has been addressed.

If you are asked to "rebase" your PR, this means a lot of code has changed, and that you need to update your fork so it's easier to merge.

To update your forked repository, follow these steps:

```
# Fetch upstream master and merge with your repo's master branch
git fetch upstream
git checkout master
git merge upstream/master

# If there were any new commits, rebase your development branch
git checkout newfeature
git rebase master
```

If too much code has changed for git to automatically apply your branches changes to the new master, you will need to manually resolve the merge conflicts yourself.

Once your new branch has no conflicts and works correctly, you can override your old branch using this command:

```
git push -f
```

Note that this will overwrite the old branch on the server, so make sure you are happy with your changes first!

## Community

If the `issues` tab does not suffice, you can email me at urs_project@protonmail.com if you have additional comments, suggestions, or questions about this project.

- If you know the answer (or a better solution to an existing answer) to a question that was listed in the `Issues` tab, feel free to contribute.

- If you have a better implementation of existing code that will improve runtime or streamline existing code, follow the pull request process to suggest improvements.

- If you liked this program, please spread the word and share it with others! 

### Real World Use of This Program

Web scrapers such as this one may be used in a professional environment, specifically IT departments for cyber threat analysis. These scrapers allow IT departments to collect user data quickly and easily. If used in conjunction with other scrapers that collect information from social media sites such as Twitter, IT departments may be able to create flagged portfolios for individuals who may become a security risk in the future, potentially preventing devastating cyber attacks against their company.

Additionally, this scraper may be used by businesses to better understand their target audience, improvements that can be made to existing products, or even spawn new ideas/products based on audience demands.

# ***Thank you all for using this program!***

[0]: CODE_OF_CONDUCT.md
[1]: style_guidelines.md
[2]: https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github
[3]: http://makeapullrequest.com/
[4]: http://www.firsttimersonly.com
[5]: https://gist.github.com/Chaser324/ce0505fbed06b947d962
[6]: https://github.com/JosephLai241/Universal-Reddit-Scraper/issues
[7]: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
