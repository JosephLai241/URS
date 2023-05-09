"""
CLI Pydantic Validator
======================
Contains a Pydantic model for validating and standardizing CLI arguments.
"""

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, validator
from taisun.utils import is_valid_file

from urs.cli.validators.analytical_tools import (
    WordcloudExportFormats,
    WordcloudSettings,
)
from urs.cli.validators.comments import CommentsSettings
from urs.cli.validators.redditor import RedditorSettings
from urs.cli.validators.subreddit import (
    SubredditCategories,
    SubredditSettings,
    SubredditTimeFilters,
)
from urs.utils.Global import date


class URSScrapeSettings(BaseModel):
    """
    A `Pydantic` Model containing all scrape settings for `URS`.
    """

    # Display information flags.
    check: bool = False
    examples: bool = False
    versions: bool = False

    # PRAW scraper flags. The `Optional[List[List[Any]]]` attributes hold the raw
    # CLI settings.
    basic: bool = False
    comments: Optional[List[List[Any]]] = None
    redditor: Optional[List[List[Any]]] = None
    subreddit: Optional[List[List[Any]]] = None

    # PRAW scraping options. These attributes contain the finalized scraping settings
    # once the validators have been run.
    comments_settings: List[CommentsSettings] = []
    redditor_settings: List[RedditorSettings] = []
    subreddit_settings: List[SubredditSettings] = []

    # PRAW livestreaming flags.
    live_redditor: Optional[str] = None
    live_subreddit: Optional[str] = None

    # Analytical tool flags.
    frequencies: Optional[List[List[str]]] = None
    wordcloud: Optional[List[List[str]]] = None

    # Analytical tool settings. These attributes contain the finalized analytical
    # settings once the validators have been run.
    wordcloud_settings: List[WordcloudSettings] = []

    # Additional Subreddit scraping options.
    rules: bool = False

    # Additional submission comments scraping options.
    raw: bool = False

    # Additional livestreaming options.
    stream_submissions: bool = False

    # Utilities flags.
    tree: Optional[str] = date

    # Export options.
    csv: bool = False
    nosave: bool = False

    # Confirmation options.
    y: bool = False

    @validator("comments", pre=True, always=True)
    def validate_comments_scraping_options(
        cls: "URSScrapeSettings", values: List[List[Any]]
    ) -> List[List[Any]]:
        """
        Validate submission comments scraping options.

        :param URSScrapeSettings cls: The `URSScrapeSettings` Pydantic model.
        :param List[List[Any]] values: The comments scraping options.

        :returns: The cleaned `List[List[Any]]` containing comments scraping options.
        :rtype: `List[List[Any]]`
        """

        if values:
            for comments_settings in values:
                if len(comments_settings) > 2 or not len(comments_settings):
                    raise ValueError(
                        "Comments scraping accepts up to two positional arguments!"
                    )
                elif len(comments_settings) == 1:
                    comments_settings.append("all")
                elif len(comments_settings) == 2:
                    try:
                        comments_settings[1] = int(comments_settings[1])
                    except ValueError:
                        raise ValueError(
                            "Comments scraping requires a number (denoting the number of comments returned) for the second positional argument!"
                        )

        return values

    @validator("comments_settings", pre=True, always=True)
    def set_comments_settings(
        cls: "URSScrapeSettings", _value: List[CommentsSettings], values: Dict[str, Any]
    ) -> List[CommentsSettings]:
        """
        Set the `comments_settings` field in the `URSScrapeSettings`.

        :param List[CommentsSettings] _value: The `List[CommentsSettings]` of the
            `URSScrapeSettings` model.
        :param Dict[str, Any] values: All values within the `URSScrapeSettings`
            model.

        :returns: A `List[CommentsSettings]` of finalized scrape settings.
        :rtype: `List[CommentsSettings]`
        """

        comments_settings_list: Any = values.get("comments")

        settings_list = []
        for settings in comments_settings_list:
            if settings[1] == "all":
                settings_list.append(
                    CommentsSettings(url=settings[0], scrape_all=True, n_results=None)
                )
            else:
                settings_list.append(
                    CommentsSettings(
                        url=settings[0], scrape_all=False, n_results=settings[1]
                    )
                )

        return settings_list

    @validator("redditor", pre=True, always=True)
    def validate_redditor_scraping_options(
        cls: "URSScrapeSettings", values: List[List[Any]]
    ) -> List[List[Any]]:
        """
        Validate Redditor scraping options.

        :param URSScrapeSettings cls: The `URSScrapeSettings` Pydantic model.
        :param List[List[Any]] values: The Redditor scraping options.

        :returns: The cleaned `List[List[Any]]` containing Redditor scraping options.
        :rtype: `List[List[Any]]`
        """

        if values:
            for redditor_settings in values:
                if len(redditor_settings) != 2:
                    raise ValueError(
                        "Redditor scraping accepts two positional arguments!"
                    )

                try:
                    redditor_settings[1] = int(redditor_settings[1])
                except ValueError:
                    raise ValueError(
                        "Redditor scraping requires a number (denoting the number of results returned) for the second positional argument!"
                    )

        return values

    @validator("redditor_settings", pre=True, always=True)
    def set_redditor_settings(
        cls: "URSScrapeSettings", _value: List[RedditorSettings], values: Dict[str, Any]
    ) -> List[RedditorSettings]:
        """
        Set the `redditor_settings` field in the `URSScrapeSettings`.

        :param List[RedditorSettings] _value: The `List[RedditorSettings]` of the
            `URSScrapeSettings` model.
        :param Dict[str, Any] values: All values within the `URSScrapeSettings`
            model.

        :returns: A `List[RedditorSettings]` of finalized scrape settings.
        :rtype: `List[RedditorSettings]`
        """

        redditor_settings_list: Any = values.get("redditor")

        return [
            RedditorSettings(redditor=settings[0], n_results=settings[1])
            for settings in redditor_settings_list
        ]

    @validator("subreddit", pre=True, always=True)
    def validate_subreddit_scraping_options(
        cls: "URSScrapeSettings", values: List[List[Any]]
    ) -> List[List[Any]]:
        """
        Validate Subreddit scraping options.

        :param URSScrapeSettings cls: The `URSScrapeSettings` Pydantic model.
        :param List[List[Any]] values: The Subreddit scraping options.

        :returns: The cleaned `List[List[Any]]` containing Subreddit scraping options.
        :rtype: `List[List[Any]]`
        """

        if values:
            for subreddit_settings in values:
                if len(subreddit_settings) not in (3, 4):
                    raise ValueError(
                        "Subreddit scraping accepts three or four positional arguments!"
                    )
                elif subreddit_settings[1] not in SubredditCategories.list():
                    raise ValueError(
                        f"Subreddit category must be one of the following: {SubredditCategories.list()}"
                    )

                if len(subreddit_settings) == 4:
                    if subreddit_settings[1] not in (
                        SubredditCategories.CONTROVERSIAL,
                        SubredditCategories.SEARCH,
                        SubredditCategories.TOP,
                    ):
                        raise ValueError(
                            "Time filters may only be applied to the following categories: ['c', 's', 't']"
                        )
                    elif subreddit_settings[3] not in SubredditTimeFilters.list():
                        raise ValueError(
                            f"Invalid time filter! Choose one of the following time filters: {SubredditTimeFilters.list()}"
                        )

                if len(subreddit_settings) == 3 and subreddit_settings[1] in (
                    SubredditCategories.CONTROVERSIAL,
                    SubredditCategories.SEARCH,
                    SubredditCategories.TOP,
                ):
                    subreddit_settings.append(SubredditTimeFilters.ALL)

                if subreddit_settings[1] != SubredditCategories.SEARCH:
                    try:
                        subreddit_settings[2] = int(subreddit_settings[2])
                    except ValueError:
                        raise ValueError(
                            "Subreddit scraping requires a number (denoting the number of results returned) for the third positional argument!"
                        )

        return values

    @validator("subreddit_settings", pre=True, always=True)
    def set_subreddit_settings(
        cls: "URSScrapeSettings",
        _value: List[SubredditSettings],
        values: Dict[str, Any],
    ) -> List[SubredditSettings]:
        """
        Set the `subreddit_settings` field in the `URSScrapeSettings`.

        :param List[SubredditSettings] _value: The `List[SubredditSettings]` of the
            `URSScrapeSettings` model.
        :param Dict[str, Any] values: All values within the `URSScrapeSettings`
            model.

        :returns: A `List[SubredditSettings]` of finalized scrape settings.
        :rtype: `List[SubredditSettings]`
        """

        subreddit_settings_list: Any = values.get("subreddit")

        settings_list = []
        for settings in subreddit_settings_list:
            if len(settings) == 3:
                settings_list.append(
                    SubredditSettings(
                        subreddit=settings[0],
                        category=settings[1],
                        n_results_or_keywords=settings[2],
                        time_filter=None,
                    )
                )
            else:
                settings_list.append(
                    SubredditSettings(
                        subreddit=settings[0],
                        category=settings[1],
                        n_results_or_keywords=settings[2],
                        time_filter=settings[3],
                    )
                )

        return settings_list

    @validator("frequencies", pre=True, always=True)
    def validate_frequencies_settings(
        cls: "URSScrapeSettings", values: List[List[str]]
    ) -> List[List[str]]:
        """
        Validate frequencies generation settings.

        :param URSScrapeSettings cls: The `URSScrapeSettings` Pydantic model.
        :param List[List[Any]] values: The frequencies generation options.

        :returns: A `List[List[Any]]` containing frequencies generation options.
        :rtype: `List[List[Any]]`
        """

        if values:
            for frequencies_settings in values:
                if len(frequencies_settings) != 1:
                    raise ValueError(
                        "Frequencies only accepts one positional argument!"
                    )
                elif not is_valid_file(frequencies_settings[0]):
                    raise ValueError(
                        "Frequencies requires a valid filepath for the first positional argument!"
                    )

        return values

    @validator("wordcloud", pre=True, always=True)
    def validate_wordcloud_settings(
        cls: "URSScrapeSettings", values: List[List[str]]
    ) -> List[List[str]]:
        """
        Validate wordcloud generation settings.

        :param URSScrapeSettings cls: The `URSScrapeSettings` Pydantic model.
        :param List[List[Any]] values: The wordcloud generation options.

        :returns: A `List[List[Any]]` containing wordcloud generation options.
        :rtype: `List[List[Any]]`
        """

        if values:
            for wordcloud_settings in values:
                if not is_valid_file(wordcloud_settings[0]):
                    raise ValueError(
                        "The wordcloud requires a valid filepath for the first positional argument!"
                    )
                elif len(wordcloud_settings) == 1:
                    wordcloud_settings.append(WordcloudExportFormats.PNG.value)
                elif (
                    len(wordcloud_settings) == 2
                    and wordcloud_settings[1] not in WordcloudExportFormats.list()
                ):
                    raise ValueError(
                        f"Invalid wordcloud export format! Accepts one of the following values: {WordcloudExportFormats.list()}"
                    )

        return values

    @validator("wordcloud_settings", pre=True, always=True)
    def set_wordcloud_settings(
        cls: "URSScrapeSettings",
        _value: List[WordcloudSettings],
        values: Dict[str, Any],
    ) -> List[WordcloudSettings]:
        """
        Set the `wordcloud_settings` field in the `URSScrapeSettings`.

        :param List[WordcloudSettings] _value: The `List[WordcloudSettings]` of the
            `URSScrapeSettings` model.
        :param Dict[str, Any] values: All values within the `URSScrapeSettings`
            model.

        :returns: A `List[WordcloudSettings]` of finalized scrape settings.
        :rtype: `List[WordcloudSettings]`
        """

        wordcloud_settings_list: Any = values.get("wordcloud")

        return [
            WordcloudSettings(export_format=settings[1], file=settings[0])
            for settings in wordcloud_settings_list
        ]

    @validator("tree")
    def validate_tree_date(cls: "URSScrapeSettings", value: str) -> str:
        """
        Validate the date provided if applicable.

        :param URSScrapeSettings cls: The `URSScrapeSettings` Pydantic model.
        :param str value: The date to validate.

        :returns: A `str` denoting the validated date.
        :rtype: `str`
        """

        if value:
            date_regex = re.compile(r"^\d{4}[-/]\d{2}[-/]\d{2}$")

            if not date_regex.match(value):
                raise ValueError(
                    "Invalid date format! Accepts one of the following formats: [`YYYY-MM-DD`, `YYYY/MM/DD`]"
                )

        return value
