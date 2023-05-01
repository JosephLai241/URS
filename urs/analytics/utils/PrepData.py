"""
Preparing data for analytical tools
===================================
Helper methods to prepare data for frequencies and wordcloud generators.
"""


import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Global import Status
from urs.utils.Logger import LogAnalyticsErrors


class GetPath:
    """
    Methods for determining file paths.
    """

    @staticmethod
    @LogAnalyticsErrors.log_invalid_top_dir
    def get_scrape_type(scrape_file: str, tool: str) -> Tuple[str, str]:
        """
        Get the name of the scrape-specific directory in which the data is stored
        and create the directories within the `analytics` folder.

        :param str scrape_file: The filepath to the scrape file.
        :param str tool: The name of the tool that was run.

        :raises TypeError: Raised if the file is not JSON or if the file resides
            in the `analytics` directory.

        :returns: The path to the analytics directory and the scrape directory.
        :rtype: `(str, str)`
        """

        file_path = Path(scrape_file)
        scrape_dir = list(file_path.parts)[file_path.parts.index("scrapes") + 2]

        if file_path.name.split(".")[1] != "json" or scrape_dir == "analytics":
            raise TypeError

        split_analytics_dir = (
            list(file_path.parts)[: file_path.parts.index("scrapes") + 2]
            + ["analytics", tool]
            + list(file_path.parts)[file_path.parts.index("scrapes") + 2 : -1]
        )

        analytics_dir = "/".join(split_analytics_dir)
        InitializeDirectory.create_dirs(analytics_dir)

        return analytics_dir, scrape_dir

    @staticmethod
    def name_file(analytics_dir: str, path: str) -> str:
        """
        Name the frequencies data or wordcloud when saving to file.

        :param str analytics_dir: The path to the directory in which the analytical
            data will be written.
        :param str path: The full filepath.

        :returns: The new filepath to save the file.
        :rtype: `str`
        """

        return f"{Path(analytics_dir)}/{Path(path).name}"


class Extract:
    """
    Methods for extracting the data from scrape files.
    """

    @staticmethod
    def extract(scrape_file: str) -> Dict[str, Any]:
        """
        Extract data from the file.

        :param str scrape_file: The filepath.

        :returns: A `dict` containing extracted scrape data.
        :rtype: `dict[str, Any]`
        """

        with open(str(scrape_file), "r", encoding="utf-8") as raw_data:
            return json.load(raw_data)


class CleanData:
    """
    Methods for cleaning words found in "title", "body" or "text" fields.
    """

    @staticmethod
    def _remove_extras(word: str) -> str:
        """
        Removing unnecessary characters from words.

        :param str word: The word to clean.

        :returns: The cleaned word.
        :rtype: `str`
        """

        illegal_chars = [char for char in "[(),:;.}{<>`]"]
        fixed = [" " if char in illegal_chars else char for char in word]

        return "".join(fixed).strip()

    @staticmethod
    def count_words(field: str, obj: Dict[str, Any], plt_dict: Dict[str, int]) -> None:
        """
        Count words that are present in a field, then update the `plt_dict` dictionary.

        :param str field: Extract data from this key in the `dict`.
        :param dict[str, Any] obj: A `dict` containing the scrape data.
        :param dict[str, int] plt_dict: A `dict` containing frequency data.
        """

        words = obj[field].split(" ")
        for word in words:
            word = CleanData._remove_extras(word)
            if not word:
                continue

            if word not in plt_dict.keys():
                plt_dict[word] = 1
            else:
                plt_dict[word] += 1


