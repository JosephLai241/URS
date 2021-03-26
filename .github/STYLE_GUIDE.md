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

Take a look at this `redditor_item` variable that is set by a [ternary operator](https://book.pythontips.com/en/latest/ternary_operators.html):

```python
redditor_item = Objectify().make_submission(item) if isinstance(item, praw.models.Submission) else Objectify().make_comment(item)
```

This line greatly exceeds the 80 character count. In cases like these, wrap the line like so:

```python
redditor_item = Objectify().make_submission(item) \
    if isinstance(item, praw.models.Submission) \
    else Objectify().make_comment(item)
```

String formatting can take up as much length as needed. Splitting this up will make the code less readable, which is not what we are trying to accomplish here. This line exceeds the 80 character count, but that is fine because there is string formatting:

```python
logging.info("Searching and scraping r/%s for posts containing '%s'..." % (subreddit_name, each_setting[1]))
```

## Whitespace

All commas should be followed by a space. This includes method parameters:

```python
def example_method(self, a_first_param, b_second_param, c_third_param):
```

There should be a space preceeding and following all equal signs or conditionals, comparison operators, etc.:

```python
boolean == True
example = "something"
something = one_thing if a_condition != None else another_thing
```

Each item in a list should be on its own line. The closing bracket should be at the same indent as the variable:

```python
interaction_titles = [ 
    "comments", 
    "controversial", 
    "downvoted", 
    "gilded", 
    "gildings", 
    "hidden", 
    "hot", 
    "moderated",
    "multireddits",
    "new", 
    "saved",
    "submissions", 
    "top", 
    "upvoted", 
]
```

Long dictionaries can be hard to read on just one line, so you will split each key, value onto its own line. Each value for a key should be preceeded with a space. Note the previous rule for lists still applies. The closing bracket is at the same indent as the key:

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
        "here"
    ]
}
```

All variables should be grouped by relevance, sorted in alphabetical order, and separated by a new line. This applies to global, instance, and method variables.

```python
first_list = [
    ...
]
second_list = [
    ...
]
```

Methods and classes are separated by a new line:

```python
def first_method_here():
    """
    First method here.
    """
    
    pass

def second_method_here():
    """
    Second method here.
    """
    
    pass
```

Class methods following the class comment will be preceeded by a new line.

```python
class FirstClass():
    """
    The first class.
    """

    def _a_private_method_here(self):
        """
        A private method here.
        """
    
        pass

    def a_second_public_method_here(self):
        """
        A second public method here.
        """

        pass

class SecondClass():
    """
    Second class here.
    """

    def another_public_method_here(self):
        """
        Another public method here.
        """

        pass
```

## Comments

***Every single class and method requires at least one comment with proper grammar and punctuation***. By doing this, I will easily be able to tell which class most likely contains the method I am looking for. Comments should also follow the ~80 character word wrap rule.

### Class Comments

Class comments should use blocks placed underneath the class:

```python
class ThisIsAnExampleClass():
    """
    This is an example of a class comment.
    """
```

### Method Comments

Method comments should more or less follow the Numpy/Scipy docstring syntax and written below the method.

```python
    def this_is_an_example_public_method(self):
        """
        This is an example of a method comment here.
        """

        ... code starts here
```

There should be a newline following the closing triple quotes.

Additional information should be added if the method:

* Takes in parameters
* Raises exceptions
* Returns something

This is the method comment taken from `GetPath.get_scrape_type()` found in `PrepData.py`:

```python
    def get_scrape_type(file):
        """
        Get the name of the scrape-specific directory in which the data is stored.

        Parameters
        ----------
        file: str
            String denoting the filepath

        Exceptions
        ----------
        TypeError:
            Raised if the file is not JSON or if the file resides in the `analytics` directory 

        Returns
        -------
        scrape_dir: str
            String denoting the scrape-specific directory
        """

        ... code starts here
```

Include the variable name and type for parameters or return values. You only have to include the exception name for exceptions. Enter a new line, tab in, then write a short description as to what the item is or why the exception would be raised.

If the method calls previously defined private or public methods, or methods from external modules, be sure to list them at the top of the method comment.

This is an example taken from `RunRedditor.run()` found in `Redditor.py`:

```python
def run(args, parser, reddit):
    """
    Get, sort, then write scraped Redditor information to CSV or JSON.

    Calls a previously defined public method:

        Write.write()

    Calls public methods from external modules: 

        GetPRAWScrapeSettings().create_list()
        Validation.validate()
        Global.make_none_dict()
        GetPRAWScrapeSettings().get_settings()

    Parameters
    ----------
    args: Namespace
        Namespace object containing all arguments that were defined in the CLI 
    parser: ArgumentParser
        argparse ArgumentParser object
    reddit: Reddit object
        Reddit instance created by PRAW API credentials

    Returns
    -------
    u_master: dict
        Dictionary containing all Redditor scrape settings
    """
