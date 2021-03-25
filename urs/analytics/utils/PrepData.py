"""
Preparing data for analytical tools
===================================
Helper methods to prepare data for frequencies and wordcloud generators.
"""


import json

from halo import Halo

from urs.utils.Global import Status
from urs.utils.Logger import LogAnalyticsErrors

class GetPath():
    """
    Methods for determining file paths.
    """

    @staticmethod
    @LogAnalyticsErrors.log_invalid_top_dir
    def get_scrape_type(file):
        """
        Get the name of the scrape-specific directory in which the data is stored.

        Parameters
        ----------
        file: str
            String denoting the filepath

        Exceptions
        ----------
        TypeError:
            Raised if the file is not JSON or if the file resides in the `analytics`
            directory 

        Returns
        -------
        scrape_dir: str
            String denoting the scrape-specific directory
        """

        if file.split("/")[-1].split(".")[-1] != "json" \
        or file.split("/")[file.split("/").index("scrapes") + 2] == "analytics":
            raise TypeError
        
        return file.split("/")[file.split("/").index("scrapes") + 2]

    @staticmethod
    def name_file(export_option, path, tool_type):
        """
        Name the chart or wordcloud when saving to file.

        Parameters
        ----------
        export_option: str
            String denoting the file format when exporting files
        path: str
            String denoting the full filepath
        tool_type: str
            String denoting the type of analytical tool

        Returns
        -------
        date_dir: str
            String denoting the date directory
        new_path: str
            String denoting the new filepath to save file
        """

        split_path = path.split("/")
        date_dir = split_path[split_path.index("scrapes") + 1]
        split_path[split_path.index("scrapes") + 2] = "analytics/%s" % tool_type

        split_file = split_path[-1].split(".")
        split_file[-1] = export_option
        split_path[-1] = ".".join(split_file)
        
        return date_dir, "/".join(split_path)

class Extract():
    """
    Methods for extracting the data from scrape files.
    """

    @staticmethod
    def extract(file):
        """
        Extract data from the file.

        Parameters
        ----------
        file: str
            String denoting the filepath

        Returns
        -------
        data: dict
            Dictionary containing extracted scrape data
        """

        with open(str(file), "r", encoding = "utf-8") as raw_data:
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
    def prep_subreddit(data, file):
        """
        Prepare Subreddit data.

        Calls previously defined public method:

            CleanData.count_words()

        Parameters
        ----------
        data: dict
            Dictionary containing extracted scrape data
        file: str
            String denoting the filepath

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
        return dict(sorted(plt_dict.items(), key = lambda item: item[1], reverse = True))

class PrepRedditor():
    """
    Methods for preparing Redditor data.
    """

    @staticmethod
    def prep_redditor(data, file):
        """
        Prepare Redditor data.

        Calls previously defined public method:

            CleanData.count_words()

        Parameters
        ----------
        data: dict
            Dictionary containing extracted scrape data
        file: str
            String denoting the filepath

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
            for obj in interactions:
                ### Indicates there is valid data in this field.
                if isinstance(obj, dict):
                    if obj["type"] == "submission":
                        CleanData.count_words("selftext", obj, plt_dict)
                        CleanData.count_words("title", obj, plt_dict)
                    elif obj["type"] == "comment":
                        CleanData.count_words("body", obj, plt_dict)
                ### Indicates this field is forbidden.
                elif isinstance(obj, str):
                    continue

        status.succeed()
        return dict(sorted(plt_dict.items(), key = lambda item: item[1], reverse = True))

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
    def prep_comments(data, file):
        """
        Prepare submission comments data.

        Calls previously defined private methods:

            PrepComments._prep_raw()
            PrepComments._prep_structured()

        Parameters
        ----------
        data: dict
            Dictionary containing extracted scrape data
        file: str
            String denoting the filepath

        Returns
        -------
        frequencies: dict
            Dictionary containing finalized word frequencies
        """

        plt_dict = dict()

        PrepComments._prep_raw(data["data"]["comments"], plt_dict) \
            if data["scrape_settings"]["style"] == "raw" \
            else PrepComments._prep_structured(data["data"]["comments"], plt_dict)

        return dict(sorted(plt_dict.items(), key = lambda item: item[1], reverse = True))

class PrepData():
    """
    Calling all methods for preparing scraped data. 
    """

    @staticmethod
    def prep(file, scrape_type):
        """
        Combine all prep methods into one public method.

        Calls previously defined public methods:

            PrepSubreddit.prep_subreddit()
            PrepSubreddit.prep_redditor()
            PrepSubreddit.prep_comments()

        Parameters
        ----------
        file: str
            String denoting the filepath
        scrape_type: str
            String denoting the scrape type 

        Returns
        -------
        frequency_data: dict
            Dictionary containing extracted scrape data
        """

        data = Extract.extract(file)

        if scrape_type == "subreddits":
            return PrepSubreddit.prep_subreddit(data["data"], file)
        elif scrape_type == "redditors":
            return PrepRedditor.prep_redditor(data["data"], file)
        elif scrape_type == "comments":
            return PrepComments.prep_comments(data, file)
    