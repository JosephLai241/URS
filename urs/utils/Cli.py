"""
Command-line interface
======================
Methods defining the command-line interface for this program.
"""


import argparse
import re
import sys
import time

from colorama import (
    Fore, 
    Style
)

from urs.Version import __version__

from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Global import (
    date,
    short_cat
)
from urs.utils.Logger import LogError

class Parser():
    """
    Methods for parsing CLI arguments.
    """

    def __init__(self):
        """
        Initialize variables used in the CLI:

            self._usage: list all available flags
            self._description: tool name and blurb, full name, author, and contact
            self._epilog: list additional options for tools
            self._examples: example usage

        Returns
        -------
        None
        """

        self._usage = r"""$ Urs.py
     
    [-h]
    [-e]
    [-v]

    [-t [<optional_date>]]
    [--check]

    [-r <subreddit> <(h|n|c|t|r|s)> <n_results_or_keywords> [<optional_time_filter>]] 
        [-y]
        [--csv]
        [--rules]
    [-u <redditor> <n_results>] 
    [-c <submission_url> <n_results>]
        [--raw] 
    [-b]
        [--csv]

    [-lr <subreddit>]
    [-lu <redditor>]

        [--nosave]
        [--stream-submissions]

    [-f <file_path>]
        [--csv]
    [-wc <file_path> [<optional_export_format>]
        [--nosave]
"""
        self._description = fr"""
Universal Reddit Scraper v{__version__} - a comprehensive Reddit scraping tool

Author: Joseph Lai
Contact: urs_project@protonmail.com
"""
        self._epilog = r"""
[PRAW SUBREDDIT SCRAPING]

Subreddit categories:
    h     selecting Hot category
    n     selecting New category
    c     selecting Controversial category (time filter available)
    t     selecting Top category           (time filter available)
    r     selecting Rising category
    s     selecting Search category        (time filter available)

Subreddit time filters:
    all (default)
    day
    hour
    month
    week
    year

[ANALYTICAL TOOLS]

wordcloud export options:
    eps     Encapsulated Postscript
    jpeg
    jpg
    pdf
    png
    ps      Postscript
    rgba    Raw RGBA bitmap
    tif
    tiff
"""
        self._examples = r"""
[[EXAMPLES]]

[PRAW SCRAPING]

Arguments:

    [-r <subreddit> <(h|n|c|t|r|s)> <n_results_or_keywords> [<optional_time_filter>]] 
        [-y]
        [--csv]
        [--rules]
    [-u <redditor> <n_results>] 
    [-c <submission_url> <n_results>]
        [--raw] 
    [-b]
        [--csv]

All scrape results are exported to JSON by default.

You can run all of these scrapers in one call.

SUBREDDITS

    Get the first 10 posts in r/askreddit in the Hot category and export to JSON:

        $ ./Urs.py -r askreddit h 10

    Search for "United States of America" in r/worldnews and export to CSV by including the `--csv` flag:

        $ ./Urs.py -r worldnews s "United States of America" --csv

    You can apply a time filter when scraping Subreddit categories Controversial, Top, or Search:
    (Scraping Search results from r/learnprogramming from the past month)

        $ ./Urs.py -r learnprogramming s "python developer" month

    You can skip the settings confirmation table and immediately scrape by including the `-y` flag:

        $ ./Urs.py -r cscareerquestions s "job" year -y

    You can add the Subreddit's rules in the scrape results by including the `--rules` flag. 
    This only works when you export to JSON:

        $ ./Urs.py -r wallstreetbets t 25 year --rules

    You can also still use URS v1.0.0 (SUBREDDIT SCRAPING ONLY), but you cannot include 
    this flag with any items besides export options:

        $ ./Urs.py -b

        $ ./Urs.py -b --csv

REDDITORS

    Scraping 15 results from u/spez's Reddit account:

        $ ./Urs.py -u spez 15

SUBMISSION COMMENTS

    Scraping 25 comments from this r/TIFU post. Returns a structured JSON file:

        $ ./Urs.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 25

    Scraping all comments from the same r/TIFU post. Returns a structured JSON file:
    
        $ ./Urs.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 0

    You can also return comments in raw format by including the `--raw` flag.
    Ie. top-level first, followed by second-level, then third-level, etc.:

        $ ./Urs.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 25 --raw
        
        $ ./Urs.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 0 --raw

[PRAW LIVESTREAM SCRAPING]

Arguments:

    [-lr <subreddit>]
    [-lu <redditor>]

        [--nosave]
        [--stream-submissions]

LIVE SUBREDDIT STREAM

    Livestream comments created in r/AskReddit. Writes livestream results to a JSON file:

        $ ./Urs.py -lr askreddit

    Or livestream submissions created in r/AskReddit:

        $ ./Urs.py -lr askreddit --stream-submissions

    If you do not want to save livestream results to file, include the `--nosave` flag:

        $ ./Urs.py -lr askreddit --stream-submissions --nosave

LIVE REDDITOR STREAM

    Livestream comments by u/spez. Writes livestream results to a JSON file:

        $ ./Urs.py -lu spez

    Or livestream submissions by u/spez:

        $ ./Urs.py -lu spez --stream-submissions

    If you do not want to save livestream results to file, include the `--nosave` flag:

        $ ./Urs.py -lu spez --stream-submissions --nosave

[ANALYTICAL TOOLS]

Arguments:

    [-f <file_path>]
        [--csv]
    [-wc <file_path> [<optional_export_format>]
        [--nosave]

Word frequencies are exported to JSON by default.

Wordclouds are exported to PNG by default.

You can run both of these tools in one call.

WORD FREQUENCIES

    Only return a count of words that are present in submission titles, bodies, and/or comments. 
    An example file path is given:

        $ ./Urs.py -f ../scrapes/02-15-2021/subreddits/askreddit-hot-100-results.json

    You can also export to CSV instead by including the `--csv` flag:

        $ ./Urs.py -f ../scrapes/02-15-2021/subreddits/askreddit-hot-100-results.json --csv

WORDCLOUD

    You can also generate a wordcloud based on word frequencies:
    
        $ ./Urs.py -wc ../scrapes/02-15-2021/subreddits/askreddit-hot-100-results.json

OPTIONAL EXPORT FORMAT

    You can export to formats other than PNG by providing the format after the file path.
    See the help menu for a full list of options. Exporting the wordcloud to JPG:

        $ ./Urs.py -wc ../scrapes/02-15-2021/subreddits/askreddit-hot-100-results.json jpg

DISPLAY INSTEAD OF SAVING

    If you do not wish to save the wordcloud to file, include the `--nosave` flag:

        $ ./Urs.py -wc ../scrapes/02-15-2021/subreddits/askreddit-hot-100-results.json --nosave

[UTILITIES]

Arguments:

    [-t [<optional_date>]]
    [--check]

DISPLAY SCRAPES DIRECTORY TREE

    You can display the scrapes directory tree for the current day by using the `-t` flag:

        $ ./Urs.py -t

    You can also include a date to display the directory tree for that date.
    The following date formats are accepted: MM-DD-YYYY, MM/DD/YYYY:

        $ ./Urs.py -t 06-02-2021
        $ ./Urs.py -t 06/02/2021

CHECK PRAW RATE LIMITS

    You can quickly check the rate limits for your account by using the `--check` flag:

        $ ./Urs.py --check

"""

    def _add_examples_flag(self, parser):
        """
        Add a flag to print example usage:

            -e: display usage (available options) and examples

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """

        example_flag = parser.add_argument_group("display examples")
        example_flag.add_argument(
            "-e", "--examples", 
            action = "store_true", 
            help = "display example use cases"
        )

    def _display_examples(self):
        """
        Print usage, followed by examples.

        Returns
        -------
        None
        """

        print(self._usage)
        print(self._examples)

    def _add_display_version(self, parser):
        """
        Add a flag to display the version number.

            -v: display the version number

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """

        version_flag = parser.add_argument_group("display the version number")
        version_flag.add_argument(
            "-v", "--version",
            action = "store_true",
            help = "display the version number"
        )

    def _add_rate_limit_check_flag(self, parser):
        """
        Add a flag to check rate limit information:

            --check: display rate limit information

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """
        
        rate_flag = parser.add_argument_group("check rate limit")
        rate_flag.add_argument(
            "--check",
            action = "store_true",
            help = "display rate limit information for your Reddit account"
        )

    def _add_display_scrapes_tree_flag(self, parser):
        """
        Add a flag to display the scrapes directory for a specific date.

            -t: display scrapes directory tree for a specific date (default is 
                the current day)

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """

        tree_flag = parser.add_argument_group("display scrapes directory tree")
        tree_flag.add_argument(
            "-t", "--tree",
            const = date,
            help = "display a visual directory tree for a date (default is the current day)",
            metavar = "<optional_date>",
            nargs = "?"
        )

    def _add_praw_scraper_flags(self, parser):
        """
        Add PRAW scraper flags:

            -r: Subreddit scraper
            -u: Redditor scraper
            -c: Submission comments scraper
            -b: Basic Subreddit scraper

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """

        praw_flags = parser.add_argument_group("PRAW scraping")
        praw_flags.add_argument(
            "-r", "--subreddit", 
            action = "append", 
            help = "specify Subreddit to scrape",
            metavar = ("<subreddit> <(h|n|c|t|r|s)> <n_results_or_keywords>", "<optional_time_filter>"), 
            nargs = "+"
        ) 
        praw_flags.add_argument(
            "-u", "--redditor", 
            action = "append", 
            help = "specify Redditor to scrape",
            metavar = ("<redditor>", "<n_results>"), 
            nargs = 2
        ) 
        praw_flags.add_argument(
            "-c", "--comments", 
            action = "append", 
            help = "specify the URL of the submission to scrape comments",
            metavar = ("<submission_url>", "<n_results>"), 
            nargs = 2
        ) 
        praw_flags.add_argument(
            "-b", "--basic", 
            action = "store_true", 
            help = "initialize interactive Subreddit scraper"
        )
    
    def _add_praw_subreddit_options(self, parser):
        """
        Add extra options for PRAW Subreddit scraping:

            --rules: include Subreddit rules and post requirements in scrape data

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """

        subreddit_flags = parser.add_argument_group("additional PRAW Subreddit scraping arguments (used with `-r`)")
        subreddit_flags.add_argument(
            "--rules",
            action = "store_true",
            help = "include Subreddit rules in scrape data"
        )

    def _add_praw_comments_options(self, parser):
        """
        Add extra options for PRAW submission comments scraping:

            --raw: return comments in raw format instead (default is structured)

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """

        comments_flags = parser.add_argument_group("additional PRAW submission comments scraping arguments (used with `-c`)")
        comments_flags.add_argument(
            "--raw",
            action = "store_true",
            help = "return comments in raw format instead (default is structured)"
        )

    def _add_praw_livestream_flags(self, parser):
        """
        Add PRAW livestream scraper flags.

            -lr: live Subreddit scraping
            -lu: live Redditor scraping

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """

        livestream_flags = parser.add_argument_group("PRAW livestream scraping")
        livestream_flags.add_argument(
            "-lr", "--live-subreddit",
            help = "specify Subreddit to livestream",
            metavar = "<subreddit>"
        )
        livestream_flags.add_argument(
            "-lu", "--live-redditor",
            help = "specify Redditor to livestream",
            metavar = "<redditor>"
        )

    def _add_praw_livestream_options(self, parser):
        """
        Add PRAW livestream options:

            --stream-submissions: livestream submissions (default is comments)
        """

        livestream_options = parser.add_argument_group("additional PRAW livestream scraping options (used with `-lr` or `-lu`)")
        livestream_options.add_argument(
            "--stream-submissions",
            action = "store_true",
            help = "livestream submissions instead (default is comments)"
        )

    def _add_analytics(self, parser):
        """
        Add flags for analytical tools:

            -f: word frequencies generator
            -w: wordcloud generator
            --nosave: do not save wordcloud to file

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """

        analyze_flags = parser.add_argument_group("analytical tools")
        analyze_flags.add_argument(
            "-f", "--frequencies",
            action = "append",
            help = "get word frequencies present in submission titles, bodies, and/or comments",
            metavar = "<file_path>", 
            nargs = 1
        )
        analyze_flags.add_argument(
            "-wc", "--wordcloud",
            action = "append",
            help = "create a wordcloud for a scrape file",
            metavar = ("<file_path>", "<optional_export_format>"), 
            nargs = "+"
        )

    def _add_extra_options(self, parser):
        """
        Add extra options for various flags:

            -y: skip settings confirmation and scrape immediately (used with `-r`)
            --nosave: display only; do not save to file (used with `-lr`, `-lu`, or `-wc`)

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """

        extra_flags = parser.add_argument_group("extra options")
        extra_flags.add_argument(
            "-y", 
            action = "store_true", 
            help = "skip settings confirmation and scrape immediately (used with `-r`)"
        )
        extra_flags.add_argument(
            "--nosave",
            action = "store_true",
            help = "display only; do not save to file (used with `-lr`, `-lu`, or `-wc`)"
        )

    def _add_export(self, parser):
        """
        Add export option flags:

            --csv: export scrape data to CSV instead (default is JSON)

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser instance

        Returns
        -------
        None
        """

        export_flags = parser.add_argument_group("export arguments (used with `-r`, `-b` or `-f`)")
        export_flags.add_argument(
            "--csv", 
            action = "store_true", 
            help = "export scrape data to CSV instead (default is JSON)"
        )

    @LogError.log_no_args
    def parse_args(self):
        """
        Parse arguments and combines previously defined private methods:

            self._add_examples_flag()
            self._add_rate_limit_check_flag()
            self._add_praw_scraper_flags()
            self._add_praw_subreddit_options()
            self._add_praw_comments_options()
            self._add_analytics()
            self._add_extra_options()
            self._add_export()

        Exceptions
        ----------
        SystemExit: 
            Raised when no arguments were entered or if the examples flag was provided

        Returns
        -------
        args: Namespace
            Namespace object containing all arguments that were defined in the
            previous private methods
        parser: ArgumentParser
            argparse ArgumentParser object
        """

        parser = argparse.ArgumentParser(
            description = self._description,
            epilog = self._epilog, 
            formatter_class = argparse.RawDescriptionHelpFormatter,
            usage = self._usage
        )

        self._add_examples_flag(parser)
        self._add_display_version(parser)
        self._add_rate_limit_check_flag(parser)
        self._add_display_scrapes_tree_flag(parser)

        self._add_praw_scraper_flags(parser)
        self._add_praw_subreddit_options(parser)
        self._add_praw_comments_options(parser)

        self._add_praw_livestream_flags(parser)
        self._add_praw_livestream_options(parser)

        self._add_analytics(parser)

        self._add_extra_options(parser)
        self._add_export(parser)

        ### Print help message if no arguments are present.
        if len(sys.argv[1:]) == 0:
            parser.print_help()
            raise SystemExit

        args = parser.parse_args()

        if args.examples:
            self._display_examples()
            raise SystemExit
        elif args.version:
            print(Fore.WHITE + Style.BRIGHT + f"Universal Reddit Scraper v{__version__}\n")
            raise SystemExit

        return args, parser

