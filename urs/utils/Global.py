"""
Global variables
================
Variables, functions, and classes that are used throughout this program.
"""


import datetime as dt
from typing import Any, Dict, List, Union

from halo import Halo

# Get current date.
date = dt.datetime.now().strftime("%Y-%m-%d")

# Subreddit categories.
categories = ["Hot", "New", "Controversial", "Top", "Rising", "Search"]
short_cat = [cat[0] for cat in categories]


def convert_time(raw_timestamp: float) -> str:
    """
    Convert UNIX time to readable format.

    :param float raw_timestamp: A UNIX timestamp.

    :returns: The timestamp converted into a readable format.
    :rtype: `str`
    """

    return dt.datetime.fromtimestamp(raw_timestamp).strftime("%Y-%m-%d %H:%M:%S")


def confirm_settings() -> Union[str, None]:
    """
    Confirm scraping options.

    :raises ValueError: Raised if the confirmation input is invalid.

    :returns: A `str` denoting whether to confirm settings and continue scraping,
        or `None` if the operation is cancelled.
    :rtype: `str | None`
    """

    options = ["y", "n"]

    while True:
        try:
            confirm = input("\nConfirm options? [Y/N] ").strip().lower()

            if confirm == options[0]:
                return confirm
            elif confirm == options[1]:
                break
            elif confirm not in options:
                raise ValueError
        except ValueError:
            print("Not an option! Try again.")


def make_list_dict(keys: List[str]) -> Dict[str, List[Any]]:
    """
    Initialize a dictionary of keys with empty lists as values.

    :param list[str] keys: A `list[str]` of keys used to initialize a dictionary.

    :returns: A `dict[str, list[any]]` initialized with the keys in the `keys`
        `list[str]` and empty arrays as its values.
    """

    return dict((key, []) for key in keys)


def make_none_dict(keys: List[str]) -> Dict[str, None]:
    """
    Initialize a dictionary of keys with `None` as values.

    :param list[str] keys: A `list[str]` of keys used to initialize a dictionary.

    :returns: A `dict[str, list[any]]` initialized with the keys in the `keys`
        `list[str]` and `None` as its values.
    """

    return dict((key, None) for key in keys)


class Status:
    """
    Methods for defining status spinners.
    """

    def __init__(self, after_message: str, before_message: str, color: str) -> None:
        """
        Initialize variables used in later methods:

            self._after_message: success message
            self._before_message: status message
            self._color: the color of the spinner

            self._spinner: Halo instance

        :param str after_message: The success message to display.
        :param str before_message: The status message to display.
        :param str color: The spinner's color.
        """

        self._after_message = after_message
        self._before_message = before_message
        self._color = color

        self.spinner = Halo(color=self._color, text=self._before_message)

    def start(self) -> None:
        """
        Start the spinner.
        """

        self.spinner.start()

    def succeed(self) -> None:
        """
        Display the success spinner message.
        """

        self.spinner.succeed(self._after_message)
