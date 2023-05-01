"""
Subreddit scraper
=================
Defining methods for the Subreddit scraper.
"""


import logging
from argparse import Namespace
from typing import Any, Dict, Iterator, List, Tuple

from colorama import Fore, Style
from halo import Halo
from praw import Reddit
from praw.models import Subreddit
from prettytable import PrettyTable

from urs.praw_scrapers.utils.Objectify import Objectify
from urs.praw_scrapers.utils.Validation import Validation
from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import Export, NameFile
from urs.utils.Global import (
    Status,
    categories,
    confirm_settings,
    convert_time,
    make_list_dict,
    short_cat,
)
from urs.utils.Logger import LogExport, LogPRAWScraper
from urs.utils.Titles import PRAWTitles


class PrintConfirm:
    """
    Methods for printing Subreddit settings and confirm settings.
    """

    @staticmethod
    def _add_each_setting(pretty_subs: PrettyTable, s_master: Dict[str, Any]) -> None:
        """
        Add each Subreddit setting to the PrettyTable.

        :param PrettyTable pretty_subs: The `PrettyTable` instance.
        :pararm dict[str, Any] s_master: A `dict[str, Any]` containing all scrape
            settings.
        """

        for sub, settings in s_master.items():
            for each_sub in settings:
                cat_i = short_cat.index(each_sub[0].upper())
                time_filter = (
                    each_sub[2].capitalize() if each_sub[2] != None else each_sub[2]
                )

                pretty_subs.add_row([sub, categories[cat_i], time_filter, each_sub[1]])

    @staticmethod
    def print_settings(s_master: Dict[str, Any]) -> None:
        """
        Print scraping details (PrettyTable) for each Subreddit.

        :pararm dict[str, Any] s_master: A `dict[str, Any]` containing all scrape
            settings.
        """

        Halo().info(Fore.CYAN + Style.BRIGHT + "Current settings for each Subreddit")

        pretty_subs = PrettyTable()
        pretty_subs.field_names = [
            "Subreddit",
            "Category",
            "Time Filter",
            "Number of results / Keywords",
        ]

        PrintConfirm._add_each_setting(pretty_subs, s_master)
        pretty_subs.align = "l"

        print(pretty_subs)


class GetExtras:
    """
    Methods for getting a Subreddit's rules and post requirements.
    """

    @staticmethod
    def get_rules(
        subreddit: Subreddit,
    ) -> Tuple[Dict[str, str | int | bool], List[Dict[str, Any]]]:
        """
        Return post requirements and Subreddit rules.

        :param Subreddit subreddit: The PRAW `Subreddit` instance.

        :returns: The post requirements and the rules for the Subreddit.
        :rtype: `(dict[str, str | int | bool], list[dict[str, Any]])`
        """

        rules = [
            {
                "created_utc": convert_time(rule.created_utc),
                "description": rule.description,
                "kind": rule.kind,
                "priority": rule.priority,
                "short_name": rule.short_name,
                "violation_reason": rule.violation_reason,
            }
            for rule in subreddit.rules
        ]

        return subreddit.post_requirements(), rules


class GetSubmissionsSwitch:
    """
    Implementing Pythonic switch case to determine which Subreddit category to
    get results from.
    """

    def __init__(self, search_for: str, subreddit: Subreddit, time_filter: str) -> None:
        """
        Initialize variables used in later methods:

            self._controversial: Subreddit's controversial ListingGenerator
            self._hot: Subreddit's hot ListingGenerator
            self._new: Subreddit's new ListingGenerator
            self._rising: Subreddit's rising ListingGenerator
            self._top: Subreddit's top ListingGenerator

            self._switch: dictionary containing all Subreddit categories

        :param str search_for: A `str` indicating the number of results to return
        :param Subreddit subreddit: The PRAW `Subreddit` instance.
        :param str time_filter: The time filter to apply (for Controversial and
            Top categories).
        """

        self._controversial = (
            subreddit.controversial(limit=int(search_for), time_filter=time_filter)
            if time_filter != None
            else subreddit.controversial(limit=int(search_for))
        )
        self._hot = subreddit.hot(limit=int(search_for))
        self._new = subreddit.new(limit=int(search_for))
        self._rising = subreddit.rising(limit=int(search_for))
        self._top = (
            subreddit.top(limit=int(search_for), time_filter=time_filter)
            if time_filter != None
            else subreddit.top(limit=int(search_for))
        )

        self._switch = {
            0: self._hot,
            1: self._new,
            2: self._controversial,
            3: self._top,
            4: self._rising,
        }

    def scrape_sub(self, index: int) -> Iterator[Any]:
        """
        Return a command based on the chosen category.

        :param int index: An `int` indicating the dictionary key to target.

        :returns: An `Iterator` over the Subreddit's posts in a particular category.
        :rtype: `Iterator[Any]`
        """

        return self._switch.get(index)


