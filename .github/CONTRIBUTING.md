# Contributing Guide

URS has drastically evolved since its first iteration into what I hope is now an adequate tool for scraping Reddit. Since I am the only one developing URS, I have spent a lot of time and effort creating it, trying to make it the best Reddit scraper in the OSINT community. I appreciate every single one of its users and never would have imagined so many people would actually use this little project. Thank you all for using the Universal Reddit Scraper! 

# Table of Contents 
- [How URS Was Born](#how-urs-was-born)
- [So What's Next?](#so-whats-next)
- [Code of Conduct](#code-of-conduct)
- [Contributing Code](#contributing-code)
    - [Style Guide](#style-and-code-guidelines)
    - [Getting Started](#getting-started)
    - [Finding An Issue](#finding-an-issue)
- [Important Resources](#important-resources)
- [Questions](#questions)
- [Feature Requests](#feature-requests)
- [Reporting Bugs](#reporting-bugs)
- [Improving Documentation](#improving-documentation)
- [Pull Request Process](#pull-request-process)
- [Addressing Feedback](#addressing-feedback)
- [Community](#community)
- [Real World Use of This Program](#real-world-use-of-this-program)

### How URS Was Born

I initially created a Reddit scraper hard-coded to scrape Subreddits related to penetration testing, which is a field that I am studying. I sent the program to my friend [Luke Schenk](https://github.com/LukeDSchenk) since he is also pursuing pentesting, and he suggested that I could make a Reddit scraper that could scrape any Subreddit that I fed to the program, and URS 1.0.0 was born. 

Later on, Luke also introduced me to argparse, which is used to create command-line interface applications, so CLI support was added, spawning URS 2.0.0.

CLI support made adding exporting to JSON, Redditor scraping, as well as post comments scraping functionality much easier to integrate, so URS 3.0.0 incorporated all of these new functions. 

I was still unsatisfied with the quality of my code, so I decided to do an OOP refactor and restructured URS. While the primary motivation was to make my code more readable, maintainable, and scalable, I also added color to terminal output, logger decorators, sorting scrape files into their own directories, and integrated Travis CI and Codecov. This spawned the release of URS 3.1.0.

URS 3.1.1+ will continue building upon the foundation set by URS 3.1.0 by adding features that have been requested by the open source community or features that I believe will enhance the capabilities of URS or improve the user experience.

I plan on adding additional features as URS continues to grow, so stay tuned for updates! 

### So What's Next?

Although I believe the current features should satisfy most users who need to scrape Reddit, there is still room to grow and you are more than welcome to create a pull request! Just be sure to fill out the pull request template when you do so I have a better idea as to what you are trying to change or add.

Please keep all changes consistent with the name of this project. This means that the code submitted in pull requests will not be hard-coded to scrape specific Subreddits, Redditors, or submissions within Reddit. This project will also [exclude capabilities that allow users to interact with Reddit][Outside of Project Scope] outside of merely scraping data from the website. Remember the name of this repository: this is a *universal* Reddit *scraper*.

## Code of Conduct

[Code of Conduct][Code of Conduct]

## Contributing Code

### Style Guide

**It is important that you read the [Style Guide][Style Guide] before you contribute any code**. I have a particular style that I think will ensure your code is easy to read, maintain, and is scalable. Enforcing this style will also allow potential contributors to easily get used to how the code is structured and guarantee they will not be surprised by strange syntax. URS is an open-source project, which means the goal here is to push code that anyone can help improve upon.

### Getting Started

Install dependencies with `pip install -r requirements.txt` or `pip3 install -r requirements.txt` depending on your system.

You will need to fork the main repository to work on your changes. Simply navigate to the GitHub page and click the "Fork" button at the top. Once you've forked the repository, you can clone your new repository and start making edits.

In git it is best to isolate each topic or feature into a “topic branch”. While individual commits allow you control over how small individual changes are made to the code, branches are a great way to group a set of commits all related to one feature together, or to isolate different efforts when you might be working on multiple topics at the same time.

While it takes some experience to get the right feel about how to break up commits, a topic branch should be limited in scope to a single issue

```bash
# Checkout the master branch - you want your new branch to come from master
git checkout master

# Create a new branch named newfeature (give your branch its own simple informative name)
git branch newfeature

# Switch to your new branch
git checkout newfeature
```

For more information on the GitHub fork and pull-request processes, [please see this helpful guide][Pull Request Guide].

### Finding an Issue

The list of outstanding feature requests and bugs can be found on our on our [GitHub issue tracker][Issues]. Pick an issue that you think you can accomplish and add a comment that you are attempting to do it.

Bug Reports can be submitted in the `Issues` tab.

## Important Resources

* [PRAW](https://praw.readthedocs.io/en/latest/)
 
## Questions

Please submit questions in the `issues` tab and apply the `question` label.

Alternatively, feel free to send me an email at [urs_project@protonmail.com][URS Project Protonmail].

## Feature Requests

Please submit feature requests in the `issues` tab by filling out the Feature Request template.

Please provide the feature you would like to see, why you need it, and how it will work. Discuss your ideas transparently so I can better understand why this feature is necessary.

Major changes that you wish to contribute to the project should be discussed first in an GitHub issue that clearly outlines the changes and benefits of the feature.

Small changes can directly be crafted and submitted to the GitHub Repository as a pull request. See the section about pull request Submission Guidelines, and for detailed information the core development documentation.

## Reporting Bugs

Please report bugs requests in the `issues` tab by filling out the Bug Report template.

Before you submit your issue, please [search the issue archive](https://github.com/JosephLai241/Universal-Reddit-Scraper/issues?q=is%3Aissue+is%3Aclosed) - maybe your question or issue has already been identified or addressed.

**Be sure to include a screenshot or a code block of the *entire* traceback of the error in the Bug Report template.**

## Improving Documentation

Should you have a suggestion for the documentation, you can open an issue with an `enhancement` label and outline the problem or improvement you have - however, creating the doc fix yourself is much better!

For large fixes, please build and test the documentation before submitting the pull request to be sure you haven't accidentally introduced any layout or formatting issues.

For new features, please include screenshots or a demo GIF of the feature running in a terminal.

## Pull Request Process

When you are ready to generate a pull request, either for preliminary review, or for consideration of merging into the project you must first push your local topic branch back up to GitHub:

```bash
git push origin newfeature
```

Once you've committed and pushed all of your changes to GitHub, go to the page for your fork on GitHub, select your development branch, and click the pull request button. If you need to make any adjustments to your pull request, just push the updates to your branch. Your pull request will automatically track the changes on your development branch and update.

1. Completely fill out the `PULL_REQUEST_TEMPLATE.md`. Make sure you go through the checklist to ensure you have followed the necessary procedures.

2. Update the `README.md` with details of changes and include a walkthrough accommodated by screenshots. If the section is long or does not directly relate to the functionality of URS, create a new Markdown file in `docs/` and link the doc to a new bullet point in the README's table of contents.
   
3. Increase the version numbers in `requirements.txt`, if applicable, and the README.md to the new version that this
pull request would represent.

### Addressing Feedback

Once a pull request has been submitted, your changes will be reviewed and constructive feedback may be provided. Feedback is not meant as an attack, but to help make sure the highest-quality code makes it into my project. Changes will be approved once required feedback has been addressed.

If you are asked to "rebase" your pull request, this means a lot of code has changed, and that you need to update your fork so it's easier to merge.

To update your forked repository, follow these steps:

```bash
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

```bash
git push -f
```

Note that this will overwrite the old branch on the server, so make sure you are happy with your changes first!

## Community

If the `issues` tab does not suffice, you can email me at [urs_project@protonmail.][URS Project Protonmail] if you have additional comments, suggestions, or questions about this project.

- If you know the answer (or a better solution to an existing answer) to a question that was listed in the `Issues` tab, feel free to contribute.

- If you have a better implementation of existing code that will improve runtime or introduces better logic, follow the pull request process to suggest improvements.

- If you liked this program, please spread the word and share it with others! 

### Real World Use of This Program

Web scrapers such as this one may be used in a professional environment, specifically IT departments for cyber threat analysis. These scrapers allow IT departments to collect user data quickly and easily. If used in conjunction with other scrapers that collect information from social media sites such as Twitter, IT departments may be able to create flagged portfolios for individuals who may become a security risk in the future, potentially preventing devastating cyber attacks against their company.

This scraper may also be used by businesses to better understand their target audience, improvements that can be made to existing products, or even spawn new ideas/products based on audience demands.

Reddit contains a lot of interesting information on the internet. I am sure the uses I have listed above are not the only ways someone can use URS!

## ***Thank you all for using this program!***

[Code of Conduct]: CODE_OF_CONDUCT.md
[How To Contribute]: https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github
[Issues]: https://github.com/JosephLai241/Universal-Reddit-Scraper/issues
[Pull Request Guide]: https://gist.github.com/Chaser324/ce0505fbed06b947d962
[Style Guide]: STYLE_GUIDE.md
[URS Project Protonmail]: mailto:urs_project@protonmail.com

[Outside of Project Scope]: https://github.com/JosephLai241/URS/issues/17