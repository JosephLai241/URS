"""
Subreddit scraper
=================
Defining methods for the Subreddit scraper.
"""


import logging

from colorama import (
    init, 
    Fore, 
    Style
)
from prettytable import PrettyTable

from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import (
    Export,
    NameFile
)
from urs.utils.Global import (
    categories,
    convert_time,
    eo,
    make_list_dict,
    options,
    s_t,
    short_cat,
)
from urs.utils.Logger import (
    LogError,
    LogExport, 
    LogPRAWScraper
)
from urs.utils.Titles import PRAWTitles

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class CheckSubreddits():
    """
    Method for checking if Subreddit(s) exist. Print invalid Subreddits if
    applicable.
    """

    @staticmethod
    @LogError.log_none_left("Subreddits")
    def list_subreddits(parser, reddit, s_t, sub_list):
        """
        Check if Subreddits exist and list invalid Subreddits if applicable.

        Calls a method from an external module:

            Validation.existence()

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser object
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        s_t: list
            List of scraper types
        sub_list: list
            List of Redditors

        Returns
        -------
        subs: list
            List of valid Subreddits
        """

        print("\nChecking if Subreddit(s) exist...")
        logging.info("Validating Subreddits...")
        logging.info("")
        subs, not_subs = Validation().existence(s_t[0], sub_list, parser, reddit, s_t)
        
        if not_subs:
            print(Fore.YELLOW + Style.BRIGHT + "\nThe following Subreddits were not found and will be skipped:")
            print(Fore.YELLOW + Style.BRIGHT + "-" * 60)
            print(*not_subs, sep = "\n")

            logging.warning("Failed to validate the following Subreddits:")
            logging.warning("%s" % (not_subs))
            logging.warning("Skipping.")
            logging.info("")

        if not subs:
            logging.critical("ALL SUBREDDITS FAILED VALIDATION.")
            raise ValueError
        
        return not_subs, subs

