# Contributing Guide

Thank you for using the Universal Reddit Scraper! Since I was the only one developing URS, I have spent a lot of time creating it, and it has drastically evolved since its first iteration. 

### URS History

I initially created a Reddit scraper hard-coded to scrape Subreddits related to penetration testing, which is a field that I am studying. I sent the program to my friend since he is also pursuing pentesting, and he suggested that I could make a Reddit scraper that could scrape any Subreddit that I fed to the program, and URS 1.0 was born. Later on, command-line interface support was added, which was URS 2.0. CLI support made adding exporting to JSON, Redditor scraping, as well as post comments scraping functionality much easier to integrate, so URS 3.0 incorporated all of these new functions. I decided to end URS releases at 3.0 because the scraper can now scrape Subreddits, Redditors, and comments on posts, truly becoming a universal Reddit scraper.

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
6. [Contributing Code](#contributing-code)
	1. [Getting Started](#getting-started)
	1. [Finding an Issue!](#finding-an-issue)
	1. [Development Process](#development-process)
	1. [Building the Project](#building-the-project)
	1. [Testing](#testing)
	1. [Style Guidelines](#style-guidelines)
	1. [Code Formatting Rules](#code-formatting)
	1. [Whitespace Cleanup](#whitespace-cleanup)
1. [Pull Request Guidelines](#pull-request-process)
	1. [Review Process](#review-process)
	1. [Addressing Feedback](#addressing-feedback)
1. [Community](#community)


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

This section is used to get new contributors up and running with dependencies, development, testing, style rules, formatting rules, and other things they should know.

If you have a label for beginner issues, talk about that here so they know where to look:

> Unsure where to begin contributing to Atom? You can start by looking through these beginner and help-wanted issues: Beginner issues - issues which should only require a few lines of code, and a test or two. Help wanted issues - issues which should be a bit more involved than beginner issues.

Working on your first open source project or pull request? Her are some helpful tutorials:

* [How to Contribute to an Open Source Project on GitHub][2]
* [Make a Pull Request][3]
* [First Timers Only][4]

### Getting Started

Install these dependencies:

```
with some examples
```

Provide some instructions for your workflow (e.g. fork the repository)

> You will need to fork the main repository to work on your changes. Simply navigate to our GitHub page and click the "Fork" button at the top. Once you've forked the repository, you can clone your new repository and start making edits.

> In git it is best to isolate each topic or feature into a “topic branch”. While individual commits allow you control over how small individual changes are made to the code, branches are a great way to group a set of commits all related to one feature together, or to isolate different efforts when you might be working on multiple topics at the same time.

> While it takes some experience to get the right feel about how to break up commits, a topic branch should be limited in scope to a single issue

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

The list of outstanding feature requests and bugs can be found on our on our [GitHub issue tracker][6]. Pick an unassigned issue that you think you can accomplish and add a comment that you are attempting to do it.

Provide notes on different kinds of issues or labels

> `starter` labeled issues are deemed to be good low-hanging fruit for newcomers to the project
> `help-wanted` labeled issues may be more difficult than `starter` and may include new feature development
> `doc` labeled issues must only touch content in the `docs` folder.

### Development Process

What is your development process?

> This project follows the [git flow](http://nvie.com/posts/a-successful-git-branching-model/) branching model of product development.

Talk about branches people should work on. Sspecifically, where is the starting point? `master`, `development`, etc.

> You should be using the master branch for the most stable release; please review [release notes](https://github.com/openopps/openopps-platform/releases) regularly. We do releases every week or two and send out notes. If you want to keep up with the latest changes, we work in the `dev` branch.  If you are using dev, keep an eagle-eye on commits and/or join our daily standup.

### Building the Project

What branches should be work be started off of?

Include instructions on how to build the project.

```
with some examples
```

Provide instructions on adding a new file/module to the build

```
with some examples
```

Keep your tests as simple as possible.

### Testing

If you add code you need to add tests! We’ve learned the hard way that code without tests is undependable. If your pull request reduces our test coverage because it lacks tests then it will be rejected.

Provide instructions for adding new tests. Provide instructions for running tests.

```
with examples
```

### Style Guidelines

If your code has any style guidelines, add them here or provide links to relevant documents. If you have an automated checker, make sure to provide instructions on how to run it.

### Code Formatting

If your code has any formatting guidelines that aren't covered in the style guidelines above, add them here.

If you're using an auto-formatting tool like clang-format

```
Provide instructions for running the formatting tool
```

### Whitespace Cleanup

Don’t mix code changes with whitespace cleanup! If you are fixing whitespace, include those changes separately from your code changes. If your request is unreadable due to whitespace changes, it will be rejected.

> Please submit whitespace cleanups in a separate pull request.

### Git Commit Guidelines

Do you have any guidelines for your commit messages? Include them here.

> The first line of the commit log must be treated as as an email
subject line.  It must be strictly no greater than 50 characters long.
The subject must stand on its own and not only make external
references such as to relevant bug numbers.

> The second line must be blank.

> The third line begins the body of the commit message (one or more
paragraphs) describing the details of the commit.  Paragraphs are each
separated by a blank line.  Paragraphs must be word wrapped to be no
longer than 76 characters.

> The last part of the commit log should contain all "external
references", such as which issues were fixed.

> For further notes about git commit messages, [please read this blog post][7].

## Pull Request Process

Do you have any labelling conventions?

Add notes for pushing your branch:

> When you are ready to generate a pull request, either for preliminary review, or for consideration of merging into the project you must first push your local topic branch back up to GitHub:

```
git push origin newfeature
```

Include a note about submitting the PR:

> Once you've committed and pushed all of your changes to GitHub, go to the page for your fork on GitHub, select your development branch, and click the pull request button. If you need to make any adjustments to your pull request, just push the updates to your branch. Your pull request will automatically track the changes on your development branch and update.

1. Ensure any install or build dependencies are removed before the end of the layer when doing a
   build.
2. Update the README.md with details of changes to the interface, this includes new environment
   variables, exposed ports, useful file locations and container parameters.
3. Increase the version numbers in any examples files and the README.md to the new version that this
   Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
4. You may merge the Pull Request in once you have the sign-off of two other developers, or if you
   do not have permission to do that, you may request the second reviewer to merge it for you.

### Review Process

Who reviews it? Who needs to sign off before it’s accepted? When should a contributor expect to hear from you? How can contributors get commit access, if at all?

> The core team looks at Pull Requests on a regular basis in a weekly triage meeting that we hold in a public Google Hangout. The hangout is announced in the weekly status updates that are sent to the puppet-dev list. Notes are posted to the Puppet Community community-triage repo and include a link to a YouTube recording of the hangout. After feedback has been given we expect responses within two weeks. After two weeks we may close the pull request if it isn't showing any activity.

> Except for critical, urgent or very small fixes, we try to leave pull requests open for most of the day or overnight if something comes in late in the day, so that multiple people have the chance to review/comment.  Anyone who reviews a pull request should leave a note to let others know that someone has looked at it.  For larger commits, we like to have a +1 from someone else on the core team and/or from other contributor(s).  Please note if you reviewed the code or tested locally -- a +1 by itself will typically be interpreted as your thinking its a good idea, but not having reviewed in detail.

Perhaps also provide the steps your team will use for checking a PR. Or discuss the steps run on your CI server if you have one. This will help developers understand how to investigate any failures or test the process on their own.

### Addressing Feedback

Once a PR has been submitted, your changes will be reviewed and constructive feedback may be provided. Feedback isn't meant as an attack, but to help make sure the highest-quality code makes it into our project. Changes will be approved once required feedback has been addressed.

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your fork so it's easier to merge.

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

Do you have a mailing list, google group, slack channel, IRC channel? Link to them here.

> Anyone actively contributing to or using OpenOpps should join our [Mailing List](https://groups.google.com/forum/#!forum/openopps-platform).
We also have a public Slack chat team. If you're interested in following along with the development process or have questions, feel free to [join us](https://openopps.slack.com).

Include Other Notes on how people can contribute

* You can help us answer questions our users have here:
* You can help build and design our website here:
* You can help write blog posts about the project by:
* You can help with newsletters and internal communications by:

* Create an example of the project in real world by building something or
showing what others have built.
* Write about other people’s projects based on this project. Show how
it’s used in daily life. Take screenshots and make videos!

[0]: CODE_OF_CONDUCT.md
[1]: style_guidelines.md
[2]: https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github
[3]: http://makeapullrequest.com/
[4]: http://www.firsttimersonly.com
[5]: https://gist.github.com/Chaser324/ce0505fbed06b947d962
[6]: link/to/your/project/issue/tracker
[7]: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
