"""
Global variables
================
Variables that are used throughout this program.
"""


import datetime as dt

### Get current date.
date = dt.datetime.now().strftime("%m-%d-%Y")

### Export options.
eo = [
    "csv", 
    "json"
]

### Confirm or deny options.
options = [
    "y", 
    "n"
]

### PRAW scrape types.
s_t = [
    "subreddit", 
    "redditor", 
    "comments"
]

### Analytical tools.
analytical_tools = [
    "frequencies",
    "wordcloud"
]

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