class GetPRAWScrapeSettings():
    """
    Methods for creating data structures to store PRAW scrape settings.
    """

    def __init__(self):
        """
        Initialize variables used when getting PRAW scrape settings:

            self._filterables: a list of categories for which time filters may be applied

        Returns
        -------
        None
        """

        self._filterables = [
            short_cat[2], 
            short_cat[3], 
            short_cat[5]
        ]

    def _list_switch(self, args, index):
        """
        Pythonic switch to determine which kind of args list to create:

            args.subreddit
            args.redditor
            args.comments

        Parameters
        ----------
        args: Namespace
            Namespace object containing Subreddit, Redditor, or submission comments
            arguments
        index: int
            Integer that corresponds with a dictionary key

        Returns
        -------
        args: Namespace
            Namespace object containing Subreddit, Redditor, or submission comments
            arguments
        """

        switch = {
            0: args.subreddit,
            1: args.redditor,
            2: args.comments
        }

        return switch.get(index)

    def create_list(self, args, l_type):
        """
        Create either Subreddits, Redditors, or submissions list.

        Calls previously defined private method:

            self._list_switch()

        Parameters
        ----------
        args: Namespace
            Namespace object containing Subreddit, Redditor, or submission comments
            arguments
        l_type: str
            String that denotes the scraper type (Subreddit, Redditor, or
            submission comments)

        Returns
        -------
        item_list: list
            List of split arguments containing the scraper flag and Reddit objects
            to scrape for
        """

        scraper_types = [
            "subreddit",
            "redditor",
            "comments"
        ]

        index = scraper_types.index(l_type)
        item_list = [item[0] for item in self._list_switch(args, index)]

        return item_list

    def _set_sub_settings(self, sub):
        """
        Set the default time filter if it can be applied to the Subreddit category.

        Parameters
        ----------
        sub: list
            A list containing the Subreddit name, category, and time filter (if
            applicable)

        Returns
        -------
        settings: list
            A list of corrected Subreddit scraping settings
        """

        if len(sub) == 3:
            time_filter = "all" \
                if sub[1].upper() in self._filterables \
                else None
            settings = [sub[1], sub[2], time_filter]
        if len(sub) == 4:
            settings = [sub[1], sub[2], sub[3]]

        return settings

    def _subreddit_settings(self, args, invalids, master):
        """
        Get Subreddit settings from the argparse Namespace and append them to the
        master scrape settings dictionary. Only appends settings for Subreddits
        that have been validated.

        Calls previously defined private method:

            self._set_sub_settings()

        Parameters
        ----------
        args: Namespace
            Namespace object containing Subreddit arguments
        invalids: list
            List containing invalid Subreddits
        master: dict
            Dictionary containing all scrape settings

        Returns
        -------
        None
        """

        for sub_n in master:
            for sub in args:
                if sub[0] not in invalids:
                    settings = self._set_sub_settings(sub)
                    
                    if sub_n == sub[0]:
                        master[sub_n].append(settings)

    def _two_arg_settings(self, args, invalids, master):
        """
        Get settings for scraping items that only require two arguments and append
        them to the master scrape settings dictionary:

            Redditor scraper
            Submission comments scraper

        Only appends settings for Redditors or submission URLs that have been 
        validated.

        Parameters
        ----------
        args: Namespace
            argparse Namespace object containing either Redditor or submission
            comments arguments
        invalids: list
            List containing invalid Reddit objects (Redditors or submission URLs)
        master: dict
            Dictionary containing all scrape settings

        Returns
        -------
        None
        """
        
        for arg in args:
            if arg[0] not in invalids:
                master[arg[0]] = arg[1]

    def get_settings(self, args, invalids, master, s_type):
        """
        Get scrape settings for Subreddits, Redditors and submission comments by
        combining all previously defined private methods:

            self._subreddit_settings()
            self._two_arg_settings()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI
        invalids: list
            List containing invalid Reddit objects (Subreddits, Redditors, or
            submission URLs)
        master: dict
            Dictionary containing all scrape settings
        s_type: str
            String that denotes the scraper type (Subreddit, Redditor, or
            submission comments)

        Returns
        -------
        None
        """

        if s_type == "subreddit":
            self._subreddit_settings(args.subreddit, invalids, master)
        elif s_type == "redditor":
            self._two_arg_settings(args.redditor, invalids, master)
        elif s_type == "comments":
            self._two_arg_settings(args.comments, invalids, master)

