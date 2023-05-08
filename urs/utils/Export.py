"""
Exporting data
==============
Methods for naming and exporting scraped data.
"""


import csv
import json
from argparse import Namespace
from json import JSONEncoder
from typing import Any, Dict, List, Literal

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Global import categories, date, short_cat


class NameFile:
    """
    Methods for naming the exported files.
    """

    def __init__(self) -> None:
        """
        Initialize variables used in naming the file:
        """

        self._illegal_chars = [char for char in '[@!#$%^&*()<>?/"\\|}{~:+`=]']

    def _check_len(self, name: str) -> str:
        """
        Verify filename is not too long. Slices the name if it exceeds 50 characters.

        :param str name: The original filename to check.

        :returns: The sliced filename if it is too long, or the original filename.
        :rtype: `str`
        """

        if len(name) > 50:
            return name[0:48] + "--"

        return name

    def _fix(self, name: str) -> str:
        """
        Fix filename if illegal characters are present.

        :param str name: The original filename to check.

        :returns: The fixed filename if it contains any illegal filename characters.
        :rtype: `str`
        """

        fixed = ["_" if char in self._illegal_chars else char for char in name]

        return "".join(fixed)

    def _r_category(self, cat_i: str, category_n: int) -> str:
        """
        Subreddit category name switch.

        :param str cat_i: The abbreviated category name.
        :param int category_n: The `int` corresponding to the dictionary key.

        :returns: The category name.
        :rtype: `str`
        """

        switch = {
            0: categories[5],
            1: categories[short_cat.index(cat_i)] if cat_i != short_cat[5] else None,
        }

        return switch.get(category_n)

    def _r_get_category(self, cat_i: str) -> Literal[0, 1]:
        """
        Choose the Subreddit category index.

        :param str cat_i: The abbreviated category name.

        :returns: An `int` denoting the selected category's index (`0` or `1`)
        :rtype: `int`
        """

        return 0 if cat_i == short_cat[5] else 1

    def _get_sub_fname(
        self,
        category: str,
        end: str,
        index: int,
        n_res_or_kwds: str,
        subreddit: str,
        time_filter: str,
    ) -> str:
        """
        File name switch that stores all possible Subreddit filename formats

        :param str category: The full Subreddit category name.
        :param str end: `"result"` or `"results"` depending on the value of `n_res_or_kwds`.
        :param int index: The `int` corresponding to the dictionary key.
        :param str n_res_or_kwds: The number of results or keywords to search for.
        :param str time_filter: The time filter applied to the scrape, if applicable.

        :returns: The filename for Subreddit scrapes.
        :rtype: `str`
        """

        filter_str = f"-past-{time_filter}"
        search = f"{subreddit}-{category.lower()}-'{n_res_or_kwds}'"
        standard = f"{subreddit}-{category.lower()}-{n_res_or_kwds}-{end}"

        filenames = {
            0: search,
            1: standard,
            2: search + filter_str,
            3: standard + filter_str,
        }

        return filenames.get(index)

    def _get_raw_n(
        self,
        args: Namespace,
        cat_i: str,
        end: str,
        each_sub: List[str],
        sub: str,
    ) -> str:
        """
        Determine filename format for the Subreddit scraper.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param str cat_i: The abbreviated category name.
        :param str end: `"result"` or `"results"` depending on the number of results
            returned.
        :param list[str] each_sub: A `list[str]` containing Subreddit scraping
            settings.
        :param str sub: The name of the Subreddit.

        :returns: The raw filename for Subreddit scrapes.
        :rtype: `str`
        """

        category_n = self._r_get_category(cat_i)
        category = self._r_category(cat_i, category_n)

        ending = None if cat_i == short_cat[5] else end
        time_filter = (
            None if each_sub[2] == None or each_sub[2] == "all" else each_sub[2]
        )

        if each_sub[2] == None or each_sub[2] == "all":
            index = 0 if cat_i == short_cat[5] else 1
        else:
            index = 2 if cat_i == short_cat[5] else 3

        filename = self._get_sub_fname(
            category, ending, index, each_sub[1], sub, time_filter
        )
        filename = self._check_len(filename)

        if args.rules:
            return filename + "-rules"

        return filename

    def r_fname(
        self, args: Namespace, cat_i: str, each_sub: List[str], sub: str
    ) -> str:
        """
        Determine the filename format for Subreddit scraping by combining previously
        defined private methods.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param str cat_i: The abbreviated category name.
        :param list[str] each_sub: A `list[str]` containing Subreddit scraping
            settings.
        :param str sub: The name of the Subreddit.

        :returns: The finalized Subreddit filename after string formatting and
            checking.
        :rtype: `str`
        """

        raw_n = ""
        end = (
            "result"
            if isinstance(each_sub[1], int) and int(each_sub[1]) < 2
            else "results"
        )

        raw_n = self._get_raw_n(args, cat_i, end, each_sub, sub)

        return self._fix(raw_n)

    def u_fname(self, limit: str, redditor: str) -> str:
        """
        Determine filename format for Redditor scraping.

        :param str limit: The number of results to return.,
        :param str redditor: The Redditor's name.

        :returns: The finalized Redditor filename after string formatting and
            checking.
        :rtype: `str`
        """

        end = "result" if int(limit) < 2 else "results"
        raw_n = f"{redditor}-{limit}-{end}"

        return self._fix(raw_n)

    def c_fname(self, args: Namespace, limit: str, submission_title: str) -> str:
        """
        Determine filename format for submission comments scraping.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param str limit: The number of results to return.
        :param str submission_title: The submission's title.

        :returns: The finalized submission filename after string formatting and
            checking.
        :rtype: `str`
        """

        submission_title = self._check_len(submission_title)

        if int(limit) != 0:
            plurality = "result" if int(limit) < 2 else "results"
            raw_n = f"{submission_title}-{limit}-{plurality}"
        else:
            raw_n = f"{submission_title}-all"

        if args.raw:
            raw_n = raw_n + "-raw"

        return self._fix(raw_n)


