import argparse
import pytest
import sys

from urs.utils import Cli, Global

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of  tests.

class MakeArgs():
    """
    Making dummy args to test Cli.py functions.
    """

    @staticmethod
    def parser_for_testing_cli():
        parser = argparse.ArgumentParser()
        return parser

    @staticmethod
    def make_scraper_args():
        parser = MakeArgs.parser_for_testing_cli()
        parser.add_argument("--subreddit", nargs = 1)
        parser.add_argument("--redditor", nargs = 1)
        parser.add_argument("--comments", nargs = 1)

        return parser

class TestParserInitMethod():
    """
    Testing Parser class __init__() method found on line 17 in Cli.py.
    """

    def test_parser_init_method_usage_instance_variable(self):
        usage = "$ Urs.py [-h] [-r SUBREDDIT [H|N|C|T|R|S] RESULTS_OR_KEYWORDS] [-u USER RESULTS] [-c URL RESULTS] [-b] [-y] [--csv|--json]"
        
        assert Cli.Parser()._usage == usage
        
    def test_parser_init_method_description_instance_variable(self):
        description = r"""
Universal Reddit Scraper 3.1 - Scrape Subreddits, Redditors, or submission comments

Author: Joseph Lai
Contact: urs_project@protonmail.com
"""
        assert Cli.Parser()._description == description

    def test_parser_init_method_epilog_instance_variable(self):
        epilog = r"""
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
        assert Cli.Parser()._epilog == epilog

class TestParserAddFlagsMethod():
    """
    Testing Parser class _add_flags() method found on line 74 in Cli.py.
    """

    def test_add_flags_method_subreddit_flag(self):
        test_subreddit_args = [['test_subreddit', 'h', '10']]
        
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_flags(parser)

        args = parser.parse_args("--subreddit test_subreddit h 10".split())

        assert args.subreddit == test_subreddit_args

    def test_add_flags_method_redditor_flag(self):
        test_subreddit_args = [['test_redditor', '10']]
        
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_flags(parser)

        args = parser.parse_args("--redditor test_redditor 10".split())

        assert args.redditor == test_subreddit_args

    def test_add_flags_method_comments_flag(self):
        test_subreddit_args = [['test_url', '10']]
        
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_flags(parser)

        args = parser.parse_args("--comments test_url 10".split())

        assert args.comments == test_subreddit_args

    def test_add_flags_method_basic_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_flags(parser)

        args = parser.parse_args(["--basic"])

        assert args.basic == True

    def test_add_flags_method_skip_confirmation_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_flags(parser)

        args = parser.parse_args(["-y"])

        assert args.y == True

class TestParserAddExportMethod():
    """
    Testing Parser class _add_export() method found on line 104 in Cli.py.
    """

    def test_add_export_method_csv_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_export(parser)

        args = parser.parse_args(["--csv"])

        assert args.csv == True

    def test_add_export_method_json_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_export(parser)

        args = parser.parse_args(["--json"])

        assert args.json == True

class TestParserParseArgsMethod():
    """
    Testing Parser class parse_args() method found on line 116 in Cli.py.
    """

    def test_parse_args_method_subreddit_and_json_flags(self):
        input_args = ["--subreddit", "test_subreddit", "h", "10", "--json"]
        for arg in input_args:
            sys.argv.append(arg)

        sys.argv = sys.argv[1:]

        args, _ = Cli.Parser().parse_args()
        
        assert args.subreddit == [["test_subreddit", "h", "10"]]
        assert args.json == True

    def test_parse_args_method_subreddit_and_csv_flags(self):
        sys.argv = [sys.argv[0]]
        input_args = ["--subreddit", "test_subreddit", "h", "10", "--csv"]
        for arg in input_args:
            sys.argv.append(arg)

        args, _ = Cli.Parser().parse_args()
        
        assert args.subreddit == [["test_subreddit", "h", "10"]]
        assert args.csv == True

    def test_parse_args_method_redditor_and_json_flags(self):
        sys.argv = [sys.argv[0]]
        input_args = ["--redditor", "test_redditor", "10", "--json"]
        for arg in input_args:
            sys.argv.append(arg)

        args, _ = Cli.Parser().parse_args()
        
        assert args.redditor == [["test_redditor", "10"]]
        assert args.json == True

    def test_parse_args_method_redditor_and_csv_flags(self):
        sys.argv = [sys.argv[0]]
        input_args = ["--redditor", "test_redditor", "10", "--csv"]
        for arg in input_args:
            sys.argv.append(arg)

        args, _ = Cli.Parser().parse_args()
        
        assert args.redditor == [["test_redditor", "10"]]
        assert args.csv == True

    def test_parse_args_method_comments_and_json_flags(self):
        sys.argv = [sys.argv[0]]
        input_args = ["--comments", "test_url", "10", "--json"]
        for arg in input_args:
            sys.argv.append(arg)

        args, _ = Cli.Parser().parse_args()
        
        assert args.comments == [["test_url", "10"]]
        assert args.json == True

    def test_parse_args_method_comments_and_csv_flags(self):
        sys.argv = [sys.argv[0]]
        input_args = ["--comments", "test_url", "10", "--csv"]
        for arg in input_args:
            sys.argv.append(arg)

        args, _ = Cli.Parser().parse_args()
        
        assert args.comments == [["test_url", "10"]]
        assert args.csv == True

class TestGetScrapeSettingsInitMethod():
    """
    Testing GetScrapeSettings class __init__() method found on line 134 in Cli.py.
    """

    def test_get_scrape_settings_init_method_s_t_instance_variable(self):
        assert Cli.GetScrapeSettings()._s_t == Global.s_t

class TestGetScrapeSettingsListSwitchMethod():
    """
    Testing GetScrapeSettings class _list_switch() method found on line 144 in 
    Cli.py.
    """

    def test_list_switch_method_first_switch(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--subreddit", "test_subreddit"])
        index = 0

        assert Cli.GetScrapeSettings()._list_switch(args, index) == \
            ["test_subreddit"]
    
    def test_list_switch_method_second_switch(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--redditor", "test_redditor"])
        index = 1

        assert Cli.GetScrapeSettings()._list_switch(args, index) == \
            ["test_redditor"]

    def test_list_switch_method_third_switch(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--comments", "test_url"])
        index = 2

        assert Cli.GetScrapeSettings()._list_switch(args, index) == \
            ["test_url"]

class TestGetScrapeSettingsCreateListMethod():
    """
    Testing GetScrapeSettings class create_list() method found on line 154 in 
    Cli.py.
    """

    def test_create_list_from_subreddit_args(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        l_type = "subreddit"

        assert Cli.GetScrapeSettings().create_list(args, l_type) == \
            ["test_subreddit"]

    def test_create_list_from_redditor_args(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])
        l_type = "redditor"

        assert Cli.GetScrapeSettings().create_list(args, l_type) == \
            ["test_redditor"]

    def test_create_list_from_comments_args(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--comments", ["test_url", "10"]])
        l_type = "comments"

        assert Cli.GetScrapeSettings().create_list(args, l_type) == \
            ["test_url"]

class TestGetScrapeSettingsSubredditSettingsMethod():
    """
    Testing GetScrapeSettings class _subreddit_settings() method found on line 
    161 in Cli.py.
    """