class CheckPRAWCli():
    """
    Methods for checking CLI arguments for PRAW scrapers and raising errors if
    they are invalid.
    """

    def __init__(self):
        """
        Initialize variables used when getting PRAW scrape settings:

            self._illegal_chars: a RegEx Pattern denoting forbidden characters
            self._filterables: a list of categories for which time filters may be applied
            self._time_filters: a list of valid time filters

        Returns
        -------
        None
        """

        self._illegal_chars = re.compile("[@_!#$%^&*()<>?/\\|}{~:+`=]")
        
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

    @LogError.log_args("SUBREDDIT N_RESULTS")
    def _check_n_results(self, n_results, sub):
        """
        Check n_results within Subreddit args.

        Parameters
        ----------
        n_results: str
            String denoting the number of results to return
        sub: list
            List of Subreddit scraping settings

        Exceptions
        ----------
        ValueError:
            Raised if n_results is invalid

        Returns
        -------
        None
        """
        
        if sub[1].upper() != "S":
            try:
                int(n_results)
                if int(n_results) == 0:
                    raise ValueError
            except ValueError:
                raise ValueError
    
    @LogError.log_args("SUBREDDIT ARGS")
    def check_subreddit(self, args):
        """
        Check all Subreddit args. 
        
        Calls previously defined private method:

            self._check_n_results()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI

        Exceptions
        ----------
        ValueError:
            Raised if category, n_results, or time filter is invalid

        Returns
        -------
        None
        """

        for sub in args.subreddit:
            if sub[1].upper() not in short_cat or len(sub) > 4:
                if sub[1].upper() not in short_cat:
                    print(Fore.RED + Style.BRIGHT + "\nINVALID CATEGORY.")
                raise ValueError
            elif sub[1].upper() in short_cat:
                ### Check args if a time filter is present.
                if len(sub) == 4:
                    if sub[1].upper() not in self._filterables \
                    or sub[3].lower() not in self._time_filters:
                        if sub[1].upper() not in self._filterables:
                            print(Fore.RED + Style.BRIGHT + "\nTIME FILTER IS NOT AVAILABLE FOR THIS CATEGORY.")
                        elif sub[3].lower() not in self._time_filters:
                            print(Fore.RED + Style.BRIGHT + "\nINVALID TIME FILTER.")
                        raise ValueError

                self._check_n_results(sub[2], sub)

    @LogError.log_args("REDDITOR ARGS")
    def check_redditor(self, args):
        """
        Check all Redditor args.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI

        Exceptions
        ----------
        ValueError:
            Raised if n_results is invalid

        Returns
        -------
        None
        """

        for user in args.redditor:
            if any(char.isalpha() for char in user[1]) \
            or self._illegal_chars.search(user[1]) != None \
            or int(user[1]) == 0:
                raise ValueError

    @LogError.log_args("SUBMISSION ARGS")
    def check_comments(self, args):
        """
        Check all submission comments args.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI

        Exceptions
        ----------
        ValueError:
            Raised if n_results is invalid

        Returns
        -------
        None
        """

        for submission in args.comments:
            if any(char.isalpha() for char in submission[1]) \
            or self._illegal_chars.search(submission[1]) != None:
                raise ValueError

