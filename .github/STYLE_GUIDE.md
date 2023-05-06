# URS Style Guide

## Table of Contents

- [Code Formatting](#code-formatting)
  - [`Black` Formatting](#black-formatting)
  - [`isort` Formatting](#isort-formatting)
- [Docstring and Type Hint Etiquette](#docstring-and-type-hint-etiquette)
- [Unit Testing Code](#unit-testing-code)

## Code Formatting

The rules for code formatting are very simple -- **all formatting rules are delegated to [`Black`][black] and [`isort`][isort]**.

### `Black` Formatting

Use the standard formatting rules when formatting code with `Black`. Formatting code manually is a very simple command:

```
black urs/
```

### `isort` Formatting

When formatting imports with `isort`, you will have to specify the `profile` setting when running the command to allow for interoperability between code styles. In this case, you will have to tell `isort` to use the `black` profile since we are formatting everything else with `Black`. The command looks something like this:

```
isort urs/ --profile black
```

## Docstring and Type Hint Etiquette

**Every single function needs a docstring describing what the function does, its parameters, and what it returns (if applicable)**, even if the function name is self-explanatory. The docstring format used by `URS` is the reStructuredText (RST) format. See the [Real Python reStructuredText example][real python restructuredtext example] for an idea as to how it looks.

Docstrings have a max character count of 80 characters. If the function description docstring exceeds 80 characters, continue typing on a new line. If parameter, exception, or return docstrings exceed 80 characters, create a new line, tab in (4 spaces), and continue typing.

Parameters, exceptions, and return statements should be grouped together/separated by a newline. Refer to the Python codeblock below for an example.

**Every single function also requires type hints for its parameters and return type**, even if the parameter name is self-explanatory. See this [Real Python type hint tutorial][real python type hint tutorial] if you are unfamiliar with type hints.

Below is an example of a properly documented function:

```python
def add_two_numbers(first_number: int, second_number: int) -> int:
    """
    Returns the sum of two numbers.

    :param int first_number: The first number to add.
    :param int second_number: The second number to add.

    :raises ValueError: Raised if either `first_number` or `second_number` is not
        an `int`.

    :returns: The sum of two numbers
    :rtype: `int`
    """

    if not isinstance(first_number, int) or not isinstance(second_number, int):
        raise ValueError("Can only add two integers together!")

    return first_number + second_number
```

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
    Testing GetScrapeSettings class _list_switch() method.
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
Testing [ClassName] class [method_name()] method.
```

The unit test method will use the following naming convention:

```python
    def test_[underscored_method_name]_[underscored_test_case](self):
        ...
```

<!-- LINKS -->

[black]: https://black.readthedocs.io/en/stable/
[isort]: https://pycqa.github.io/isort/
[real python type hint tutorial]: https://realpython.com/lessons/type-hinting/
[real python restructuredtext example]: https://realpython.com/documenting-python-code/#restructuredtext-example
