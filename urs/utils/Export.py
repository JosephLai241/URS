"""
Exporting data
==============
Methods for naming and exporting scraped data.
"""


import csv
import json

from json import JSONEncoder

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Global import (
    categories,
    date,
    short_cat
)

class NameFile():
    """
    Methods for naming the exported files.
    """

    def __init__(self):
        """
        Initialize variables used in naming the file:

            self._illegal_chars: list denoting illegal filename characters

        Returns
        -------
        None
        """

        self._illegal_chars = [char for char in '[@!#$%^&*()<>?/"\\|}{~:+`=]']

    def _check_len(self, name):
        """
        Verify filename is not too long. Slices the name if it exceeds 50 characters.

        Parameters
        ----------
        name: str
            Original filename

        Returns
        -------
        name: str
            Sliced filename if applicable
        """

        if len(name) > 50:
            return name[0:48] + "--"

        return name

    def _fix(self, name):
        """
        Fix filename if illegal characters are present.

        Parameters
        ----------
        name: str
            Original filename

        Returns
        -------
        name: str
            Fixed filename
        """

        fixed = [
            "_" 
                if char in self._illegal_chars
                else char for char in name
        ]

        return "".join(fixed)

    def _r_category(self, cat_i, category_n):
        """
        Subreddit category name switch.

        Parameters
        ----------
        cat_i: str
            String denoting the abbreviated category
        category_n: int
            Integer denoting a dictionary key

        Returns
        -------
        category: str
            The category name
        """

        switch = {
            0: categories[5],
            1: categories[short_cat.index(cat_i)] \
                if cat_i != short_cat[5] \
                else None
        }

        return switch.get(category_n)

    def _r_get_category(self, cat_i):
        """
        Choose the Subreddit category index.

        Parameters
        ----------
        cat_i: int
            Integer denoting the full category's index

        Returns
        -------
        category_n: int
            Integer denoting the selected category's index
        """

        return 0 \
            if cat_i == short_cat[5] \
            else 1

    def _get_sub_fname(self, category, end, index, n_res_or_kwds, subreddit, time_filter):
        """
        File name switch that stores all possible Subreddit filename formats

        Parameters
        ----------
        category: str
            Full Subreddit category name
        end: str
            "result" or "results" depending on n_results
        index: int
            Integer denoting the dictionary key to return
        n_res_or_kwds: str
            n_results to return or keywords to search for
        subreddit: str
            Subreddit name
        time_filter: str
            Time filter if applicable

        Returns
        -------
        filename: str
            The filename for Subreddit scrapes
        """

        filter_str = f"-past-{time_filter}"
        search = f"{subreddit}-{category.lower()}-'{n_res_or_kwds}'"
        standard = f"{subreddit}-{category.lower()}-{n_res_or_kwds}-{end}"

        filenames = {
            0: search,
            1: standard,
            2: search + filter_str,
            3: standard + filter_str
        }

        return filenames.get(index)

    def _get_raw_n(self, args, cat_i, end, each_sub, sub):
        """
        Determine filename format for the Subreddit scraper. 
        
        Calls previously defined private methods:

            self._r_get_category()
            self._r_category()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI
        cat_i: str or int
            Either a single character or integer denoting the full category's index
            or abbreviated category
        end: str
            "results" or "result" depending on n_results
        each_sub: list
            List of Subreddit scraping settings
        sub: str
            Subreddit name

        Returns
        -------
        filename: str
            Raw filename for Subreddits
        """

        category_n = self._r_get_category(cat_i)
        category = self._r_category(cat_i, category_n)

        ending = None \
            if cat_i == short_cat[5] \
            else end
        time_filter = None \
            if each_sub[2] == None or each_sub[2] == "all" \
            else each_sub[2]

        if each_sub[2] == None or each_sub[2] == "all":
            index = 0 \
                if cat_i == short_cat[5] \
                else 1
        else:
            index = 2 \
                if cat_i == short_cat[5] \
                else 3

        filename = self._get_sub_fname(category, ending, index, each_sub[1], sub, time_filter)
        filename = self._check_len(filename)

        if args.rules:
            return filename + "-rules"
        
        return filename

    def r_fname(self, args, cat_i, each_sub, sub):
        """
        Determine the filename format for Subreddit scraping by combining previously
        defined private methods:

            self._get_raw_n()
            self._fix()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI
        cat_i: str or int
            Either a single character or integer denoting the full category's index
            or abbreviated category
        each_sub: list
            List of Subreddit scraping settings
        sub: str
            Subreddit name

        Returns
        -------
        filename: str
            Finalized Subreddit filename after string formatting and checking
        """

        raw_n = ""
        end = "result" \
            if isinstance(each_sub[1], int) and int(each_sub[1]) < 2 \
            else "results"

        raw_n = self._get_raw_n(args, cat_i, end, each_sub, sub)

        return self._fix(raw_n)

    def u_fname(self, limit, string):
        """
        Determine filename format for Redditor scraping. 
        
        Calls previously defined private methods:

            self._fix()

        Parameters
        ----------
        limit: str
            Integer in string format denoting the number of results to return
        string: str
            String denoting the Redditor name

        Returns
        -------
        filename: str
            Finalized Redditor filename after string formatting and checking 
        """

        end = "result" \
            if int(limit) < 2 \
            else "results"
        raw_n = f"{string}-{limit}-{end}"

        return self._fix(raw_n)

    def c_fname(self, args, limit, string):
        """
        Determine filename format for submission comments scraping. 
        
        Calls previously defined private methods:

            self._check_len()
            self._fix()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI
        limit: str
            Integer in string format denoting the number of results to return
        string: str
            String denoting the submission's title

        Returns
        -------
        filename: str
            Finalized submission comments filename after string formatting and 
            checking 
        """

        string = self._check_len(string)
        
        if int(limit) != 0:
            plurality = "result" \
                if int(limit) < 2 \
                else "results"
            raw_n = f"{string}-{limit}-{plurality}"
        else:
            raw_n = f"{string}-all"

        if args.raw:
            raw_n = raw_n + "-raw"

        return self._fix(raw_n)