class CheckAnalyticCli():
    """
    Methods for checking CLI arguments for analytical tools and raising errors
    if they are invalid.
    """

    def __init__(self):
        """
        Initialize variables used when getting PRAW scrape settings:

            self._export_options: a list of valid export options for wordclouds

        Returns
        -------
        None
        """

        self._export_options = [
            "eps",
            "jpeg",
            "jpg",
            "pdf",
            "png",
            "ps",
            "rgba",
            "tif",
            "tiff"
        ]

    def _check_valid_file(self, file):
        """
        Check valid files for generating wordclouds.

        Parameters
        ----------
        file: file system path
            A file path

        Exceptions
        ----------
        ValueError:
            Raised if an invalid file is provided

        Returns
        -------
        None
        """

        try:
            _ = open(f"{file}")
        except FileNotFoundError:
            raise ValueError

    @LogError.log_args("SCRAPE FILE FOR FREQUENCIES")
    def check_frequencies(self, args):
        """
        Check all frequencies args. 
        
        Calls previously defined private method:

            self._check_valid_file()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI

        Exceptions
        ----------
        ValueError:
            Raised if an invalid file is provided

        Returns
        -------
        None
        """

        for file in args.frequencies:
            self._check_valid_file(file[0])

    @LogError.log_args("SCRAPE FILE FOR WORDCLOUD")
    def check_wordcloud(self, args):
        """
        Check all wordcloud args. 
        
        Calls previously defined private method:

            self._check_valid_file()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI

        Exceptions
        ----------
        ValueError:
            Raised if too many args, an invalid file, or invalid export option
            is provided

        Returns
        -------
        None
        """

        for file in args.wordcloud:
            if len(file) > 2:
                raise ValueError
            
            self._check_valid_file(file[0])
            
            if len(file) == 1:
                file.append("png")
            else:
                if file[1].lower() not in self._export_options:
                    print(Fore.RED + Style.BRIGHT + "\nINVALID EXPORT OPTION.")
                    raise ValueError

                file[1] = file[1].lower()

class CheckCli():
    """
    Methods for checking CLI arguments and raising errors if they are invalid.
    """

    def check_args(self, args):
        """
        Check all arguments. Calls previously defined methods:

            CheckPRAWCli():
                check_subreddit()
                check_redditor()
                check_comments()

            CheckAnalyticCli():
                check_frequencies()
                check_wordcloud()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the
            previous private methods

        Exceptions
        ----------
        ValueError:
            Raised for any errors that were previously defined

        Returns
        -------
        None

        """

        ### Check PRAW arguments.
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