class PrintConfirm():
    """
    Methods for printing Subreddit settings and confirm settings.
    """

    @staticmethod
    def _add_each_setting(args, pretty_subs, s_master):
        """
        Add each Subreddit setting to the PrettyTable.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
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
    def print_settings(args, s_master):
        """
        Print scraping details (PrettyTable) for each Subreddit.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        s_master: dict
            Dictionary containing all scrape settings

        Returns
        -------
        None
        """

        print(Fore.CYAN + Style.BRIGHT + "\nCurrent settings for each Subreddit")

        pretty_subs = PrettyTable()
        pretty_subs.field_names = [
            "Subreddit", 
            "Category", 
            "Time Filter",
            "Number of results / Keywords"
        ]

        PrintConfirm._add_each_setting(args, pretty_subs, s_master)
        pretty_subs.align = "l"

        print(pretty_subs)

    @staticmethod
    def confirm_settings():
        """
        Confirm scraping options.

        Parameters
        ----------
        None

        Exceptions
        ----------
        ValueError:
            Raised if the confirmation input is invalid

        Returns
        -------
        confirm: str
            String denoting whether to confirm settings and continue Subreddit scraping
        """

        while True:
            try:
                confirm = input("\nConfirm options? [Y/N] ").strip().lower()

                if confirm == options[0]:
                    return confirm
                elif confirm == options[1]:
                    break
                elif confirm not in options:
                    raise ValueError
            except ValueError:
                print("Not an option! Try again.")

class GetRules():
    """
    Methods for getting a Subreddit's rules and post requirements.
    """

    @staticmethod
    def get(subreddit):
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

        rules = [rule_list for rule, rule_list in subreddit.rules().items() if rule == "rules"]
        return subreddit.post_requirements(), rules[0]

class GetPostsSwitch():
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

class GetPosts():
    """
    Methods for getting posts from a Subreddit.
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

        print(Style.BRIGHT + "\nSearching posts in r/%s for '%s'..." % (sub, search_for))
        
        if time_filter != None:
            print(Style.BRIGHT + "Time filter: %s" % time_filter.capitalize())

        return subreddit.search("%s" % search_for, time_filter = time_filter) \
            if time_filter != None \
            else subreddit.search("%s" % search_for)

    @staticmethod
    def _collect_others(args, cat_i, search_for, sub, subreddit, time_filter):
        """
        Return PRAW ListingGenerator for all other categories (excluding Search).
        
        Calls previously defined private method:

            GetPostsSwitch().scrape_sub()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
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
            
        print(Style.BRIGHT + "\nProcessing %s %s results from r/%s..." % (search_for, category, sub))
        
        if time_filter != None:
            print(Style.BRIGHT + "Time filter: %s" % time_filter.capitalize())

        return GetPostsSwitch(search_for, subreddit, time_filter).scrape_sub(index)

    @staticmethod
    def get(args, cat_i, reddit, search_for, sub, time_filter):
        """
        Get Subreddit posts and return the PRAW ListingGenerator. 
        
        Calls previously defined private methods:

            GetPosts._collect_search()
            GetPosts._collect_others()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        cat_i: int
            Integer denoting the index within the categories or short_cat lists
        reddit: PRAW Reddit instance
        search_for: str
            String denoting keywords to search for
        sub: str
            String denoting Subreddit name
        time_filter: str
            String denoting time filter to apply

        Returns
        -------
        submissions: PRAW ListingGenerator
        """

        subreddit = reddit.subreddit(sub)

        return GetPosts._collect_search(search_for, sub, subreddit, time_filter) \
            if cat_i == short_cat[5] \
            else GetPosts._collect_others(args, cat_i, search_for, sub, subreddit, time_filter)

class SortPosts():
    """
    Methods for sorting posts based on the export option.
    """

    def __init__(self):
        """
        Initialize variables used in later methods:

            self._titles: list of titles for Subreddit metadata
        
        Returns
        -------
        None
        """

        self._titles = [
            "title", 
            "flair", 
            "date_created", 
            "upvotes", 
            "upvote_ratio", 
            "id", 
            "edited", 
            "is_locked", 
            "nsfw", 
            "is_spoiler", 
            "stickied", 
            "url", 
            "comment_count", 
            "text"
        ]

    def _initialize_dict(self, args):
        """
        Initialize a dictionary depending on export option. Creates a dictionary
        with empty lists as values if exporting to CSV. 
        
        Calls a public method from an external module:

            Global.make_list_dict() 

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 

        Returns
        -------
        empty_dict: dict
            Dictionary to store Subreddit data
        """

        return make_list_dict(self._titles) \
            if args.csv \
            else dict()

    def _fix_edit_date(self, post):
        """
        Fix "Edited?" date.
        
        Calls a public method from an external module:

            Global.convert_time() 

        Parameters
        ----------
        post: PRAW submission object 

        Returns
        -------
        fixed_date: str
            String denoting either an edited date or boolean indicating the post
            was not edited
        """

        return str(post.edited) \
            if str(post.edited).isalpha() \
            else str(convert_time(post.edited))

    def _get_data(self, post):
        """
        Get post data. 
        
        Calls previously defined private method:

            self._fix_edit_date()
        
        Calls a public method from an external module:

            Global.convert_time() 

        Parameters
        ----------
        post: PRAW submission object 

        Returns
        -------
        post_data: list
            List containing post metadata
        """

        edited = self._fix_edit_date(post)
        post_data = [
            post.title, 
            post.link_flair_text, 
            convert_time(post.created), 
            post.score, 
            post.upvote_ratio, 
            post.id, 
            edited, 
            post.locked, 
            post.over_18, 
            post.spoiler, 
            post.stickied, 
            post.url, 
            post.num_comments, 
            post.selftext
        ]

        return post_data

    def _csv_format(self, overview, post_data):
        """
        Append data to overview dictionary for CSV export.

        Parameters
        ----------
        overview: dict
            Dictionary containing Subreddit submission data
        post_data: list
            List containing post metadata

        Returns
        -------
        None
        """

        for title, data in zip(self._titles, post_data):
            overview[title].append(data)

    def _make_json_skeleton(self, cat_i, search_for, sub, time_filter):
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
        json_data: dict
            Dictionary containing Subreddit data
        """

        json_data = {
            "scrape_settings": {
                "subreddit": sub,
                "category": categories[short_cat.index(cat_i)].lower(),
                "n_results_or_keywords": search_for,
                "time_filter": time_filter
            },
            "data": []
        }

        return json_data

    def _add_json_subreddit_rules(self, json_data, post_requirements, rules):
        """
        Add Subreddit rules and post requirements to the JSON skeleton.

        Parameters
        ----------
        json_data: dict
            Dictionary containing Subreddit data
        post_requirements: dict
            Dictionary containing the Subreddit's post requirements
        rules: list
            List of rule objects

        Returns
        -------
        None
        """

        json_data["subreddit_rules"] = {}
        json_data["subreddit_rules"]["rules"] = rules
        json_data["subreddit_rules"]["post_requirements"] = post_requirements

    def _add_json_submission_data(self, json_data, post_data):
        """
        Add Subreddit rules and post requirements to the JSON skeleton.

        Parameters
        ----------
        json_data: dict
            Dictionary containing Subreddit data
        post_data: list
            List containing submission data

        Returns
        -------
        None
        """

        json_data["data"].append({
            title: value for title, value in zip(self._titles, post_data)
        })
    
    def sort(self, args, cat_i, collected, post_requirements, rules, search_for, sub, time_filter):
        """
        Sort collected dictionary based on export option. 
        
        Calls previously defined private methods:

            self._initialize_dict()
            self._get_data()
            self._csv_format()
            self._make_json_skeleton()
            self._add_json_subreddit_rules()
            self._add_json_submission_data()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        cat_i: str
            String denoting n_results returned or keywords searched for
        collected: PRAW submission object
        post_requirements: dict
            Dictionary containing the Subreddit's post requirements 
        rules: list
            List of rule objects
        search_for: str
            String denoting n_results returned or keywords searched for
        sub: str
            String denoting the Subreddit name
        time_filter: str
            String denoting the time filter applied to the scrape

        Returns
        -------
        data: dict
            Dictionary containing scraped Subreddit submission data
        """

        print("\nThis may take a while. Please wait.")

        if args.csv:
            overview = self._initialize_dict(args)
            for post in collected:
                post_data = self._get_data(post)
                self._csv_format(overview, post_data)

            return overview
            
        json_data = self._make_json_skeleton(cat_i, search_for, sub, time_filter)
        
        if args.rules:
            print(Fore.CYAN + Style.BRIGHT + "\nIncluding Subreddit rules...")
            logging.info("Including Subreddit rules...")
            logging.info("")
            
            self._add_json_subreddit_rules(json_data, post_requirements, rules)
        
        for post in collected:
            post_data = self._get_data(post)
            self._add_json_submission_data(json_data, post_data)

        return json_data

