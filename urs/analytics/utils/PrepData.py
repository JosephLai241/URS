"""
Preparing data for analytical tools
===================================
Helper methods to prepare data for frequencies and wordcloud generators.
"""


import json

from pathlib import Path

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Global import Status
from urs.utils.Logger import LogAnalyticsErrors

class GetPath():
    """
    Methods for determining file paths.
    """

    @staticmethod
    @LogAnalyticsErrors.log_invalid_top_dir
    def get_scrape_type(scrape_file, tool):
        """
        Get the name of the scrape-specific directory in which the data is stored
        and create the directories within the `analytics` folder.

        Parameters
        ----------
        scrape_file: str
            String denoting the filepath
        tool: str
            String denoting the tool type

        Exceptions
        ----------
        TypeError:
            Raised if the file is not JSON or if the file resides in the `analytics`
            directory 

        Returns
        -------
        analytics_dir: str
            String denoting the path to the directory in which the analytical
            data will be written
        scrape_dir: str
            String denoting the scrape-specific directory
        """

        file_path = Path(scrape_file)
        scrape_dir = list(file_path.parts)[file_path.parts.index("scrapes") + 2]

        if file_path.name.split(".")[1] != "json" or scrape_dir == "analytics":
            raise TypeError

        split_analytics_dir = \
            list(file_path.parts)[:file_path.parts.index("scrapes") + 2] + \
            ["analytics", tool] + \
            list(file_path.parts)[file_path.parts.index("scrapes") + 2:-1]

        analytics_dir = "/".join(split_analytics_dir)
        InitializeDirectory.create_dirs(analytics_dir)

        return analytics_dir, scrape_dir

    @staticmethod
    def name_file(analytics_dir, path):
        """
        Name the frequencies data or wordcloud when saving to file.

        Parameters
        ----------
        analytics_dir: str
            String denoting the path to the directory in which the analytical
            data will be written
        path: str
            String denoting the full filepath

        Returns
        -------
        filename: str
            String denoting the new filepath to save file
        """

        return f"{Path(analytics_dir)}/{Path(path).name}"

class Extract():
    """
    Methods for extracting the data from scrape files.
    """

    @staticmethod
    def extract(scrape_file):
        """
        Extract data from the file.

        Parameters
        ----------
        scrape_file: str
            String denoting the filepath

        Returns
        -------
        data: dict
            Dictionary containing extracted scrape data
        """

        with open(str(scrape_file), "r", encoding = "utf-8") as raw_data:
            return json.load(raw_data)