class PrepSubreddit:
    """
    Methods for preparing Subreddit data.
    """

    @staticmethod
    def prep_subreddit(data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Prepare Subreddit data.

        :param list[dict[str, Any]] data: A `list` containing scraped Subreddit data.

        :returns: A `dict` containing finalized word frequencies.
        :rtype: `dict[str, int]`
        """

        status = Status(
            "Finished Subreddit analysis.", "Analyzing Subreddit scrape.", "white"
        )

        plt_dict = dict()

        status.start()
        for submission in data:
            CleanData.count_words("selftext", submission, plt_dict)
            CleanData.count_words("title", submission, plt_dict)

        status.succeed()
        return plt_dict


class PrepMutts:
    """
    Methods for preparing data that may contain a mix of Reddit objects.
    """

    @staticmethod
    def prep_mutts(data: List[Dict[str, Any]], plt_dict: Dict[str, int]) -> None:
        """
        Prepare data that may contain a mix of Reddit objects.

        :param list[dict[str, Any]] data: A `list` containing Reddit objects.
        :param dict[str, int] plt_dict: A `dict` containing frequency data.
        """

        for obj in data:
            # Indicates there is valid data in this field.
            if isinstance(obj, dict):
                try:
                    if obj["type"] == "submission":
                        CleanData.count_words("selftext", obj, plt_dict)
                        CleanData.count_words("title", obj, plt_dict)
                    elif obj["type"] == "comment":
                        CleanData.count_words("body", obj, plt_dict)
                except KeyError:
                    continue
            # Indicates this field is forbidden when analyzing Redditor scrapes.
            elif isinstance(obj, str):
                continue


class PrepRedditor:
    """
    Methods for preparing Redditor data.
    """

    @staticmethod
    def prep_redditor(data: Dict[str, Any]) -> Dict[str, int]:
        """
        Prepare Redditor data.

        :param dict[str, Any] data: A `dict` containing scraped Redditor data.

        :returns: A `dict` containing finalized word frequencies.
        :rtype: `dict[str, int]`
        """

        status = Status(
            "Finished Redditor analysis.", "Analyzing Redditor scrape.", "white"
        )

        plt_dict = dict()

        status.start()
        for interactions in data["interactions"].values():
            PrepMutts.prep_mutts(interactions, plt_dict)

        status.succeed()
        return plt_dict


class PrepComments:
    """
    Methods for preparing submission comments data.
    """

    @staticmethod
    def _prep_raw(data: List[Dict[str, Any]], plt_dict: Dict[str, int]) -> None:
        """
        Prepare raw submission comments.

        :param list[dict[str, Any]] data: A `list` containing comment data.
        :param dict[str, int] plt_dict: A `dict` containing frequency data.
        """

        status = Status(
            "Finished raw submission comments analysis.",
            "Analyzing raw submission comments scrape.",
            "white",
        )

        status.start()
        for comment in data:
            CleanData.count_words("body", comment, plt_dict)

        status.succeed()

    @staticmethod
    def _prep_structured(data: List[Dict[str, Any]], plt_dict: Dict[str, int]) -> None:
        """
        An iterative implementation of depth-first search to prepare structured
        comments.

        :param list[dict[str, Any]] data: A `list` containing comment data.
        :param dict[str, int] plt_dict: A `dict` containing frequency data.
        """

        status = Status(
            "Finished structured submission comments analysis.",
            "Analyzing structured submission comments scrape.",
            "white",
        )

        status.start()
        for comment in data:
            CleanData.count_words("body", comment, plt_dict)

            stack = []
            stack.append(comment)

            visited = []
            visited.append(comment)

            while stack:
                current_comment = stack.pop(0)

                for reply in current_comment["replies"]:
                    CleanData.count_words("body", reply, plt_dict)

                    if reply not in visited:
                        stack.insert(0, reply)
                        visited.append(reply)

        status.succeed()

    @staticmethod
    def prep_comments(data: Dict[str, Any]) -> Dict[str, int]:
        """
        Prepare submission comments data.

        :param list[dict[str, Any]] data: A `list` containing Reddit objects.

        :returns: A `dict` containing finalized word frequencies.
        :rtype: `dict[str, int]`
        """

        plt_dict = dict()

        PrepComments._prep_raw(data["data"]["comments"], plt_dict) if data[
            "scrape_settings"
        ]["style"] == "raw" else PrepComments._prep_structured(
            data["data"]["comments"], plt_dict
        )

        return plt_dict


class PrepLivestream:
    """
    Methods for preparing livestream data.
    """

    @staticmethod
    def prep_livestream(data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Prepare livestream data.

        :param list[dict[str, Any]] data: A `list` containing livestream data.

        :returns: A `dict` containing finalized word frequencies.
        :rtype: `dict[str, int]`
        """

        status = Status(
            "Finished livestream analysis.", "Analyzing livestream scrape.", "white"
        )

        plt_dict = {}

        status.start()
        PrepMutts.prep_mutts(data, plt_dict)
        status.succeed()

        return plt_dict


class PrepData:
    """
    Calling all methods for preparing scraped data.
    """

    @staticmethod
    def prep(scrape_file: str, scrape_type: str) -> Dict[str, int]:
        """
        Combine all prep methods into one public method.

        :param str scrape_file: The filepath.
        :param str scrape_type: The scrape type.

        :returns: A `dict` containing finalized word frequencies.
        :rtype: `dict[str, int]`
        """

        data = Extract.extract(scrape_file)

        if scrape_type == "subreddits":
            plt_dict = PrepSubreddit.prep_subreddit(data["data"])
        elif scrape_type == "redditors":
            plt_dict = PrepRedditor.prep_redditor(data["data"])
        elif scrape_type == "comments":
            plt_dict = PrepComments.prep_comments(data)
        elif scrape_type == "livestream":
            plt_dict = PrepLivestream.prep_livestream(data["data"])

        return dict(sorted(plt_dict.items(), key=lambda item: item[1], reverse=True))