```

Notice how I have included the `Returns` section in the comment even though it returns nothing. Include `Returns` any time the method takes parameters. You do not need to include the additional sections if the method does not take parameters, raise exceptions, or return values. Simply write a short description as to what it does.

### Describing a Piece of Code

Comments describing what is happening in a piece of code should use `###` before the comment and placed above the code you are describing. Split the comment into a new line if it exceeds the ~80 character ruler in your IDE.

If you are describing why multiple conditionals are triggered, place the comment above the conditional. This is a modified version of `PrepRedditor.prep_redditor()`, also found in `PrepData.py`.

```python
def prep_redditor(data, file):
    """
    Method comment here...
    """

    plt_dict = dict()

    for interactions in data["interactions"].values():
        for obj in interactions:
            ### Indicates there is valid data in this field.
            if isinstance(obj, dict):
                if obj["type"] == "submission":
                    CleanData.count_words("selftext", obj, plt_dict)
                    CleanData.count_words("title", obj, plt_dict)
                elif obj["type"] == "comment":
                    CleanData.count_words("body", obj, plt_dict)
            ### Indicates this field is forbidden.
            elif isinstance(obj, str):
                continue
```

New maintainers would most likely be confused as to why I am type-checking the objects within the interactions list, which is why I have included the comments above the conditionals. 

### Global Variable Comments

Global variables and functions should use `###` before the comment and placed above the variable.

```python
### An example of a global comment.
an_example_list = [
    "subreddit", 
    "redditor", 
    "submissions"
]
```

An example taken from my code would be calling the Colorama `init` function at the top of many scripts:

```python
### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)
```

## Imports

**Do not use relative imports.**

All imports have to be listed at the top of each script two newlines below the header docstring block. This is an example from `Tools.py`.

Imports should be grouped together based on relevance. Each group is sorted in alphabetical order.

Standard library and third-party imports are listed first, then URS package imports. These imports should be separated by a new line.

Imports using the `import` form come before imports using the `from` form. These imports should also be separated by a new line.

Additionally, multiple imports should be on its own line. Lowercase imports are listed before uppercase imports. Each are sorted by alphabetical order. 

Here is an example of a group of imports from `Redditor.py`.

```python
"""
Redditor scraper
================
Defining methods for the Redditor scraper.
"""


import logging <------ Two newlines under the docstring block.
import praw

from colorama import (
    init,  <----------------- Lowercase imports come first
    Fore, 
    Style <----------------- Alphabetical order
)
from halo import Halo
from prawcore import PrawcoreException
                    <----------------- Newline separating relevance
from urs.praw_scrapers.utils.Validation import Validation
                    <----------------- Newline separating relevance
from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import (
    Export,
    NameFile <----------------- Alphabetical order
)
from urs.utils.Global import (
    convert_time,
    make_none_dict,
    Status <----------------- Alphabetical order, uppercase also comes last
)
from urs.utils.Logger import (
    LogError,
    LogExport, 
    LogPRAWScraper <----------------- Alphabetical order
)
from urs.utils.Titles import PRAWTitles
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
    def __init__(self, limit, redditor, skeleton):
        self._skeleton = skeleton

        self._comments = redditor.comments.new(limit = limit)
        self._controversial = redditor.controversial(limit = limit)
        self._downvoted = redditor.downvoted(limit = limit)
        self._gilded = redditor.gilded(limit = limit)
        self._gildings = redditor.gildings(limit = limit)
        self._hidden = redditor.hidden(limit = limit)
        self._hot = redditor.hot(limit = limit)
        self._moderated = redditor.moderated()
        self._multireddits = redditor.multireddits()
        self._new = redditor.new(limit = limit)
        self._saved = redditor.saved(limit = limit)
        self._submissions = redditor.submissions.new(limit = limit)
        self._top = redditor.top(limit = limit)
        self._upvoted = redditor.upvoted(limit = limit)
```

## URS Code

### Classes

Every method in URS has to be wrapped in a class. These classes contain methods that are sorted by relevance. 

Showing an example would be the best way to describe how the code is structured:

```python
class Something():
    """
    Class comment here...
    """

    def __init__(self):
        ...

    def _first_call(self, something):
        ...

    def _second_call(self, another_thing):
        ...

    def final_call(self, a_third_thing):
        ...
        calls self._first_call()
        then calls self._second_call()
```

Python does not have true "private" methods or variables, but we can indicate that they are only supposed to be called within the class by prepending an underscore in front of the method or variable name. 

`final_call()` is called outside of the `Something` class, which is why an underscore is not prepended. `_first_call()` and `_second_call()` are called by `final_call()` but are not called outside the function, hence why they are prepended with an underscore.

### Modularizing Code

The block of code above is also another great representation of how sections of code should be organized.

Within `final_call()`, `_first_call()` is called first, followed by `_second_call()`. The order in which smaller methods that will be called in a class's "main" method should be sorted by execution order (from top to bottom). These smaller methods will also be placed above the "main" method.

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

`_list_switch()` is a method found in `Cli.py` within the `GetScrapeSettings` class:

```python
class GetScrapeSettings():
    """
    Methods for creating data structures to store scrape settings.
    """
    
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
