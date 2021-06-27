"""
Subreddit scraper
=================
Defining methods for the Subreddit scraper.
"""


import logging

from colorama import (
    Fore, 
    Style
)
from halo import Halo
from prettytable import PrettyTable

from urs.praw_scrapers.utils.Objectify import Objectify
from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import (
    Export,
    NameFile
)
from urs.utils.Global import (
    categories,
    confirm_settings,
    convert_time,
    make_list_dict,
    short_cat,
    Status
)
from urs.utils.Logger import (
    LogError,
    LogExport, 
    LogPRAWScraper
)
from urs.utils.Titles import PRAWTitles

class PrintConfirm():
    """
    Methods for printing Subreddit settings and confirm settings.
    """

    @staticmethod
    def _add_each_setting(pretty_subs, s_master):
        """
        Add each Subreddit setting to the PrettyTable.

        Parameters
        ----------
        pretty_subs: PrettyTable
            PrettyTable instance
        s_master: dict
            Dictionary containing all scrape settings

        Returns
        -------
        None
        """

        for sub, settings in s_master.items():
            for each_sub in settings:
                cat_i = short_cat.index(each_sub[0].upper())
                time_filter = each_sub[2].capitalize() \
                    if each_sub[2] != None \
                    else each_sub[2]
                
                pretty_subs.add_row([
                    sub, 
                    categories[cat_i], 
                    time_filter, 
                    each_sub[1]
                ])

    @staticmethod
    def print_settings(s_master):
        """
        Print scraping details (PrettyTable) for each Subreddit.

        Parameters
        ----------
        s_master: dict
            Dictionary containing all scrape settings

        Returns
        -------
        None
        """

        Halo().info(Fore.CYAN + Style.BRIGHT + "Current settings for each Subreddit")

        pretty_subs = PrettyTable()
        pretty_subs.field_names = [
            "Subreddit", 
            "Category", 
            "Time Filter",
            "Number of results / Keywords"
        ]

        PrintConfirm._add_each_setting(pretty_subs, s_master)
        pretty_subs.align = "l"

        print(pretty_subs)

