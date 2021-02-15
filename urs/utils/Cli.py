"""
Command-line interface
======================
Methods defining the command-line interface for this program.
"""


import argparse
import re
import sys

from colorama import (
    init, 
    Fore, 
    Style
)

from utils.Global import (
    s_t,
    short_cat
)
from utils.Logger import LogError

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class Parser():
    """
    Methods for parsing CLI arguments.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._usage = r"""$ Urs.py
     
    [-h]
    [-e]

    [--check]

    [-r SUBREDDIT [H|N|C|T|R|S] N_RESULTS_OR_KEYWORDS OPTIONAL_TIME_FILTER] 
    [--rules]
    [-u USER N_RESULTS] 
    [-c URL N_RESULTS] 
    [-b]

    [-f FILE]
    [-ch FILE OPTIONAL_EXPORT_FORMAT] 
    [-wc FILE OPTIONAL_EXPORT_FORMAT OPTIONAL_MASK_IMAGE]
    [--nosave]

    [-y]

    [--csv] 
"""
        self._description = r"""
Universal Reddit Scraper v3.1.3 - a comprehensive Reddit scraping tool

Author: Joseph Lai
Contact: urs_project@protonmail.com
"""
        self._epilog = r"""
[PRAW SUBREDDIT SCRAPING]

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

[ANALYTICAL TOOLS]

chart and wordcloud export options:
    eps     Encapsulated Postscript
    jpg
    jpeg
    pdf
    pgf     PGF code for LaTeX
    png
    ps      Postscript
    raw     Raw RGBA bitmap
    rgba    Raw RGBA bitmap
    svg
    svgz
    tif
    tiff
"""
        self._examples = r"""
[[EXAMPLES]]

[PRAW SCRAPING]

SUBREDDITS

    Get the first 10 posts in r/askreddit in the Hot category and export to JSON:

        $ ./Urs.py -r askreddit h 10

    Search for "United States of America" in r/worldnews and export to CSV:

        $ ./Urs.py -r worldnews s "United States of America" --csv

    You can apply a time filter when scraping Subreddit categories Controversial, Top, or Search:
    (Scraping Search results from r/learnprogramming from the past month)

        $ ./Urs.py -r learnprogramming s "python developer" month

    You can add the Subreddit's rules in the scrape results by providing the `--rules` flag. This only works when you export to JSON:

        $ ./Urs.py -r wallstreetbets t 25 --rules

    You can also still use URS 1.0 (SUBREDDIT SCRAPING ONLY), but you cannot include this flag with any items besides export options:

        $ ./Urs.py -b

        $ ./Urs.py -b --csv

REDDITORS

    Scraping 15 results from u/spez's Reddit account:

        $ ./Urs.py -u spez 15

SUBMISSION COMMENTS

    Scraping 25 comments from this r/TIFU post:
    (Returns a structured JSON file that includes down to third-level replies)

        $ ./Urs.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 25

    Scraping all comments from the same r/TIFU post:
    (Returns an unstructured JSON file of all comments in level order, ie. top-level first, followed by second-level, then third-level, etc.)

        $ ./Urs.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 0

COMBINING SCRAPERS

    You can scrape multiple items at once:

        $ ./Urs.py -r askreddit h 15 -u spez 25 -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 50

[ANALYTICAL TOOLS]

WORD FREQUENCIES

    Only return a count of words that are present in submission titles, bodies, and/or comments. An example file path is given:

        $ ./Urs.py -f ../scrapes/02-15-2020/subreddits/askreddit-hot-100-results.json

WORDCLOUD

    You can also generate a wordcloud based on word frequencies:
    
        $ ./Urs.py -wc ../scrapes/02-15-2020/subreddits/askreddit-hot-100-results.json

CHART

    Or you can create a bar chart based on word frequencies:

        $ ./Urs.py -ch ../scrapes/02-15-2020/subreddits/askreddit-hot-100-results.json

    If you do not wish to save the chart or wordcloud to file, provide the `--nosave` flag:

        $ ./Urs.py -wc ../scrapes/02-15-2020/subreddits/askreddit-hot-100-results.json --nosave

        $ ./Urs.py -ch ../scrapes/02-15-2020/subreddits/askreddit-hot-100-results.json --nosave

