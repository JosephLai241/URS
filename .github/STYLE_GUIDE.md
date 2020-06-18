# Table of Contents

* [URS Code](#urs-code)
* [Unit Testing Code](#unit-testing-code)

# URS Code

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