class GetExtras():
    """
    Methods for getting a Subreddit's rules and post requirements.
    """

    @staticmethod
    def get_rules(subreddit):
        """
        Return post requirements and Subreddit rules.

        Parameters
        ----------
        subreddit: PRAW Subreddit object

        Returns
        -------
        post_requirements: dict
            Dictionary containing Subreddit's post requirements
        rules: list[str]
            List containing Subreddit rules
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

class GetSubmissionsSwitch():
    """
    Implementing Pythonic switch case to determine which Subreddit category to
    get results from.
    """

    def __init__(self, search_for, subreddit, time_filter):
        """
        Initialize variables used in later methods:

            self._controversial: Subreddit's controversial ListingGenerator
            self._hot: Subreddit's hot ListingGenerator
            self._new: Subreddit's new ListingGenerator
            self._rising: Subreddit's rising ListingGenerator
            self._top: Subreddit's top ListingGenerator

            self._switch: dictionary containing all Subreddit categories

        Parameters
        ----------
        search_for: str
            String denoting n_results to return
        subreddit: PRAW ListingGenerator
        time_filter: str
            String denoting time filter to apply (for controversial or top categories)

        Returns
        -------
        None
        """

        self._controversial = subreddit.controversial(limit = int(search_for), time_filter = time_filter) \
            if time_filter != None \
            else subreddit.controversial(limit = int(search_for))
        self._hot = subreddit.hot(limit = int(search_for))
        self._new = subreddit.new(limit = int(search_for))
        self._rising = subreddit.rising(limit = int(search_for))
        self._top = subreddit.top(limit = int(search_for), time_filter = time_filter) \
            if time_filter != None \
            else subreddit.top(limit = int(search_for))

        self._switch = {
            0: self._hot,
            1: self._new,
            2: self._controversial,
            3: self._top,
            4: self._rising
        }

    def scrape_sub(self, index):
        """
        Return a command based on the chosen category. 
        
        Calls previously defined private method:

            self._switch()

        Parameters
        ----------
        index: int
            Integer denoting dictionary key

        Returns
        -------
        category_submissions: PRAW ListingGenerator
        """

        return self._switch.get(index)

class GetSubmissions():
    """
    Methods for getting submissions from a Subreddit.
    """

    @staticmethod
    def _collect_search(search_for, sub, subreddit, time_filter):
        """
        Return PRAW ListingGenerator for searching keywords.

        Parameters
        ----------
        search_for: str
            String denoting keywords to search for
        sub: str
            String denoting Subreddit name
        subreddit: PRAW Subreddit object
        time_filter: str
            String denoting time filter to apply

        Returns
        -------
        search_submissions: PRAW ListingGenerator
        """

        Halo().info(f"Searching submissions in r/{sub} for '{search_for}'.")
        
        if time_filter != None:
            Halo().info(f"Time filter: {time_filter.capitalize()}")

        return subreddit.search(f"{search_for}", time_filter = time_filter) \
            if time_filter != None \
            else subreddit.search(f"{search_for}")

    @staticmethod
    def _collect_others(cat_i, search_for, sub, subreddit, time_filter):
        """
        Return PRAW ListingGenerator for all other categories (excluding Search).
        
        Calls previously defined private method:

            GetSubmissionsSwitch().scrape_sub()

        Parameters
        ----------
        cat_i: int
            Integer denoting the index within the categories or short_cat lists
        search_for: str
            String denoting keywords to search for
        sub: str
            String denoting Subreddit name
        subreddit: PRAW Subreddit object
        time_filter: str
            String denoting time filter to apply

        Returns
        -------
        category_submissions: PRAW ListingGenerator
        """

        category = categories[short_cat.index(cat_i)]
        index = short_cat.index(cat_i)
        
        Halo().info(f"Processing {search_for} {category} results from r/{sub}.")
        
        if time_filter != None:
            Halo().info(f"Time filter: {time_filter.capitalize()}")

        return GetSubmissionsSwitch(search_for, subreddit, time_filter).scrape_sub(index)

    @staticmethod
    def get(cat_i, search_for, sub, subreddit, time_filter):
        """
        Get Subreddit submissions and return the PRAW ListingGenerator. 
        
        Calls previously defined private methods:

            GetSubmissions._collect_search()
            GetSubmissions._collect_others()

        Parameters
        ----------
        cat_i: int
            Integer denoting the index within the categories or short_cat lists
        search_for: str
            String denoting keywords to search for
        sub: str
            String denoting Subreddit name
        subreddit: PRAW Subreddit object
        time_filter: str
            String denoting time filter to apply

        Returns
        -------
        submissions: PRAW ListingGenerator
        """

        return GetSubmissions._collect_search(search_for, sub, subreddit, time_filter) \
            if cat_i == short_cat[5] \
            else GetSubmissions._collect_others(cat_i, search_for, sub, subreddit, time_filter)

class FormatSubmissions():
    """
    Methods for formatting PRAW submissions.
    """

    @staticmethod
    def format_submissions(submissions):
        """
        Format submissions to dictionary structure.

        Calls a public method from an external module:

            Objectify().make_submission()

        Parameters
        ----------
        submissions: PRAW ListingGenerator

        Returns
        -------
        submissions_list: list
            List containing formatted submissions
        """

        return [
            Objectify().make_submission(False, submission) 
            for submission in submissions
        ]

class FormatCSV():
    """
    Methods for formatting PRAW submission objects in CSV format.
    """

    @staticmethod
    def format_csv(submissions):
        """
        Format submission metadata for CSV export.

        Parameters
        ----------
        submissions: list
            List containing submission objects

        Returns
        -------
        overview: dict
            Dictionary containing submission data
        """

        format_status = Status(
            "Finished formatting data for CSV export.",
            "Formatting data for CSV export.",
            "white"
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

class FormatJSON():
    """
    Methods for formatting PRAW submission objects in JSON format. 
    """

    @staticmethod
    def _add_subreddit_rules(skeleton, subreddit):
        """
        Add Subreddit rules and post requirements to the JSON skeleton.

        Calls previously defined public method:

            GetExtras.get_rules()

        Parameters
        ----------
        skeleton: dict
            Dictionary containing all Subreddit scrape data
        subreddit: PRAW Subreddit object

        Returns
        -------
        None
        """

        Halo().info("Including Subreddit rules.")
        logging.info("Including Subreddit rules.")
        logging.info("")

        post_requirements, rules = GetExtras.get_rules(subreddit)

        skeleton["subreddit_rules"] = {}
        skeleton["subreddit_rules"]["rules"] = rules
        skeleton["subreddit_rules"]["post_requirements"] = post_requirements

    @staticmethod
    def make_json_skeleton(cat_i, search_for, sub, time_filter):
        """
        Create a skeleton for JSON export. Include scrape details at the top.

        Parameters
        ----------
        cat_i: str
            String denoting the shortened category in the `short_cat` list
        search_for: str
            String denoting n_results returned or keywords searched for
        sub: str
            String denoting the Subreddit name
        time_filter: str
            String denoting the time filter applied to the scrape

        Returns
        -------
        skeleton: dict
            Dictionary containing Subreddit data
        """

        skeleton = {
            "scrape_settings": {
                "subreddit": sub,
                "category": categories[short_cat.index(cat_i)].lower(),
                "n_results_or_keywords": search_for,
                "time_filter": time_filter
            },
            "data": None
        }

        return skeleton

    @staticmethod
    def format_json(args, skeleton, submissions, subreddit):
        """
        Format submission metadata for JSON export.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        reddit: PRAW Reddit object
        skeleton: dict
            Dictionary containing all Subreddit scrape data
        sub: str
            String denoting the Subreddit name
        submissions: list
            List containing submission objects
        """

        format_status = Status(
            "Finished formatting data for JSON export.",
            "Formatting data for JSON export.",
            "white"
        )

        format_status.start()
        skeleton["data"] = submissions
        
        if args.rules:
            FormatJSON._add_subreddit_rules(skeleton, subreddit)
        
        format_status.succeed()

class GetSortWrite():
    """
    Methods to get, sort, then write scraped Subreddit submissions to CSV or JSON.
    """

    @staticmethod
    def _get_sort(args, cat_i, search_for, sub, subreddit, time_filter):
        """
        Get and sort submissions. 
        
        Calls previously defined public methods:

            GetExtras.get_rules()
            GetSubmissions.get()
            SortSubmissions().sort()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        cat_i: str
            String denoting n_results returned or keywords searched for
        search_for: str
            String denoting n_results returned or keywords searched for
        sub: str
            String denoting the Subreddit name
        subreddit: PRAW Subreddit object
        time_filter: str
            String denoting the time filter applied to the scrape

        Returns
        -------
        data: dict
            Dictionary containing scraped Subreddit submission data 
        """

        submissions = GetSubmissions.get(cat_i, search_for, sub, subreddit, time_filter)
        submissions = FormatSubmissions.format_submissions(submissions)

        if args.csv:
            return FormatCSV.format_csv(submissions)

        skeleton = FormatJSON.make_json_skeleton(cat_i, search_for, sub, time_filter)
        FormatJSON.format_json(args, skeleton, submissions, subreddit)

        return skeleton

    @staticmethod
    def _write(args, cat_i, data, each_sub, sub):
        """
        Write submissions to file. 
        
        Calls methods from external modules:

            NameFile().r_fname()
            Export.export()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        cat_i: str
            String denoting n_results returned or keywords searched for
        data: dict
            Dictionary containing scraped Subreddit submission data 
        each_sub: list
            List of Subreddit scraping settings
        sub: str
            String denoting the Subreddit name

        Returns
        -------
        None
        """

        f_name = NameFile().r_fname(args, cat_i, each_sub, sub)
        
        export_option = "json" \
            if not args.csv \
            else "csv"

        Export.export(data, f_name, export_option, "subreddits")

        print()
        Halo(color = "green", text = Style.BRIGHT + Fore.GREEN + f"{export_option.upper()} file for r/{sub} created.").succeed()
        print()

    @staticmethod
    def gsw(args, reddit, s_master):
        """
        Get, sort, then write submissions to file.

        Calls previously defined private methods:

            GetSortWrite._get_sort()
            GetSortWrite._write()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        s_master: dict
            Dictionary containing all scrape settings

        Returns
        -------
        None
        """

        for sub, settings in s_master.items():
            for each_sub in settings:
                cat_i = each_sub[0].upper()
                subreddit = reddit.subreddit(sub)

                data = GetSortWrite._get_sort(args, cat_i, str(each_sub[1]), sub, subreddit, each_sub[2])
                GetSortWrite._write(args, cat_i, data, each_sub, sub)

class RunSubreddit():
    """
    Run the Subreddit scraper.
    """

    @staticmethod
    def _create_settings(args, parser, reddit):
        """
        Create settings for each user input. 
        
        Calls methods from an external modules:

            GetPRAWScrapeSettings().create_list()
            Validation.validate()
            GetPRAWScrapeSettings().get_settings()
            Global.make_list_dict()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        parser: ArgumentParser
            argparse ArgumentParser object
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        s_master: dict
            Dictionary containing all scrape settings
        """

        sub_list = GetPRAWScrapeSettings().create_list(args, "subreddit")
        not_subs, subs = Validation.validate(sub_list, reddit, "subreddit")
        s_master = make_list_dict(subs)
        GetPRAWScrapeSettings().get_settings(args, not_subs, s_master, "subreddit")

        return s_master

    @staticmethod
    @LogPRAWScraper.log_cancel
    def _confirm_write(args, reddit, s_master):
        """
        Print the confirm screen if the user did not specify the `-y` flag. 
        
        Calls previously defined public methods:

            GetSortWrite.gsw(args, reddit, s_master)
            Global.confirm_settings()
            PrintConfirm.print_settings()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        s_master: dict
            Dictionary containing all scrape settings

        Returns
        -------
        None
        """

        PrintConfirm.print_settings(s_master)
        confirm = confirm_settings()
        if confirm == "y":
            print()
            GetSortWrite.gsw(args, reddit, s_master)
        else:
            raise KeyboardInterrupt

    @staticmethod
    def _write_file(args, reddit, s_master):
        """
        Skip or print Subreddit scraping settings if the `-y` flag is entered.
        Then write or quit scraper. 
        
        Calls previously defined public methods:

            GetSortWrite.gsw()
            RunSubreddit._confirm_write()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        s_master: dict
            Dictionary containing all scrape settings

        Returns
        -------
        None
        """

        GetSortWrite.gsw(args, reddit, s_master) \
            if args.y \
            else RunSubreddit._confirm_write(args, reddit, s_master)

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer("subreddit")
    def run(args, parser, reddit):
        """
        Run Subreddit scraper. 
        
        Calls previously defined public methods:

            RunSubreddit._create_settings()
            RunSubreddit._write_file()

        Calls a method from an external module:

            PRAWTitles.r_title()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        parser: ArgumentParser
            argparse ArgumentParser object 
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        s_master: dict
            Dictionary containing all Subreddit scrape settings
        """

        PRAWTitles.r_title()

        s_master = RunSubreddit._create_settings(args, parser, reddit)
        RunSubreddit._write_file(args, reddit, s_master)
        
        return s_master