"""

    ### Add flag to print examples.
    def _add_examples_flag(self, parser):
        example_flag = parser.add_argument_group("display examples")
        example_flag.add_argument(
            "-e", "--examples", 
            action = "store_true", 
            help = "display example use cases"
        )

    ### Print usage, then examples.
    def _display_examples(self):
        print(self._usage)
        print(self._examples)

    ### Add flag to check rate limit information.
    def _add_rate_limit_check_flag(self, parser):
        rate_flag = parser.add_argument_group("check rate limit")
        rate_flag.add_argument(
            "--check",
            action = "store_true",
            help = "display rate limit information for your Reddit account"
        )

    ### Add PRAW scraper flags - Subreddit, Redditor, comments, basic scraper, 
    ### and skip confirmation flags.
    def _add_praw_scraper_flags(self, parser):
        praw_flags = parser.add_argument_group("PRAW scraping")
        praw_flags.add_argument(
            "-r", "--subreddit", 
            action = "append", 
            help = "specify Subreddit to scrape",
            metavar = "", 
            nargs = "+"
        ) 
        praw_flags.add_argument(
            "-u", "--redditor", 
            action = "append", 
            help = "specify Redditor profile to scrape",
            metavar = "", 
            nargs = 2
        ) 
        praw_flags.add_argument(
            "-c", "--comments", 
            action = "append", 
            help = "specify the URL of the submission to scrape comments",
            metavar = "", 
            nargs = 2
        ) 
        praw_flags.add_argument(
            "-b", "--basic", 
            action = "store_true", 
            help = "initialize non-CLI Subreddit scraper"
        )
    
    ### Add extra options for PRAW Subreddit scraping.
    def _add_praw_subreddit_options(self, parser):
        subreddit_flags = parser.add_argument_group("additional PRAW Subreddit scraping arguments")
        subreddit_flags.add_argument(
            "--rules",
            action = "store_true",
            help = "include Subreddit rules in scrape data"
        )

    ### Add analytical flags - wordcloud, chart, and save flags.
    def _add_analytics(self, parser):
        analyze_flags = parser.add_argument_group("analytical tools")
        analyze_flags.add_argument(
            "-f", "--frequencies",
            action = "append",
            help = "get word frequencies present in submission titles, bodies, and/or comments",
            metavar = "", 
            nargs = 1
        )
        analyze_flags.add_argument(
            "-wc", "--wordcloud",
            action = "append",
            help = "create a wordcloud for a scrape file",
            metavar = "", 
            nargs = "+"
        )
        analyze_flags.add_argument(
            "-ch", "--chart",
            action = "append",
            help = "create a chart for a scrape file",
            metavar = "", 
            nargs = "+"
        )
        analyze_flags.add_argument(
            "--nosave",
            action = "store_true",
            help = "do not save wordcloud or chart to file"
        )

    ### Add skip confirmation flags.
    def _add_skip(self, parser):
        skip_flags = parser.add_argument_group("skip confirmation")
        skip_flags.add_argument(
            "-y", 
            action = "store_true", 
            help = "skip options confirmation and scrape immediately"
        )

    ### Add export flags.
    def _add_export(self, parser):
        export_flags = parser.add_argument_group("export arguments")
        export_flags.add_argument(
            "--csv", 
            action = "store_true", 
            help = "export scrape data to CSV instead (default is JSON)"
        )

    ### Get args.
    @LogError.log_no_args
    def parse_args(self):
        parser = argparse.ArgumentParser(
            description = self._description,
            epilog = self._epilog, 
            formatter_class = argparse.RawDescriptionHelpFormatter,
            usage = self._usage
        )

        self._add_examples_flag(parser)
        self._add_rate_limit_check_flag(parser)
        self._add_praw_scraper_flags(parser)
        self._add_praw_subreddit_options(parser)
        self._add_analytics(parser)
        self._add_skip(parser)
        self._add_export(parser)

        ### Print help message if no arguments are present.
        if len(sys.argv[1:]) == 0:
            parser.print_help()
            raise SystemExit

        args = parser.parse_args()

        ### Print examples if the flag is present.
        if args.examples:
            self._display_examples()
            raise SystemExit

        return args, parser

class GetPRAWScrapeSettings():
    """
    Methods for creating data structures to store PRAW scrape settings.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._filterables = [
            short_cat[2], 
            short_cat[3], 
            short_cat[5]
        ]

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
        index = s_t.index(l_type)
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
        if s_type == s_t[0]:
            self._subreddit_settings(args, master)
        elif s_type == s_t[1]:
            self._two_arg_settings(master, args.redditor)
        elif s_type == s_t[2]:
            self._two_arg_settings(master, args.comments)

