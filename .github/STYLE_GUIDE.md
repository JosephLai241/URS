# Table of Contents

* [Introduction](#introduction)
* [Tabs](#tabs)
* [Word Wrap](#word-wrap)
* [Whitespace](#whitespace)
* [Comments](#comments)
* [URS Code](#urs-code)
* [Unit Testing Code](#unit-testing-code)

# Introduction

The goal is to write code that is maintainable, readable, and scalable. This standard is applied to both URS code and unit tests.

# Tabs

Tabs are set at 4 spaces wide for all scripts.

# Word Wrap

Word wrap should be 80-83 characters per line. You can modify your editor settings to display a horizontal ruler at 80 characters, which is very useful for following the wrap guideline.

Use `\` to write a line of code in multiple lines.

Indent each following line by a tab to indicate it is still the same line of code.

If you have a long line of code, try to separate it by any special characters or keywords. Showing an example would be the best way to describe this.

Take a look at this `redditor_list` variable that is set by [ternary operator](https://book.pythontips.com/en/latest/ternary_operators.html):

```python
redditor_list = self._make_submission_list(item) if isinstance(item, praw.models.Submission) else self._make_comment_list(item)
```

This line greatly exceeds the 80 character count. In cases like these, wrap the line like so:

```python
redditor_list = self._make_submission_list(item) \
    if isinstance(item, praw.models.Submission) \
        else self._make_comment_list(item)
```

Let's take a look at another example. Here I am printing a string that uses string formatting to pass in variables:

```python
print(Style.BRIGHT + ("\nProcessing %s %s from u/%s's profile...") % (limit, plurality, user))
```

Again, this line exceeds the 80 character count. You can split this into two lines at the special character `%`.

```python
print(Style.BRIGHT + ("\nProcessing %s %s from u/%s's profile...") % 
    (limit, plurality, user))
```

If you are printing a string that is longer than 80 characters, do not worry about splitting the string into sections. Just place the string on its own line and pass in the variables on a new line.

```python
print(Style.BRIGHT + 
    ("\nThis is a very long line that is going to be a lot longer than 80 characters %s %s %s") % 
        (something, another_thing, something_else))
```

Let's take a look at a third example. Here I am defining a very long list that will greatly exceed 80 characters:

```python
self._titles = ["Name", "Fullname", "ID", "Date Created", "Comment Karma", "Link Karma", "Is Employee?", "Is Friend?", "Is Mod?", "Is Gold?", "Submissions", "Comments", "Hot", "New", "Controversial", "Top", "Upvoted (may be forbidden)", "Downvoted (may be forbidden)", "Gilded", "Gildings (may be forbidden)", "Hidden (may be forbidden)", "Saved (may be forbidden)"]
```

If more than half of the word populates the space before the 80 character mark and exceeds the limit by ~2-4 characters, you can leave it on the same line. But if the word is more than ~10 characters over the limit, put it on a new line.

```python
self._titles = ["Name", "Fullname", "ID", "Date Created", "Comment Karma", 
    "Link Karma", "Is Employee?", "Is Friend?", "Is Mod?", "Is Gold?", 
    "Submissions", "Comments", "Hot", "New", "Controversial", "Top", 
    "Upvoted (may be forbidden)", "Downvoted (may be forbidden)", "Gilded", <- Exceeds the limit by 2 chars 👍
    "Gildings (may be forbidden)", "Hidden (may be forbidden)", 
    "Saved (may be forbidden)"]
```

# Whitespace

Commas should be followed by a space:

```python
example_list_with_commas = [1, 2, 3, 4, 5]
```

This includes method parameters:

```python
def example_method(self, first_param, second_param, third_param):
```

There should be a space preceeding and following all equal signs or conditionals, comparison operators, etc.:

```python
example = "something"
boolean == True
something = one_thing if a_condition != None else another_thing
```

Long dictionaries can be hard to read on just one line, so you will split each key, value onto its own line. Each value for a key should be preceeded with a space. Lists are not as difficult to read on one line, so values do not need to be split into their own lines:

```python
a_dictionary = {
    "this": 1,
    "is": 2,
    "an": 3,
    "example": 4,
    "of": 5,
    "a": 6,
    "long": 7,
    "dictionary": ["an", "example", "list", "here"]
}
```

Variables should be grouped by relevance and separated by a new line:

```python
self._comment_titles = ["Date Created", "Score", "Text", "Parent ID", 
    "Link ID", "Edited?", "Stickied?", "Replying to", "In Subreddit"]
self._submission_titles = ["Title", "Date Created", "Upvotes", "Upvote Ratio",
    "ID", "NSFW?", "In Subreddit", "Body"]

self._mutts = [self._controversial, self._gilded, self._hot, self._new, 
    self._top]
self._mutt_names = ["Controversial", "Gilded", "Hot", "New", "Top"]

self._access = [self._downvoted, self._gildings, self._hidden, self._saved, 
    self._upvoted]
self._access_names = ["Downvoted", "Gildings", "Hidden", "Saved", "Upvoted"]
```

Methods and classes are separated by a new line:

```python
### First method here.
def first_method_here():
    pass

### Second method here.
def second_method_here():
    pass
```

Class methods following the class comment will be preceeded by a new line.

```python
class FirstClass():
    """
    The first class.
    """

    ### A method here.
    def a_method_here(self):
        pass

    ### A second method here.
    def a_second_method_here(self):
        pass

class SecondClass():
    """
    Second class here.
    """

    ### Another method here.
    def another_method_here(self):
        pass
```

# Comments

***Every single class and method requires at least one comment with proper grammar and punctuation***. By doing this, I will easily be able to tell which class most likely contains the method I am looking for. Comments will also follow the ~80 character word wrap rule.

## Class Comments

Class comments should use blocks placed underneath the class:

```python
class ThisIsAnExampleClass():
    """
    This is an example of a class comment.
    """
```

## Method Comments

Method comments should start with `###` so that it is easily distinguished from code. These comments are placed above the method.

```python
    ### This is an example of a method comment.
    def this_is_an_example_method(self):
```

## Global Variable Comments

Global variables or functions follow the same style as method comments.

```python
### An example of a global comment 
an_example_list = ["subreddit", "redditor", "submissions"]
```

An example taken from my code would be calling the Colorama `init` function at the top of most scripts:

```python
### Automate sending reset sequences to turn off color changes at the end of 
### every print
init(autoreset = True)
```

# URS Code

## Classes

Every method in URS has to be wrapped in a class. These classes contain methods that are sorted by relevance. 

Showing an example would be the best way to describe how the code is structured:

The `Write` class on line 216 in `Redditor.py` wraps all methods relating to exporting scraped Redditor data to a CSV or JSON file.

```python
class Write():
    """
    Functions for writing scraped Redditor information to CSV or JSON.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._eo = Global.eo

    ### Export to either CSV or JSON.
    def _determine_export(self, args, f_name, overview):
        ...

    ### Print confirmation message and set print length depending on string length.
    def _print_confirm(self, args, user):
        ...

    ### Get, sort, then write scraped Redditor information to CSV or JSON.
    def write(self, args, reddit, u_master):
        ...
        calls _determine_export()
        then calls _print_confirm()
```

Python does not have true "private" methods or variables, but we can indicate that they are only supposed to be called within the class by prepending an underscore in front of the method or variable name. 

`write()` is called outside of the `Write` class, which is why an underscore is not prepended. `_determine_export()` and `_print_confirm()` are called by `write()` but are not called outside the function, hence why they are prepended with an underscore.

## Modularizing Code

The block of code above is also another great representation of how sections of code should be organized.

Within `write()`, `_determine_export()` is called first, followed by `_print_confirm()`. The order in which smaller methods that will be called in a class's "main" method should be sorted by execution order (from top to bottom). These smaller methods will also be placed above the "main" method.


# Unit Testing Code

Every method in URS has to be wrapped in a class for unit testing. This makes it easier to add and group tests if features are added to a method in the future.

Showing an example would be the best way to describe how unit tests should be named and structured:

`_list_switch()` is a method found on line 144 in `Cli.py` within the `GetScrapeSettings` class:

```python
class GetScrapeSettings():
    """
    Functions for creating data structures to store scrape settings.
    """
    
    ### Switch to determine which kind of list to create.
    def _list_switch(self, args, index):
        ...
```

The unit test for this function is located in the `tests/` directory in the file `test_Cli.py` and looks like this:

```python
class TestGetScrapeSettingsListSwitchMethod():
    """
    Testing GetScrapeSettings class _list_switch() method found on line 144 in 
    Cli.py.
    """
    
    def test_list_switch_method_first_switch(self):
        ...
    
    def test_list_switch_method_second_switch(self):
        ...

    def test_list_switch_method_third_switch(self):
        ...
```

The unit test class will use the following naming convention: 

```python
class Test[CamelCaseClassName][CamelCaseMethodName]Method():
    ...
```

Include a block comment under the unit test class using the following convention:

```
Testing [ClassName] class [method_name()] method found on line [line number] in [ScriptName.py].
```

The unit test method will use the following naming convention:

```python
    def test_[underscored_method_name]_[underscored_test_case](self):
        ...
```
