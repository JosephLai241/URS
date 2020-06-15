#===============================================================================
#                       Command-line Interface Functions
#===============================================================================
import argparse
import sys

from colorama import Fore, init, Style
from . import Global, Titles, Validation
from .Logger import LogError

### Automate sending reset sequences to turn off color changes at the end of 
### every print
init(autoreset = True)

class Parser():
    """
    Functions for parsing CLI arguments.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._usage = "Urs.py [-h] [-r SUBREDDIT [H|N|C|T|R|S] RESULTS_OR_KEYWORDS] [-u USER RESULTS] [-c URL RESULTS] [-b] [-y] [--csv|--json]"
        self._description = r"""
Universal Reddit Scraper 3.1 - Scrape Subreddits, submissions, Redditors, or comments from submissions

Author: Joseph Lai
Contact: urs_project@protonmail.com
"""
        self._epilog = r"""
Subreddit categories:
   H,h     selecting Hot category
   N,n     selecting New category
   C,c     selecting Controversial category
   T,t     selecting Top category
   R,r     selecting Rising category
   S,s     selecting Search category

EXAMPLES

Get the first 10 posts in r/askreddit in the Hot category and export to JSON:

    $ ./Urs.py -r askreddit h 10 --json

Search for "United States of America" in r/worldnews and export to CSV:

    $ ./Urs.py -r worldnews s "United States of America" --csv

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
    @staticmethod
    def _add_flags(parser):
        urs = parser.add_argument_group("Scraping options")
        urs.add_argument("-r", "--subreddit", action = "append", nargs = 3, 
            metavar = "", help = "specify Subreddit to scrape")
        urs.add_argument("-u", "--redditor", action = "append", nargs = 2, 
            metavar = "", help = "specify Redditor profile to scrape")
        urs.add_argument("-c", "--comments", action = "append", nargs = 2, 
            metavar = "", help = "specify the URL of the submission to scrape comments")
        urs.add_argument("-b", "--basic", action = "store_true", 
            help = "initialize non-CLI Subreddit scraper")
        urs.add_argument("-y", action = "store_true", 
            help = "skip Subreddit options confirmation and scrape immediately")

    ### Add export flags.
    @staticmethod
    def _add_export(parser):
        expt = parser.add_mutually_exclusive_group(required = True)
        expt.add_argument("--csv", action = "store_true", help = "export to CSV")
        expt.add_argument("--json", action = "store_true", help = "export to JSON")

    ### Get args.
    def parse_args(self):
        parser = argparse.ArgumentParser(description = self._description,
            epilog = self._epilog, formatter_class = argparse.RawDescriptionHelpFormatter,
            usage = self._usage)

        Parser._add_flags(parser)
        Parser._add_export(parser)

        ### Print help message if no arguments are present.
        if len(sys.argv[1:]) == 0:
            parser.print_help()
            parser.exit()

        args = parser.parse_args()
        return args, parser

class GetScrapeSettings():
    """
    Functions for creating data structures to store scrape settings.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._s_t = Global.s_t

    ### Switch to determine which kind of list to create.
    @staticmethod
    def _list_switch(args, index):
        switch = {
            0: args.subreddit,
            1: args.redditor,
            2: args.comments
        }

        return switch.get(index)

    ### Create either Subreddit, Redditor, or posts list.
    def create_list(self, args, l_type):
        index = self._s_t.index(l_type)
        list = [item[0] for item in GetScrapeSettings._list_switch(args, index)]

        return list

    ### Get Subreddit settings.
    @staticmethod
    def _subreddit_settings(args, master):
        for sub_n in master:
            for sub in args.subreddit:
                settings = [sub[1], sub[2]]
                if sub_n == sub[0]:
                    master[sub_n].append(settings)

    ### Get settings for scraping items that only require two arguments 
    ### (Redditor or comments scrapers).
    @staticmethod
    def _two_arg_settings(master, object):
        for obj in object:
            master[obj[0]] = obj[1]

    ### Get CLI scraping settings for Subreddits, Redditors, and post comments.
    def get_settings(self, args, master, reddit, s_type):
        if s_type == self._s_t[0]:
            GetScrapeSettings._subreddit_settings(args, master)
        elif s_type == self._s_t[1]:
            GetScrapeSettings._two_arg_settings(master, args.redditor)
        elif s_type == self._s_t[2]:
            GetScrapeSettings._two_arg_settings(master, args.comments)

class CheckCli():
    """
    Functions for checking CLI arguments and raising errors if they are invalid.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._short_cat = Global.short_cat

    ### Check Subreddit args
    def _check_subreddit(self, args):
        for subs in args.subreddit:
            if subs[1].upper() not in self._short_cat:
                raise ValueError
            elif subs[1].upper() in self._short_cat:
                if subs[1].upper() != "S":
                    try:
                        int(subs[2])
                    except ValueError:
                        raise ValueError

    ### Check Redditor args
    @staticmethod
    def _check_redditor(args):
        for users in args.redditor:
            if users[1].isalpha() or int(users[1]) == 0:
                raise ValueError

    ### Check args for items that only require two arguments (Redditor or 
    ### comments scrapers).
    @staticmethod
    def _check_comments(args):
        for comments in args.comments:
            if comments[1].isalpha():
                raise ValueError

    ### Check args and catching errors.
    @LogError.log_args
    def check_args(self, args, parser):
        if args.subreddit:
            self._check_subreddit(args)
        if args.redditor:
            CheckCli._check_redditor(args)
        if args.comments:
            CheckCli._check_comments(args)