class GetSortWrite():
    """
    Methods to get, sort, then write scraped Subreddit posts to CSV or JSON.
    """

    @staticmethod
    def _get_sort(args, cat_i, reddit, search_for, sub, time_filter):
        """
        Get and sort posts. 
        
        Calls previously defined public methods:

            GetRules.get()
            GetPosts.get()
            SortPosts().sort()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        cat_i: str
            String denoting n_results returned or keywords searched for
        reddit: PRAW Reddit object
        search_for: str
            String denoting n_results returned or keywords searched for
        sub: str
            String denoting the Subreddit name
        time_filter: str
            String denoting the time filter applied to the scrape

        Returns
        -------
        data: dict
            Dictionary containing scraped Subreddit submission data 
        """

        post_requirements, rules = GetRules.get(reddit.subreddit(sub))
        collected = GetPosts.get(args, cat_i, reddit, search_for, sub, time_filter)

        return SortPosts().sort(args, cat_i, collected, post_requirements, rules, search_for, sub, time_filter)

    @staticmethod
    def _determine_export(args, data, f_name):
        """
        Export to either CSV or JSON.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        data: dict
            Dictionary containing scraped Subreddit submission data 
        f_name: str
            String denoting the filename

        Returns
        -------
        None
        """

        export_option = eo[1] \
            if not args.csv \
            else eo[0]

        Export.export(data, f_name, export_option, "subreddits")

    @staticmethod
    def _print_confirm(args, sub):
        """
        Set print length depending on string length.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        sub: str
            String denoting the Subreddit name

        Returns
        -------
        None
        """

        export_option = "JSON" \
            if not args.csv \
            else "CSV"

        confirmation = "\n%s file for r/%s created." % (export_option, sub)

        print(Style.BRIGHT + Fore.GREEN + confirmation)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(confirmation) - 1))

    @staticmethod
    def _write(args, cat_i, data, each_sub, sub):
        """
        Write posts. 
        
        Calls previously defined private methods:

            GetSortWrite._determine_export()
            GetSortWrite._print_confirm()

        Calls a method from an external module:

            NameFile().r_fname()

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
        GetSortWrite._determine_export(args, data, f_name)
        GetSortWrite._print_confirm(args, sub)

    @staticmethod
    def gsw(args, reddit, s_master):
        """
        Get, sort, then write posts to file.

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
                data = GetSortWrite._get_sort(args, cat_i, reddit, str(each_sub[1]), sub, each_sub[2])
                GetSortWrite._write(args, cat_i, data, each_sub, sub)

class RunSubreddit():
    """
    Run the Subreddit scraper.
    """

    @staticmethod
    def _create_settings(args, parser, reddit, s_t):
        """
        Create settings for each user input. 
        
        Calls previously defined private methods:

            CheckSubreddits.list_subreddits()

        Calls methods from an external modules:

            GetPRAWScrapeSettings().create_list()
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
        s_t: list
            List of scraper types

        Returns
        -------
        s_master: dict
            Dictionary containing all scrape settings
        """

        sub_list = GetPRAWScrapeSettings().create_list(args, s_t[0])
        not_subs, subs = CheckSubreddits.list_subreddits(parser, reddit, s_t, sub_list)
        s_master = make_list_dict(subs)
        GetPRAWScrapeSettings().get_settings(args, not_subs, s_master, s_t[0])

        return s_master

    @staticmethod
    @LogPRAWScraper.log_cancel
    def _confirm_write(args, reddit, s_master):
        """
        Print the confirm screen if the user did not specify the `-y` flag. 
        
        Calls previously defined public methods:

            GetSortWrite.gsw(args, reddit, s_master)
            PrintConfirm.confirm_settings()
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

        PrintConfirm.print_settings(args, s_master)
        confirm = PrintConfirm.confirm_settings()
        if confirm == options[0]:
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

        if args.y:
            GetSortWrite.gsw(args, reddit, s_master)
        else:
            RunSubreddit._confirm_write(args, reddit, s_master)

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer(s_t[0])
    def run(args, parser, reddit, s_t):
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
        s_t: list
            List of scraper types

        Returns
        -------
        s_master: dict
            Dictionary containing valid Subreddits and their respective scrape
            settings
        """

        PRAWTitles.r_title()

        s_master = RunSubreddit._create_settings(args, parser, reddit, s_t)
        RunSubreddit._write_file(args, reddit, s_master)
        
        return s_master
