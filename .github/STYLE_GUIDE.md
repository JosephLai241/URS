# URS Style Guide

## Table of Contents

* [Introduction](#introduction)
* [Tabs](#tabs)
* [Word Wrap](#word-wrap)
* [Whitespace](#whitespace)
* [Comments](#comments)
* [Imports](#imports)
* [Method Parameters](#method-parameters)
* [URS Code](#urs-code)
* [Unit Testing Code](#unit-testing-code)

## Introduction

The goal is to write code that is maintainable, readable, and scalable. This standard is applied to both URS code and unit tests.

***Pro tip***: When in doubt, do it in alphabetical order.

## Tabs

![TABS NOT SPACES](https://markjaquith.files.wordpress.com/2018/06/not-hiring.gif)

**Tabs** are set at 4 spaces wide for all scripts.

<sub>Silicon Valley is great show, by the way.</sub>

## Word Wrap

Try your best to word wrap around 80-83 characters per line. You can modify your editor settings to display a horizontal ruler at 80 characters, which is very useful for following the wrap guideline.

Use `\` to write a line of code in multiple lines.

Indent each following line by a tab to indicate it is still the same line of code.

If you have a long line of code, try to separate it by any special characters or keywords. Showing an example would be the best way to describe this.

Take a look at this `redditor_list` variable that is set by a [ternary operator](https://book.pythontips.com/en/latest/ternary_operators.html):

```python
redditor_list = _make_submission_list(item) if isinstance(item, praw.models.Submission) else _make_comment_list(item)
```

This line greatly exceeds the 80 character count. In cases like these, wrap the line like so:

```python
redditor_list = _make_submission_list(item) \
    if isinstance(item, praw.models.Submission) \
    else _make_comment_list(item)
```

Let's take a look at another example. Here I am printing a string that uses string formatting to pass in variables:

```python
print(("\nProcessing %s %s from u/%s's profile... Extending this print line") % (limit, plurality, user))
```

Again, this line exceeds the 80 character count. You can split this into two lines after the special character `%`.

```python
print(("\nProcessing %s %s from u/%s's profile... Extending this print line") % 
    (limit, plurality, user))
```

If you are printing a string that is longer than 80 characters, do not worry about splitting the string into sections. Just place the string on its own line and pass in the variables on a new line.

```python
print(Style.BRIGHT + 
    ("\nThis is a very long line that is going to be a lot longer than 80 characters %s %s %s") % 
    (something, another_thing, something_else))
```

Or if you are passing in many variables into a string, do not worry about breaking the variables into new lines. Breaking them into a different line may affect readability, which is the opposite of what we're trying to achieve with this style guide. This rule also applies to methods that take in many arguments.

```python
print(("Passing %s a %s lot %s of %s variables %s in %s this %s string") %
    (first_thing, second_thing, third_thing, fourth_thing, fifth_thing, six_thing, seventh_thing))
                                                                                ^
                                                                                |
                                                                            Exceeds 80 chars
```

## Whitespace

Commas should be followed by a space. This includes method parameters:

```python
def example_method(self, a_first_param, b_second_param, c_third_param):
```

There should be a space preceeding and following all equal signs or conditionals, comparison operators, etc.:

```python
boolean == True
example = "something"
something = one_thing if a_condition != None else another_thing
```

Each item in a list should be on its own line:

```python
titles = [
    "Name", 
    "Fullname", 
    "ID", 
    "Date Created", 
    "Comment Karma", 
    "Link Karma", 
    "Is Employee?", 
    "Is Friend?", 
    "Is Mod?", 
    "Is Gold?", 
    "Submissions", 
    "Comments", 
    "Hot", 
    "New", 
    "Controversial", 
    "Top", 
    "Upvoted (may be forbidden)", 
    "Downvoted (may be forbidden)", 
    "Gilded", 
    "Gildings (may be forbidden)", 
    "Hidden (may be forbidden)", 
    "Saved (may be forbidden)"]
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
    "dictionary": [
        "an", 
        "example", 
        "list", 
        "here"]
}
```

All variables should be grouped by relevance, sorted in alphabetical order, and separated by a new line. This applies to global, instance, and method variables.

```python
comment_titles = [
    ...]
submission_titles = [
    ...]
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

    ### A private method here.
    def _a_private_method_here(self):
        pass

    ### A second public method here.
    def a_second_public_method_here(self):
        pass

class SecondClass():
    """
    Second class here.
    """

    ### Another public method here.
    def another_method_here(self):
        pass
```

## Comments

***Every single class and method requires at least one comment with proper grammar and punctuation***. By doing this, I will easily be able to tell which class most likely contains the method I am looking for. Comments will also follow the ~80 character word wrap rule.

### Class Comments

Class comments should use blocks placed underneath the class:

```python
class ThisIsAnExampleClass():
    """
    This is an example of a class comment.
    """
```

### Method Comments

Method comments should start with `###` so that it is easily distinguished from code. These comments are placed above the method.

```python
    ### This is an example of a method comment.
    def this_is_an_example_public_method(self):
```

### Global Variable Comments

Global variables or functions follow the same style as method comments.

```python
### An example of a global comment.
an_example_list = ["subreddit", "redditor", "submissions"]
```

An example taken from my code would be calling the Colorama `init` function at the top of most scripts:

```python
### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)
```

## Imports

All imports have to be listed at the top of each script. Each group is sorted in alphabetical order.

Standard library and third-party imports are listed first, then relative imports. These imports should be separated by a new line.

Imports using the `import` form come before imports using the `from` form. These imports should also be separated by a new line.

Relative imports that import an entire module come before importing a module class.

Additionally, multiple imports should be on its own line. Lowercase imports are listed before uppercase imports. Each are sorted by alphabetical order. 

Here is an example of a group of imports from `Redditor.py`.

```python
import praw

from colorama import (
    init,  <----------------- Lowercase imports come first
    Fore, 
    Style) <----------------- Alphabetical order
from prawcore import PrawcoreException

from . import (
    Cli, 
    Export, 
    Global, 
    Titles, 
    Validation) <-- Alphabetical order
from .Logger import (
    LogExport, 
    LogScraper) <-------------- Alphabetical order
```

## Method Parameters

### Static Methods

Static method parameters should be sorted in alphabetical order:

```python
@staticmethod
def example_method(args, basic, comments, parser, reddit, subreddit):
```

### Instance methods

Instance methods will take `self` as the first parameter, followed by all other parameters sorted in alphabetical order:

```python
def example_with_self(self, args, basic, comments, parser, reddit, subreddit):
```

### Init methods

`init` methods follow the same style above. Again, instance variables defined in the `init` method will be grouped by relevance and sorted in alphabetical order.

This is a modified version of the huge `init` method in `Redditor.py`:

```python
    ### Initialize objects that will be used in class methods.
    def __init__(self, limit, overview, user):
        self._overview = overview

        self._controversial = user.controversial(limit = limit)
        self._downvoted = user.downvoted(limit = limit)
        self._gilded = user.gilded(limit = limit)
        self._gildings = user.gildings(limit = limit)
        self._hidden = user.hidden(limit = limit)
        self._hot = user.hot(limit = limit)
        self._new = user.new(limit = limit)
        self._saved = user.saved(limit = limit)

        self._comment_titles = [
            "Date Created", 
            "Score", 
            "Text", 
            "Parent ID"]
        self._submission_titles = [
            "Title", 
            "Date Created", 
            "Upvotes", 
            "Upvote Ratio"]

        self._s_types = [
            "Submissions", 
            "Comments", 
            "Mutts", 
            "Access"]

        self._mutts = [
            self._controversial, 
            self._gilded, 
            self._hot, 
            self._new]
        self._mutt_names = [
            "Controversial", 
            "Gilded", 
            "Hot", 
            "New"]

        self._access = [
            self._downvoted, 
            self._gildings, 
            self._hidden, 
            self._saved]
        self._access_names = [
            "Downvoted", 
            "Gildings", 
            "Hidden", 
            "Saved"]
```

`self._mutts` and `self._mutt_names` are not in alphabetical order. This is okay if you need to define sets of variables that are similar. In this case it would be the four lists defined at the very end of this `init` method.

## URS Code

### Classes

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
        ...

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

### Modularizing Code

The block of code above is also another great representation of how sections of code should be organized.

Within `write()`, `_determine_export()` is called first, followed by `_print_confirm()`. The order in which smaller methods that will be called in a class's "main" method should be sorted by execution order (from top to bottom). These smaller methods will also be placed above the "main" method.

### The `@staticmethod` Decorator

Use the `@staticmethod` decorator if you are defining methods in a class that does not have an `__init__()` method.

This is the class taken from `DirInit.py`:

```python
class InitializeDirectory():
    """
    ...
    """
    
    Does not include an __init__() method, therefore a @staticmethod decorator is necessary.
          |
          |
          v
    @staticmethod
    def make_directory():
        ...
```

`Logger.py` is another good example since none of the classes include an `__init__()` method.

## Unit Testing Code

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
