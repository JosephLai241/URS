"""
Global variables
================
Variables, functions, and classes that are used throughout this program.
"""


import datetime as dt

from halo import Halo

### Get current date.
date = dt.datetime.now().strftime("%m-%d-%Y")

### Subreddit categories.
categories = [
    "Hot", 
    "New", 
    "Controversial", 
    "Top", 
    "Rising", 
    "Search"
]
short_cat = [cat[0] for cat in categories]

def convert_time(object):
    """
    Convert UNIX time to readable format.

    Parameters
    ----------
    object: UNIX timestamp
        UNIX timestamp returned from PRAW

    Returns
    -------
    converted_date: datetime object
        UNIX timestamp in readable format
    """

    return dt.datetime.fromtimestamp(object).strftime("%m-%d-%Y %H:%M:%S")

def confirm_settings():
        """
        Confirm scraping options.

        Parameters
        ----------
        None

        Exceptions
        ----------
        ValueError:
            Raised if the confirmation input is invalid

        Returns
        -------
        confirm: str
            String denoting whether to confirm settings and continue scraping
        """

        options = [
            "y", 
            "n"
        ]

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

def make_list_dict(item):
    """
    Initialize a dictionary of keys with empty lists as values.

    Parameters
    ----------
    item: list
        List of titles used to initialize a dictionary

    Returns
    -------
    list_dict: dict
        Dictionary initialized with objects in `item` list as keys and empty arrays
        as its values
    """

    return dict((obj, []) for obj in item)

def make_none_dict(item):
    """
    Initialize a dictionary of keys with None as values.

    Parameters
    ----------
    item: list
        List of titles used to initialize a dictionary

    Returns
    -------
    list_dict: dict
        Dictionary initialized with objects in `item` list as keys and `None` as
        its values
    """

    return dict((obj, None) for obj in item)

class Status():
    """
    Methods for defining status spinners.
    """

    def __init__(self, after_message, before_message, color):
        """
        Initialize variables used in later methods:

            self._after_message: success message
            self._before_message: status message
            self._color: the color of the spinner

            self._spinner: Halo instance

        Parameters
        ----------
        after_message: str
            String denoting the success message
        before_message: str
            String denoting the status message
        color: str
            String denoting the spinner's color

        Returns
        -------
        None
        """

        self._after_message = after_message
        self._before_message = before_message
        self._color = color

        self.spinner = Halo(color = self._color, text = self._before_message)

    def start(self):
        """
        Start the spinner.
        """

        self.spinner.start()

    def succeed(self):
        """
        Display the success spinner message.
        """

        self.spinner.succeed(self._after_message)