class CleanData():
    """
    Methods for cleaning words found in "title", "body" or "text" fields.
    """

    @staticmethod
    def _remove_extras(word):
        """
        Removing unnecessary characters from words.

        Parameters
        ----------
        word: str
            String denoting the word to clean

        Returns
        -------
        cleaned_word: str
            String denoting the cleaned word
        """

        illegal_chars = [char for char in "[(),:;.}{<>`]"]
        fixed = [
            " "
                if char in illegal_chars
                else char for char in word
        ]

        return "".join(fixed).strip()

    @staticmethod
    def count_words(field, obj, plt_dict):
        """
        Count words that are present in a field, then update the plt_dict dictionary.

        Calls previously defined private method:

            CleanData._remove_extras()

        Parameters
        ----------
        field: str
            String denoting the dictionary key to extract data from
        obj: dict
            Dictionary containing scrape data
        plt_dict: dict
            Dictionary containing frequency data

        Returns
        -------
        None
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

class PrepSubreddit():
    """
    Methods for preparing Subreddit data.
    """

    @staticmethod
    def prep_subreddit(data):
        """
        Prepare Subreddit data.

        Calls previously defined public method:

            CleanData.count_words()

        Parameters
        ----------
        data: list
            List containing extracted scrape data

        Returns
        -------
        frequencies: dict
            Dictionary containing finalized word frequencies
        """

        status = Status(
            "Finished Subreddit analysis.",
            "Analyzing Subreddit scrape.",
            "white"
        )

        plt_dict = dict()

        status.start()
        for submission in data:
            CleanData.count_words("selftext", submission, plt_dict)
            CleanData.count_words("title", submission, plt_dict)

        status.succeed()
        return plt_dict

class PrepMutts():
    """
    Methods for preparing data that may contain a mix of Reddit objects.
    """

    @staticmethod
    def prep_mutts(data, plt_dict):
        """
        Prepare data that may contain a mix of Reddit objects.

        Parameters
        ----------
        data: list
            List containing Reddit objects
        plt_dict: dict
            Dictionary containing frequency data

        Returns
        -------
        None
        """

        for obj in data:
            ### Indicates there is valid data in this field.
            if isinstance(obj, dict):
                try:
                    if obj["type"] == "submission":
                        CleanData.count_words("selftext", obj, plt_dict)
                        CleanData.count_words("title", obj, plt_dict)
                    elif obj["type"] == "comment":
                        CleanData.count_words("body", obj, plt_dict)
                except KeyError:
                    continue
            ### Indicates this field is forbidden when analyzing Redditor scrapes.
            elif isinstance(obj, str):
                continue

class PrepRedditor():
    """
    Methods for preparing Redditor data.
    """

    @staticmethod
    def prep_redditor(data):
        """
        Prepare Redditor data.

        Calls previously defined public methods:

            CleanData.count_words()
            PrepMutts.prep_mutts()

        Parameters
        ----------
        data: dict
            Dictionary containing extracted scrape data

        Returns
        -------
        frequencies: dict
            Dictionary containing finalized word frequencies
        """

        status = Status(
            "Finished Redditor analysis.",
            "Analyzing Redditor scrape.",
            "white"
        )

        plt_dict = dict()

        status.start()
        for interactions in data["interactions"].values():
            PrepMutts.prep_mutts(interactions, plt_dict)

        status.succeed()
        return plt_dict

class PrepComments():
    """
    Methods for preparing submission comments data.
    """

    @staticmethod
    def _prep_raw(data, plt_dict):
        """
        Prepare raw submission comments.

        Calls previously defined public method:

            CleanData.count_words()

        Parameters
        ----------
        data: list
            List containing extracted scrape data
        plt_dict: dict
            Dictionary containing frequency data

        Returns
        -------
        None
        """

        status = Status(
            "Finished raw submission comments analysis.",
            "Analyzing raw submission comments scrape.",
            "white"
        )

        status.start()
        for comment in data:
            CleanData.count_words("body", comment, plt_dict)
        
        status.succeed()

    @staticmethod
    def _prep_structured(data, plt_dict):
        """
        An iterative implementation of depth-first search to prepare structured
        comments.

        Parameters
        ----------
        data: list
            List containing extracted scrape data
        plt_dict: dict
            Dictionary containing frequency data

        Returns
        -------
        None
        """

        status = Status(
            "Finished structured submission comments analysis.",
            "Analyzing structured submission comments scrape.",
            "white"
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
    def prep_comments(data):
        """
        Prepare submission comments data.

        Calls previously defined private methods:

            PrepComments._prep_raw()
            PrepComments._prep_structured()

        Parameters
        ----------
        data: dict
            Dictionary containing extracted scrape data

        Returns
        -------
        frequencies: dict
            Dictionary containing finalized word frequencies
        """

        plt_dict = dict()

        PrepComments._prep_raw(data["data"]["comments"], plt_dict) \
            if data["scrape_settings"]["style"] == "raw" \
            else PrepComments._prep_structured(data["data"]["comments"], plt_dict)

        return plt_dict

class PrepLivestream():
    """
    Methods for preparing livestream data.
    """

    @staticmethod
    def prep_livestream(data):
        """
        Prepare livestream data.

        Parameters
        ----------
        data: list
            List containing extracted scrape data
        """

        status = Status(
            "Finished livestream analysis.",
            "Analyzing livestream scrape.",
            "white"
        )

        plt_dict = {}

        status.start()
        PrepMutts.prep_mutts(data, plt_dict)
        status.succeed()

        return plt_dict

class PrepData():
    """
    Calling all methods for preparing scraped data. 
    """

    @staticmethod
    def prep(scrape_file, scrape_type):
        """
        Combine all prep methods into one public method.

        Calls previously defined public methods:

            PrepSubreddit.prep_subreddit()
            PrepSubreddit.prep_redditor()
            PrepSubreddit.prep_comments()

        Parameters
        ----------
        scrape_file: str
            String denoting the filepath
        scrape_type: str
            String denoting the scrape type 

        Returns
        -------
        frequency_data: dict
            Dictionary containing extracted scrape data
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

        return dict(sorted(plt_dict.items(), key = lambda item: item[1], reverse = True))