class GetSubmissions:
    """
    Methods for getting submissions from a Subreddit.
    """

    @staticmethod
    def _collect_search(
        search_for: str, sub: str, subreddit: Subreddit, time_filter: str
    ) -> Iterator[Any]:
        """
        Return PRAW ListingGenerator for searching keywords.

        :param str search_for: Keywords to search for.
        :param str sub: The Subreddit's name.
        :param Subreddit subreddit: The `Subreddit` instance.
        :param str time_filter: The time filter to apply to the query.

        :returns: An `Iterator` over the Subreddit's posts.
        :rtype: `Iterator[Any]`
        """

        Halo().info(f"Searching submissions in r/{sub} for '{search_for}'.")

        if time_filter != None:
            Halo().info(f"Time filter: {time_filter.capitalize()}")

        return (
            subreddit.search(f"{search_for}", time_filter=time_filter)
            if time_filter != None
            else subreddit.search(f"{search_for}")
        )

    @staticmethod
    def _collect_others(
        cat_i: str, search_for: str, sub: str, subreddit: Subreddit, time_filter: str
    ) -> Iterator[Any]:
        """
        Return PRAW ListingGenerator for all other categories (excluding Search).

        :param str cat_i: The shortened category name.
        :param str search_for: Keywords to search for.
        :param str sub: The Subreddit's name.
        :param Subreddit subreddit: The `Subreddit` instance.
        :param str time_filter: The time filter to apply to the query.

        :returns: An `Iterator` over the Subreddit's posts.
        :rtype: `Iterator[Any]`
        """

        category = categories[short_cat.index(cat_i)]
        index = short_cat.index(cat_i)

        Halo().info(f"Processing {search_for} {category} results from r/{sub}.")

        if time_filter != None:
            Halo().info(f"Time filter: {time_filter.capitalize()}")

        return GetSubmissionsSwitch(search_for, subreddit, time_filter).scrape_sub(
            index
        )

    @staticmethod
    def get(
        cat_i: str, search_for: str, sub: str, subreddit: Subreddit, time_filter: str
    ) -> Iterator[Any]:
        """
        Get Subreddit submissions and return the PRAW ListingGenerator.

        :param str cat_i: The shortened category name.
        :param str search_for: Keywords to search for.
        :param str sub: The Subreddit's name.
        :param Subreddit subreddit: The `Subreddit` instance.
        :param str time_filter: The time filter to apply to the query.

        :returns: An `Iterator` over the Subreddit's posts.
        :rtype: `Iterator[Any]`
        """

        return (
            GetSubmissions._collect_search(search_for, sub, subreddit, time_filter)
            if cat_i == short_cat[5]
            else GetSubmissions._collect_others(
                cat_i, search_for, sub, subreddit, time_filter
            )
        )


class FormatSubmissions:
    """
    Methods for formatting PRAW submissions.
    """

    @staticmethod
    def format_submissions(submissions: Iterator[Any]) -> List[Dict[str, Any]]:
        """
        Format submissions to dictionary structure.

        :param Iterator[Any] submissions: PRAW `ListingGenerator` for submissions.

        :returns: A `list[dict[str, Any]]` containing formatted submissions.
        :rtype: `list[dict[str, Any]]`
        """

        return [
            Objectify().make_submission(False, submission) for submission in submissions
        ]


