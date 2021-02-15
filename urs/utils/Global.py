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
    "chart",
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

### Convert UNIX time to readable format.
def convert_time(object):
    return dt.datetime.fromtimestamp(object).strftime("%m-%d-%Y %H:%M:%S")

### Initialize a dictionary of keys with empty lists as values.
def make_list_dict(item):
    return dict((obj, []) for obj in item)

### Initialize a dictionary of keys with None as values.
def make_none_dict(item):
    return dict((obj, None) for obj in item)
