#===============================================================================
#                           Command-line Interface
#===============================================================================
import argparse
import re
import sys

from colorama import (
    init, 
    Fore, 
    Style)

from . import (
    Global, 
    Titles, 
    Validation)
from .Logger import LogError

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class Parser():
    """
    Methods for parsing CLI arguments.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._usage = "$ Urs.py [-h] [-r SUBREDDIT [H|N|C|T|R|S] RESULTS_OR_KEYWORDS OPTIONAL_TIME_FILTER] [-u USER RESULTS] [-c URL RESULTS] [-b] [-y] [--csv|--json]"
        self._description = r"""
Universal Reddit Scraper 3.1.1 - Scrape Subreddits, Redditors, or submission comments

Author: Joseph Lai
Contact: urs_project@protonmail.com
"""
        self._epilog = r"""
Subreddit categories:
   H,h     selecting Hot category
   N,n     selecting New category
   C,c     selecting Controversial category (time filter available)
   T,t     selecting Top category           (time filter available)
   R,r     selecting Rising category
   S,s     selecting Search category        (time filter available)

Subreddit time filters:
   all (default)
   day
   hour
   month
   week
   year

EXAMPLES

Get the first 10 posts in r/askreddit in the Hot category and export to JSON:

    $ ./Urs.py -r askreddit h 10 --json

Search for "United States of America" in r/worldnews and export to CSV:

    $ ./Urs.py -r worldnews s "United States of America" --csv

You can apply a time filter when scraping Subreddit categories Controversial, Top, or Search:
(Scraping Search results from r/learnprogramming from the past month)

    $ ./Urs.py -r learnprogramming s "python developer" month --json

Scraping 15 results from u/spez's Reddit account:

    $ ./Urs.py -u spez 15 --json

Scraping 25 comments from this r/TIFU post:
(Returns a structured JSON file that includes down to third-level replies)

    $ ./Urs.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 25 --json

Scraping all comments from the same r/TIFU post:
(Returns an unstructured JSON file of all comments in level order, ie. top-level first, followed by second-level, then third-level, etc.)

    $ ./Urs.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 0 --json

You can scrape multiple items at once:

    $ ./Urs.py -r askreddit h 15 -u spez 25 -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 50 --json

You can also still use URS 1.0 (SUBREDDIT SCRAPING ONLY), but you cannot include this flag with any items besides export options:

    $ ./Urs.py -b --csv

