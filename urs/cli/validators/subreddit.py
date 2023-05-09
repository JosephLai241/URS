"""
Subreddit Validator
===================
Contains Pydantic validation Models for Subreddit scraping.
"""

from pydantic import BaseModel

from urs.cli.utils import DebuggableEnum


class SubredditCategories(str, DebuggableEnum):
    """
    Contains all possible values for Subreddit categories.
    """

    CONTROVERSIAL = "c"
    """
    The Controversial category.
    """
    HOT = "h"
    """
    The Hot category.
    """
    NEW = "n"
    """
    The New category.
    """
    RISING = "r"
    """
    The Rising category.
    """
    SEARCH = "s"
    """
    The Search category.
    """
    TOP = "t"
    """
    The Top category.
    """


class SubredditTimeFilters(str, DebuggableEnum):
    """
    Contains all possible time filters for Subreddit scraping. These time filters
    only apply to the following categories:

    - Controversial
    - Search
    - Top
    """

    ALL = "all"
    """
    Filter by all time. This is the default time filter if no time filter is specified.
    """
    DAY = "day"
    """
    Filter by past day.
    """
    HOUR = "hour"
    """
    Filter by past hour.
    """
    MONTH = "month"
    """
    Filter by past month.
    """
    WEEK = "week"
    """
    Filter by past week.
    """
    YEAR = "year"
    """
    Filter by past year.
    """


class SubredditSettings(BaseModel):
    """
    A `Pydantic` Model containing Subreddit scrape settings.
    """

    category: SubredditCategories
    """
    The category name.
    """
    n_results_or_keywords: int | str
    """
    The number of results to return, or keywords to search for.
    """
    subreddit: str
    """
    The name of the Subreddit.
    """
    time_filter: SubredditTimeFilters | None
    """
    The time filter to apply to the results. This is set to `None` if the `category`
    is not `SubredditCategories.CONTROVERSIAL`, `SubredditCategories.SEARCH`, or
    `SubredditCategories.TOP`.
    """