class EncodeNode(JSONEncoder):
    """
    Methods to serialize CommentNodes for JSON export.
    """

    def default(self, obj: Any) -> Dict[str, Any]:
        """
        Override the default JSONEncoder `default()` method.

        :param Any obj: A `CommentNode` to convert into a `dict[str, Any]`.

        :returns: A `dict[str, Any]` containing `CommentNode` data.
        :rtype: `dict[str, Any]`
        """

        return obj.__dict__


class Export:
    """
    Methods for creating directories and export the file.
    """

    @staticmethod
    def _get_filename_extension(
        f_name: str, f_type: str, scrape: Literal["subreddits", "redditors", "comments"]
    ) -> str:
        """
        Get filename extension.

        :param str f_name: The filename.
        :param str f_type: The filetype.
        :param str scrape: The scrape type ("subreddits", "redditors", or "comments").

        :returns: The path to the file.
        :rtype: `str`
        """

        dir_path = f"../scrapes/{date}/{scrape}"

        extension = ".csv" if f_type == "csv" else ".json"

        return dir_path + f"/{f_name}{extension}"

    @staticmethod
    def write_csv(data: Dict[str, Any], filename: str) -> None:
        """
        Write data to CSV.

        :param dict[str, Any] data: The `dict[str, Any]` containing scrape data.
        :param str filename: The filename.
        """

        with open(filename, "w", encoding="utf-8") as results:
            writer = csv.writer(results, delimiter=",")
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))

    @staticmethod
    def write_structured_comments(data: Dict[str, Any], f_name: str) -> None:
        """
        Write structured comments to JSON by using the custom JSONEncoder class
        with the `cls` parameter within `json.dumps()`.

        :param dict[str, Any] data: The `dict[str, Any]` containing scrape data.
        :param str f_name: The filename.
        """

        filename = Export._get_filename_extension(f_name, "json", "comments")
        InitializeDirectory.create_dirs("/".join(filename.split("/")[:-1]))

        with open(filename, "w", encoding="utf-8") as results:
            json.dump(data, results, cls=EncodeNode, indent=2)

    @staticmethod
    def write_json(data: Dict[str, Any], filename: str) -> None:
        """
        Write data to JSON.

        :param dict[str, Any] data: The `dict[str, Any]` containing scrape data.
        :param str f_name: The filename.
        """

        with open(filename, "w", encoding="utf-8") as results:
            json.dump(data, results, indent=2)

    @staticmethod
    def export(
        data: Dict[str, Any],
        f_name: str,
        f_type: str,
        scrape: Literal["subreddits", "redditors", "comments"],
    ) -> None:
        """
        Write data to either CSV or JSON.

        :param dict[str, Any] data: The `dict[str, Any]` containing scrape data.
        :param str f_name: The filename.
        :param str f_type: The file type.
        :param str scrape: The scrape type ("subreddits", "redditors", or "comments").
        """

        filename = Export._get_filename_extension(f_name, f_type, scrape)
        InitializeDirectory.create_dirs("/".join(filename.split("/")[:-1]))

        Export.write_json(data, filename) if f_type == "json" else Export.write_csv(
            data, filename
        )