"""

    ### Add parser Subreddit, Redditor, comments, basic scraper, and skip 
    ### confirmation flags.
    def _add_flags(self, parser):
        urs = parser.add_argument_group("Scraping options")
        urs.add_argument(
            "-r", "--subreddit", 
            action = "append", 
            help = "specify Subreddit to scrape",
            metavar = "", 
            nargs = "+") 
        urs.add_argument(
            "-u", "--redditor", 
            action = "append", 
            help = "specify Redditor profile to scrape",
            metavar = "", 
            nargs = 2) 
        urs.add_argument(
            "-c", "--comments", 
            action = "append", 
            help = "specify the URL of the submission to scrape comments",
            metavar = "", 
            nargs = 2) 
        urs.add_argument(
            "-b", "--basic", 
            action = "store_true", 
            help = "initialize non-CLI Subreddit scraper")
        urs.add_argument(
            "-y", 
            action = "store_true", 
            help = "skip Subreddit options confirmation and scrape immediately")

    ### Add export flags.
    def _add_export(self, parser):
        expt = parser.add_mutually_exclusive_group(required = True)
        expt.add_argument(
            "--csv", 
            action = "store_true", 
            help = "export to CSV")
        expt.add_argument(
            "--json", 
            action = "store_true", 
            help = "export to JSON")

    ### Get args.
    @LogError.log_no_args
    def parse_args(self):
        parser = argparse.ArgumentParser(
            description = self._description,
            epilog = self._epilog, 
            formatter_class = argparse.RawDescriptionHelpFormatter,
            usage = self._usage)

        self._add_flags(parser)
        self._add_export(parser)

        ### Print help message if no arguments are present.
        if len(sys.argv[1:]) == 0:
            parser.print_help()
            raise SystemExit

        args = parser.parse_args()
        return args, parser

class GetScrapeSettings():
    """
    Methods for creating data structures to store scrape settings.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._s_t = Global.s_t
        self._short_cat = Global.short_cat

        self._filterables = [
            self._short_cat[2], 
            self._short_cat[3], 
            self._short_cat[5]]

    ### Switch to determine which kind of list to create.
    def _list_switch(self, args, index):
        switch = {
            0: args.subreddit,
            1: args.redditor,
            2: args.comments
        }

        return switch.get(index)

    ### Create either Subreddit, Redditor, or submissions list.
    def create_list(self, args, l_type):
        index = self._s_t.index(l_type)
        item_list = [item[0] for item in self._list_switch(args, index)]

        return item_list

    ### Set default time filter if a time filter can be applied to the category.
    ### Return the Subreddit settings.
    def _set_sub_settings(self, sub):
        if len(sub) == 3:
            settings = [sub[1], sub[2], "all"] \
                if sub[1].upper() in self._filterables \
                else [sub[1], sub[2], None]
        if len(sub) == 4:
            settings = [sub[1], sub[2], sub[3]]

        return settings

    ### Get Subreddit settings.
    def _subreddit_settings(self, args, master):
        for sub_n in master:
            for sub in args.subreddit:
                settings = self._set_sub_settings(sub)
                
                if sub_n == sub[0]:
                    master[sub_n].append(settings)

    ### Get settings for scraping items that only require two arguments 
    ### (Redditor or comments scrapers).
    def _two_arg_settings(self, master, object):
        for obj in object:
            master[obj[0]] = obj[1]

    ### Get CLI scraping settings for Subreddits, Redditors, and post comments.
    def get_settings(self, args, master, s_type):
        if s_type == self._s_t[0]:
            self._subreddit_settings(args, master)
        elif s_type == self._s_t[1]:
            self._two_arg_settings(master, args.redditor)
        elif s_type == self._s_t[2]:
            self._two_arg_settings(master, args.comments)

class CheckCli():
    """
    Methods for checking CLI arguments and raising errors if they are invalid.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._short_cat = Global.short_cat
        self._special_chars = re.compile("[@_!#$%^&*()<>?/\\|}{~:+`=]")
        
        self._filterables = [
            self._short_cat[2], 
            self._short_cat[3], 
            self._short_cat[5]]
        self._time_filters = [
            "all", 
            "day", 
            "hour", 
            "month", 
            "week", 
            "year"]

    ### Check n_results for Subreddit args.
    def _check_n_results(self, n_results, sub):
        if sub[1].upper() != "S":
            try:
                int(n_results)
                if int(n_results) == 0:
                    raise ValueError
            except ValueError:
                raise ValueError

    ### Check Subreddit args.
    def _check_subreddit(self, args):
        for sub in args.subreddit:
            if sub[1].upper() not in self._short_cat or len(sub) > 4:
                raise ValueError
            elif sub[1].upper() in self._short_cat:
                ### Check args if a time filter is present.
                if len(sub) == 4:
                    if sub[1].upper() not in self._filterables \
                    or sub[3].lower() not in self._time_filters:
                        raise ValueError

                self._check_n_results(sub[2], sub)

    ### Check Redditor args.
    def _check_redditor(self, args):
        for user in args.redditor:
            if user[1].isalpha() \
            or self._special_chars.search(user[1]) != None \
            or int(user[1]) == 0:
                raise ValueError

    ### Check args for items that only require two arguments (Redditor or 
    ### comments scrapers).
    def _check_comments(self, args):
        for submission in args.comments:
            if submission[1].isalpha() \
            or self._special_chars.search(submission[1]) != None:
                raise ValueError

    ### Check args and catching errors.
    @LogError.log_args
    def check_args(self, args, parser):
        if args.subreddit:
            self._check_subreddit(args)
        if args.redditor:
            self._check_redditor(args)
        if args.comments:
            self._check_comments(args)