class FormatCSV:
    """
    Methods for formatting PRAW submission objects in CSV format.
    """

    @staticmethod
    def format_csv(submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format submission metadata for CSV export.

        :param list[dict[str, Any]] submissions: A `list[dict[str, Any]]` containing
            submission objects.

        :returns: A `dict[str, Any]` containing submission data.
        :rtype: `dict[str, Any]`
        """

        format_status = Status(
            "Finished formatting data for CSV export.",
            "Formatting data for CSV export.",
            "white",
        )

        overview = dict()

        format_status.start()
        for submission in submissions:
            for field, metadata in submission.items():
                if field not in overview.keys():
                    overview[field] = []

                overview[field].append(metadata)

        format_status.succeed()
        return overview


class FormatJSON:
    """
    Methods for formatting PRAW submission objects in JSON format.
    """

    @staticmethod
    def _add_subreddit_rules(skeleton: Dict[str, Any], subreddit: Subreddit) -> None:
        """
        Add Subreddit rules and post requirements to the JSON skeleton.

        :param dict[str, Any] skeleton: A `dict[str, Any]` containing all Subreddit
            scrape data.
        :param Subreddit subreddit: The `Subreddit` instance.
        """

        Halo().info("Including Subreddit rules.")
        logging.info("Including Subreddit rules.")
        logging.info("")

        post_requirements, rules = GetExtras.get_rules(subreddit)

        skeleton["subreddit_rules"] = {}
        skeleton["subreddit_rules"]["rules"] = rules
        skeleton["subreddit_rules"]["post_requirements"] = post_requirements

    @staticmethod
    def make_json_skeleton(
        cat_i: str, search_for: str, sub: str, time_filter: str
    ) -> Dict[str, Any]:
        """
        Create a skeleton for JSON export. Include scrape details at the top.

        :param str cat_i: The index within the `categories` or `short_cat` lists.
        :param str search_for: Keywords to search for.
        :param str sub: The Subreddit's name.
        :param str time_filter: The time filter to apply to the query.

        :returns: A `dict[str, Any]` containing Subreddit data.
        :rtype: `dict[str, Any]`
        """

        skeleton = {
            "scrape_settings": {
                "subreddit": sub,
                "category": categories[short_cat.index(cat_i)].lower(),
                "n_results_or_keywords": search_for,
                "time_filter": time_filter,
            },
            "data": None,
        }

        return skeleton

    @staticmethod
    def format_json(
        args: Namespace,
        skeleton: Dict[str, Any],
        submissions: List[Dict[str, Any]],
        subreddit: Subreddit,
    ) -> None:
        """
        Format submission metadata for JSON export.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param dict[str, Any] skeleton: A `dict[str, Any]` containing all Subreddit
            scrape data.
        :param list[dict[str, Any]] submissions: A `list[dict[str, Any]]` containing
            submission objects.
        :param Subreddit subreddit: The PRAW `Subreddit` instance.
        """

        format_status = Status(
            "Finished formatting data for JSON export.",
            "Formatting data for JSON export.",
            "white",
        )

        format_status.start()
        skeleton["data"] = submissions

        if args.rules:
            FormatJSON._add_subreddit_rules(skeleton, subreddit)

        format_status.succeed()


class GetSortWrite:
    """
    Methods to get, sort, then write scraped Subreddit submissions to CSV or JSON.
    """

    @staticmethod
    def _get_sort(
        args: Namespace,
        cat_i: str,
        search_for: str,
        sub: str,
        subreddit: Subreddit,
        time_filter: str,
    ) -> Dict[str, Any]:
        """
        Get and sort submissions.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param str cat_i: The shortened category index.
        :param str search_for: Keywords to search for.
        :param str sub: The Subreddit's name.
        :param Subreddit subreddit: The `Subreddit` instance.
        :param str time_filter: The time filter to apply to the query.

        :returns: A `dict[str, Any]` containing scraped Subreddit submission data.
        :rtype: `dict[str, Any]`
        """

        submissions = GetSubmissions.get(cat_i, search_for, sub, subreddit, time_filter)
        submissions = FormatSubmissions.format_submissions(submissions)

        if args.csv:
            return FormatCSV.format_csv(submissions)

        skeleton = FormatJSON.make_json_skeleton(cat_i, search_for, sub, time_filter)
        FormatJSON.format_json(args, skeleton, submissions, subreddit)

        return skeleton

    @staticmethod
    def _write(
        args: Namespace,
        cat_i: str,
        data: Dict[str, Any],
        each_sub: List[str],
        sub: str,
    ) -> None:
        """
        Write submissions to file.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param str cat_i: The shortened category index.
        :param dict[str, Any] data: A `dict[str, Any]` containing scraped Subreddit
            submission data.
        :param list[str] each_sub: A `list[str]` containing Subreddit scraping
            settings.
        :param str sub: The Subreddit's name.
        """

        f_name = NameFile().r_fname(args, cat_i, each_sub, sub)

        export_option = "json" if not args.csv else "csv"

        Export.export(data, f_name, export_option, "subreddits")

        print()
        Halo(
            color="green",
            text=Style.BRIGHT
            + Fore.GREEN
            + f"{export_option.upper()} file for r/{sub} created.",
        ).succeed()
        print()

    @staticmethod
    def gsw(args: Namespace, reddit: Reddit, s_master: Dict[str, Any]) -> None:
        """
        Get, sort, then write submissions to file.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param Reddit reddit: The Reddit instance.
        :param dict[str, Any] s_master: A `dict[str, Any]` containing all scrape
            settings.
        """

        for sub, settings in s_master.items():
            for each_sub in settings:
                cat_i = each_sub[0].upper()
                subreddit = reddit.subreddit(sub)

                data = GetSortWrite._get_sort(
                    args, cat_i, str(each_sub[1]), sub, subreddit, each_sub[2]
                )
                GetSortWrite._write(args, cat_i, data, each_sub, sub)


class RunSubreddit:
    """
    Run the Subreddit scraper.
    """

    @staticmethod
    def _create_settings(args: Namespace, reddit: Reddit) -> Dict[str, List[Any]]:
        """
        Create settings for each user input.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param Reddit reddit: The Reddit instance.

        :returns: A `dict[str, list[Any]]` containing all scrape settings.
        :rtype: `dict[str, list[Any]]`
        """

        sub_list = GetPRAWScrapeSettings().create_list(args, "subreddit")
        not_subs, subs = Validation.validate(sub_list, reddit, "subreddit")
        s_master = make_list_dict(subs)
        GetPRAWScrapeSettings().get_settings(args, not_subs, s_master, "subreddit")

        return s_master

    @staticmethod
    @LogPRAWScraper.log_cancel
    def _confirm_write(
        args: Namespace, reddit: Reddit, s_master: Dict[str, Any]
    ) -> None:
        """
        Print the confirm screen if the user did not specify the `-y` flag.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param Reddit reddit: The Reddit instance.
        :param dict[str, Any] s_master: A `dict[str, Any]` containing all scrape
            settings.
        """

        PrintConfirm.print_settings(s_master)
        confirm = confirm_settings()
        if confirm == "y":
            print()
            GetSortWrite.gsw(args, reddit, s_master)
        else:
            raise KeyboardInterrupt

    @staticmethod
    def _write_file(args: Namespace, reddit: Reddit, s_master: Dict[str, Any]) -> None:
        """
        Skip or print Subreddit scraping settings if the `-y` flag is entered.
        Then write or quit scraper.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param Reddit reddit: The Reddit instance.
        :param dict[str, Any] s_master: A `dict[str, Any]` containing all scrape
            settings.
        """

        GetSortWrite.gsw(
            args, reddit, s_master
        ) if args.y else RunSubreddit._confirm_write(args, reddit, s_master)

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer("subreddit")
    def run(args: Namespace, reddit: Reddit) -> Dict[str, List[Any]]:
        """
        Run Subreddit scraper.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param Reddit reddit: The Reddit instance.
        """

        PRAWTitles.r_title()

        s_master = RunSubreddit._create_settings(args, reddit)
        RunSubreddit._write_file(args, reddit, s_master)

        return s_master
