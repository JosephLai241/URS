#===============================================================================
#                       Command-line Interface Functions
#===============================================================================
import argparse
import sys

from colorama import Fore, init, Style
from . import Global, Titles, Validation

### Automate sending reset sequences to turn off color changes at the end of 
### every print
init(autoreset = True)

class Parser():
    """
    Function for parsing CLI arguments.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self.usage = "scraper.py [-h] [-r SUBREDDIT [H|N|C|T|R|S] RESULTS_OR_KEYWORDS] [-u USER RESULTS] [-c URL RESULTS] [-b] [-y] [--csv|--json]"
        self.description = "Universal Reddit Scraper 3.0 - Scrape Subreddits, submissions, Redditors, or comments from posts"
        self.epilog = r"""
Subreddit categories:
   H,h     selecting Hot category
   N,n     selecting New category
   C,c     selecting Controversial category
   T,t     selecting Top category
   R,r     selecting Rising category
   S,s     selecting Search category

EXAMPLES

    Get the first 10 posts in r/all in the Hot category and export to JSON:

        $ ./scraper.py -r all h 10 --json

    Search for "United States of America" in r/worldnews and export to CSV:

        $ ./scraper.py -r worldnews s "United States of America" --csv

    Scraping 50 results from u/spez's Reddit account:

        $ ./scraper.py -u spez 50 --json

    Scraping 25 comments from this r/TIFU post:

        $ ./scraper.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 25 --csv

    You can scrape multiple items at once:

        $ ./scraper.py -r askreddit h 15 -u spez 25 -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 50 --json

    You can also still use URS 1.0 (SUBREDDIT SCRAPING ONLY), but you cannot include this flag with any items besides export options:

        $ ./scraper.py -b --csv

"""

    ### Get args.
    def parse_args(self):
        parser = argparse.ArgumentParser(usage = self.usage,
                                        formatter_class = argparse.RawDescriptionHelpFormatter,
                                        description = self.description,
                                        epilog = self.epilog)

        ### Parser Subreddit, Redditor, comments, basic scraper, and skip 
        ### confirmation flags.
        scraper = parser.add_argument_group("Scraping options")
        scraper.add_argument("-r", "--subreddit", action = "append", nargs = 3, metavar = "", 
                                help = "specify Subreddit to scrape")
        scraper.add_argument("-u", "--redditor", action = "append", nargs = 2, metavar = "", 
                                help = "specify Redditor profile to scrape")
        scraper.add_argument("-c", "--comments", action = "append", nargs = 2, metavar = "", 
                                help = "specify the URL of the post to scrape comments")
        scraper.add_argument("-b", "--basic", action = "store_true", 
                                help = "initialize non-CLI Subreddit scraper")
        scraper.add_argument("-y", action = "store_true", 
                                help = "skip Subreddit options confirmation and scrape immediately")

        ### Export to CSV or JSON flags.
        expt = parser.add_mutually_exclusive_group(required = True)
        expt.add_argument("--csv", action = "store_true", help = "export to CSV")
        expt.add_argument("--json", action = "store_true", help = "export to JSON")

        ### Print help message if no arguments are present.
        if len(sys.argv[1:]) == 0:
            parser.print_help()
            parser.exit()

        args = parser.parse_args()
        return args, parser

class GetScrapeSettings():
    """
    Functions for creating data structures to store scrape settings
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self.s_t = Global.s_t

    ### Switch to determine which kind of list to create.
    def list_switch(self, args, index):
        switch = {
            0: args.subreddit,
            1: args.redditor,
            2: args.comments
        }

        return switch.get(index)

    ### Create either Subreddit, Redditor, or posts list.
    def create_list(self, args, l_type):
        index = self.s_t.index(l_type)
        list = [item[0] for item in self.list_switch(args, index)]

        return list

    ### Get Subreddit settings.
    def subreddit_settings(self, args, master):
        for sub_n in master:
            for sub in args.subreddit:
                settings = [sub[1], sub[2]]
                if sub_n == sub[0]:
                    master[sub_n].append(settings)

    ### Get settings for scraping items that only require two arguments 
    ### (Redditor or comments scrapers).
    def two_arg_settings(self, master, object):
        for obj in object:
            master[obj[0]] = obj[1]

    # ### Switch to determine how to loop through CLI scraping settings.
    # def settings_switch(self, args, index, master):
    #     scrape_switch = {
    #         0: self.subreddit_settings(args, master) if args.subreddit else None,
    #         1: self.two_arg_settings(master, args.redditor) if args.redditor else None,
    #         2: self.two_arg_settings(master, args.comments) if args.comments else None
    #     }

    #     return scrape_switch.get(index)

    ### Get CLI scraping settings for Subreddits, Redditors, and post comments.
    def get_settings(self, args, master, reddit, s_type):
        if s_type == self.s_t[0]:
            self.subreddit_settings(args, master)
        elif s_type == self.s_t[1]:
            self.two_arg_settings(master, args.redditor)
        elif s_type == self.s_t[2]:
            self.two_arg_settings(master, args.comments)

class CheckCli():
    """
    Function for checking CLI arguments and raising errors if they are invalid.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self.short_cat = Global.short_cat

    ### Check Subreddit args
    def check_subreddit(self, args):
        for subs in args.subreddit:
            if subs[1].upper() not in self.short_cat:
                raise ValueError
            elif subs[1].upper() in self.short_cat:
                if subs[1].upper() != "S":
                    try:
                        int(subs[2])
                    except ValueError:
                        raise ValueError

    ### Check args for items that only require two arguments (Redditor or 
    ### comments scrapers).
    def check_two_arg(self, object):
        for obj in object:
            if obj[1].isalpha():
                raise ValueError

    ### Check args and catching errors.
    def check_args(self, args, parser):
        try:
            if args.subreddit:
                self.check_subreddit(args)
            if args.redditor:
                self.check_two_arg(args.redditor)
            if args.comments:
                self.check_two_arg(args.comments)
        except ValueError:
            Titles.Titles().e_title()
            parser.exit()