class EncodeNode(JSONEncoder):
    """
    Methods to serialize CommentNodes for JSON export. 
    """

    def default(self, object):
        """
        Override the default JSONEncoder `default()` method. 
        """

        return object.__dict__

class Export():
    """
    Methods for creating directories and export the file.
    """

    @staticmethod
    def _get_filename_extension(f_name, f_type, scrape):
        """
        Get filename extension.

        Parameters
        ----------
        f_name: str
            Filename
        f_type: str
            File type (.csv or .json)
        scrape: str
            Scrape type ("subreddits", "redditors", or "comments")

        Returns
        -------
        dir_path: str
            String denoting the directory path
        """

        dir_path = f"../scrapes/{date}/{scrape}"

        extension = ".csv" \
            if f_type == "csv" \
            else ".json"

        return dir_path + f"/{f_name}{extension}"

    @staticmethod
    def write_csv(data, filename):
        """
        Write data to CSV.

        Parameters
        ----------
        data: dict
            Dictionary of scrape data
        filename: str
            String denoting the filename

        Returns
        -------
        None 
        """

        with open(filename, "w", encoding = "utf-8") as results:
            writer = csv.writer(results, delimiter = ",")
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))

    @staticmethod
    def write_structured_comments(data, f_name):
        """
        Write structured comments to JSON by using the custom JSONEncoder class
        with the `cls` parameter within `json.dumps()`.

        Calls a method from an external module:

            InitializeDirectory.create_dirs()    

        Parameters
        ----------
        data: dict
            Dictionary of scrape data
        f_name: str
            String denoting the filename

        Returns
        -------
        None 
        """

        filename = Export._get_filename_extension(f_name, "json", "comments")
        InitializeDirectory.create_dirs("/".join(filename.split("/")[:-1]))

        with open(filename, "w", encoding = "utf-8") as results:
            json.dump(data, results, indent = 4, cls = EncodeNode)

    @staticmethod
    def write_json(data, filename):
        """
        Write data to JSON.

        Parameters
        ----------
        data: dict
            Dictionary of scrape data
        filename: str
            String denoting the filename

        Returns
        -------
        None 
        """

        with open(filename, "w", encoding = "utf-8") as results:
            json.dump(data, results, indent = 4)
    
    @staticmethod
    def export(data, f_name, f_type, scrape):
        """
        Write data to either CSV or JSON. 
        
        Calls a method from an external module:

            InitializeDirectory.create_dirs()

        Calls previously defined private and public methods:

            Export._get_filename_extension()
            Export.write_json()
            Export.write_csv()

        Parameters
        ----------
        data: dict
            Dictionary of scrape data
        f_name: str
            Filename
        f_type: str
            File type (.csv or .json)
        scrape: str
            Scrape type ("subreddits", "redditors", or "comments")

        Returns
        -------
        None
        """

        filename = Export._get_filename_extension(f_name, f_type, scrape)
        InitializeDirectory.create_dirs("/".join(filename.split("/")[:-1]))

        Export.write_json(data, filename) \
            if f_type == "json" \
            else Export.write_csv(data, filename)