class CheckPRAWCli():
    """
    Methods for checking CLI arguments for PRAW scrapers and raising errors if
    they are invalid.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._special_chars = re.compile("[@_!#$%^&*()<>?/\\|}{~:+`=]")
        
        self._filterables = [
            short_cat[2], 
            short_cat[3], 
            short_cat[5]
        ]
        self._time_filters = [
            "all", 
            "day", 
            "hour", 
            "month", 
            "week", 
            "year"
        ]

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
    def check_subreddit(self, args):
        for sub in args.subreddit:
            if sub[1].upper() not in short_cat or len(sub) > 4:
                raise ValueError
            elif sub[1].upper() in short_cat:
                ### Check args if a time filter is present.
                if len(sub) == 4:
                    if sub[1].upper() not in self._filterables \
                    or sub[3].lower() not in self._time_filters:
                        raise ValueError

                self._check_n_results(sub[2], sub)

    ### Check Redditor args.
    def check_redditor(self, args):
        for user in args.redditor:
            if user[1].isalpha() \
            or self._special_chars.search(user[1]) != None \
            or int(user[1]) == 0:
                raise ValueError

    ### Check submission comments args.
    def check_comments(self, args):
        for submission in args.comments:
            if submission[1].isalpha() \
            or self._special_chars.search(submission[1]) != None:
                raise ValueError

class CheckAnalyticCli():
    """
    Methods for checking CLI arguments for analytical tools and raising errors
    if they are invalid.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._export_options = [
            "eps",
            "jpg",
            "jpeg",
            "pdf",
            "pgf",
            "png",
            "ps",
            "raw",
            "rgba",
            "svg",
            "svgz",
            "tif",
            "tiff",
        ]

    ### Check valid files for generating charts or wordclouds.
    def _check_valid_file(self, file):
        try:
            _ = open("%s" % file)
        except FileNotFoundError:
            raise ValueError

    ### Check if export format is valid.
    def _check_valid_export(self, export_option):
        if export_option not in self._export_options:
            raise ValueError

    ### Check frequencies args.
    def check_frequencies(self, args):
        for file in args.frequencies:
            self._check_valid_file(file[0])

    ### Check wordcloud args.
    def check_wordcloud(self, args):
        for file in args.wordcloud:
            if len(file) > 3:
                raise ValueError

            self._check_valid_file(file[0])

            if len(file) == 1:
                file.append("png")
            elif len(file) == 3:
                self._check_valid_file(file[2])
            
            file[1] = file[1].lower()
            self._check_valid_export(file[1])

    ### Check chart args.
    def check_chart(self, args):
        for file in args.chart:
            if len(file) > 2:
                raise ValueError
            
            self._check_valid_file(file[0])
            
            if len(file) == 1:
                file.append("png")
            else:
                self._check_valid_export(file[1])

class CheckCli():
    """
    Methods for checking CLI arguments and raising errors if they are invalid.
    """

    ### Check args and catching errors.
    @LogError.log_args
    def check_args(self, args, parser):
        ### Check PRAW CLI arguments.
        if args.subreddit:
            CheckPRAWCli().check_subreddit(args)
        if args.redditor:
            CheckPRAWCli().check_redditor(args)
        if args.comments:
            CheckPRAWCli().check_comments(args)
        
        ### Check analytical tool arguments.
        if args.frequencies:
            CheckAnalyticCli().check_frequencies(args)
        if args.wordcloud:
            CheckAnalyticCli().check_wordcloud(args)
        if args.chart:
            CheckAnalyticCli().check_chart(args)
