# Overview

## Summary

Delete this line and write your summary here. Section your summary by relevance if it is lengthy.

## Motivation/Context

Delete this line and write your motivation/context here. Section your motivation/context by relevance if it is lengthy.

## New Dependencies

```
Delete this line and paste your new dependencies here. Put "None" here if there are no new dependencies.
```

## Issue Fix or Enhancement Request

**Put "N/A" in this block if this is not applicable.**

If it fixes an open issue, link the issue and write a summary for the bug and fix like so:

* Fixes #issue_number_here.
    + **Bug:** Write a brief description of the bug.
    + **Fix:** Write a brief description of the fix.
        * If applicable, add additional information for the fix.

Alternatively, if it resolves an open feature/enhancement request, link the request in this pull request like so:

* Resolves #issue_number_here.
    + **Enhancement/Feature Request:** Write a brief description of the enhancement/feature request.
    + **Enhancement or Feature:** Write a brief description of what is new in this pull request.
        * If applicable, add additional information for the enhancement or feature.

If neither of the above apply, use the templates described above and replace the issue number with a summary of the new changes you have made.

# Type of Change

**Please delete options that are not relevant.**

* [x] Bug Fix (non-breaking change which fixes an issue)
* [x] Bug Fix - Breaking Change (breaking change causes existing functionality to not work as expected)
* [x] Code Refactor
* [x] New Feature (non-breaking change which adds functionality)
* [x] New Feature - Breaking Change (breaking change causes existing functionality to not work as expected)
* [x] This change requires a documentation update

# Breaking Change

**Put "N/A" in this block if this is not applicable.**

Delete this line and describe how URS breaks. Then provide a code block or screenshots of the ***entire*** traceback underneath your description. Section your description by relevance if it is lengthy. 

```
Paste entire traceback here. Make sure the traceback is formatted correctly.
```

# List All Changes That Have Been Made

**Please delete sections and/or fields that are not relevant.**

### Added

* User interface
    + Summary of change
        * Describing the change
* Source code
    + Summary of change
        * Describing the change
* `README`
    + Summary of change
        * Describing the change
* Tests
    + Summary of change
        * Describing the change
* Repository documents
    + Summary of change
        * Describing the change
* Community documents
    + Summary of change
        * Describing the change

### Changed

* User interface
    + Summary of change
        * Describing the change
* Source code
    + Summary of change
        * Describing the change
* `README`
    + Summary of change
        * Describing the change
* Tests
    + Summary of change
        * Describing the change
* Repository documents
    + Summary of change
        * Describing the change
* Community documents
    + Summary of change
        * Describing the change

### Deprecated

* User interface
    + Summary of change
        * Describing the change
* Source code
    + Summary of change
        * Describing the change
* `README`
    + Summary of change
        * Describing the change
* Tests
    + Summary of change
        * Describing the change
* Repository documents
    + Summary of change
        * Describing the change
* Community documents
    + Summary of change
        * Describing the change

# How Has This Been Tested?

**Put "N/A" in this block if this is not applicable.**

Please describe the tests that you ran to verify your changes. Provide instructions so I can reproduce. Please also list any relevant details for your test configuration. Section your tests by relevance if it is lengthy. An example outline is shown below:

* Summary of a test here
    + Details here with relevant test commands underneath.
        * Ran `test command here`.
            + If applicable, more details about the command underneath.
        * Then ran `another test command here`.

## Test Configuration

**Put "N/A" in this block if this is not applicable.**

* Python version: 3.x.x

If applicable, describe more configuration settings. An example outline is shown below:

* Summary goes here.
    + Configuration 1.
    + Configuration 2.
        * If applicable, provide extra details underneath a configuration.
    + Configuration 3.

New Travis CI configuration:

```yaml
If any changes have been made to `.travis.yml`, paste the new configuration file here. Delete this block if not.
```

## Dependencies

```
Paste your new `requirements.txt` here. Put "N/A" in this block if this is not applicable.
```

# Checklist

Tip: You can check off items by writing an "x" in the brackets, e.g. `[x]`.

* [ ] My code follows the [style guidelines][Style Guide] of this project.
* [ ] I have performed a self-review of my own code, including testing to ensure my fix is effective or that my feature works.
* [ ] My changes generate no new warnings.
* [ ] I have commented my code, providing a summary of the functionality of each method, particularly in areas that may be hard to understand.
* [ ] I have made corresponding changes to the documentation.
* [ ] I have performed a self-review of this Pull Request template, ensuring the Markdown file renders correctly.

<!-- LINKS -->
[Style Guide]: STYLE_GUIDE.md
