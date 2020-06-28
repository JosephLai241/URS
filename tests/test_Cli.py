import argparse
import pytest
import re
import sys

from urs.utils import Cli, Global

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of 44 tests.

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
        usage = "$ Urs.py [-h] [-r SUBREDDIT [H|N|C|T|R|S] RESULTS_OR_KEYWORDS OPTIONAL_TIME_FILTER] [-u USER RESULTS] [-c URL RESULTS] [-b] [-y] [--csv|--json]"
        
        assert Cli.Parser()._usage == usage
        
    def test_parser_init_method_description_instance_variable(self):
        description = r"""
Universal Reddit Scraper 3.1.1 - Scrape Subreddits, Redditors, or submission comments

Author: Joseph Lai
Contact: urs_project@protonmail.com
"""
        assert Cli.Parser()._description == description

    def test_parser_init_method_epilog_instance_variable(self):
        epilog = r"""
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
        assert Cli.Parser()._epilog == epilog

class TestParserAddFlagsMethod():
    """
    Testing Parser class _add_flags() method found on line 74 in Cli.py.
    """

    def test_add_flags_method_subreddit_flag(self):
        test_subreddit_args = [["test_subreddit", "h", "10"]]
        
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_flags(parser)

        args = parser.parse_args("--subreddit test_subreddit h 10".split())

        assert args.subreddit == test_subreddit_args

    def test_add_flags_method_redditor_flag(self):
        test_subreddit_args = [["test_redditor", "10"]]
        
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_flags(parser)

        args = parser.parse_args("--redditor test_redditor 10".split())

        assert args.redditor == test_subreddit_args

    def test_add_flags_method_comments_flag(self):
        test_subreddit_args = [["test_url", "10"]]
        
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

    def test_parse_args_method_no_args_were_entered(self):
        sys.argv = [sys.argv[0]]

        try:
            _, _ = Cli.Parser().parse_args()
            assert False
        except SystemExit:
            assert True

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

    def test_subreddit_settings_one_subreddit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        master = {"test_subreddit": []}
        Cli.GetScrapeSettings()._subreddit_settings(args, master)

        assert master == {"test_subreddit": [["h", "10", None]]}

class TestGetScrapeSettingsTwoArgsSettingsMethod():
    """
    Testing GetScrapeSettings class _two_arg_settings() method found on line 170
    in Cli.py.
    """

    def test_two_arg_settings_one_arg_redditor(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])
        master = {"test_redditor": None}
        Cli.GetScrapeSettings()._two_arg_settings(master, args.redditor)

        assert master == {"test_redditor": "10"}

    def test_two_arg_settings_one_arg_comments(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["test_url", "2"]])
        master = {"test_url": None}
        Cli.GetScrapeSettings()._two_arg_settings(master, args.comments)

        assert master == {"test_url": "2"}

class TestGetScrapeSettingsGetSettingsMethod():
    """
    Testing GetScrapeSettings class get_settings() method found on line 175 in 
    Cli.py.
    """

    def test_get_settings_with_subreddit_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        master = {"test_subreddit": []}
        s_type = Global.s_t[0]
        Cli.GetScrapeSettings().get_settings(args, master, s_type)

        assert master == {"test_subreddit": [["h", "10", None]]}

    def test_get_settings_with_redditor_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])
        master = {"test_redditor": None}
        s_type = Global.s_t[1]
        Cli.GetScrapeSettings().get_settings(args, master, s_type)

        assert master == {"test_redditor": "10"}

    def test_get_settings_with_comments_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["test_url", "2"]])
        master = {"test_url": None}
        s_type = Global.s_t[2]
        Cli.GetScrapeSettings().get_settings(args, master, s_type)

        assert master == {"test_url": "2"}

class TestCheckCliInitMethod():
    """
    Testing CheckCli class __init__() method found on line 189 in Cli.py.
    """

    def test_check_cli_init_method_short_cat_instance_variable(self):
        assert Cli.CheckCli()._short_cat == Global.short_cat

    def test_check_cli_init_method_special_chars_instance_variable(self):
        assert Cli.CheckCli()._special_chars == \
            re.compile("[@_!#$%^&*()<>?/\\|}{~:+`=]")

class TestCheckCliCheckSubredditMethod():
    """
    Testing CheckCli class _check_subreddit() method found on line 193 in Cli.py.
    """

    def test_check_subreddit_with_correct_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        Cli.CheckCli()._check_subreddit(args)

        assert args.subreddit == [["test_subreddit", "h", "10"]]

    def test_check_subreddit_with_invalid_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "w", "asdf"]])
        
        try:
            Cli.CheckCli()._check_subreddit(args)
            assert False
        except ValueError:
            assert True

class TestCheckCliCheckRedditorMethod():
    """
    Testing CheckCli class _check_redditor() method found on line 205 in Cli.py.
    """

    def test_check_redditor_with_correct_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])
        Cli.CheckCli()._check_redditor(args)

        assert args.redditor == [["test_redditor", "10"]]

    def test_check_redditor_with_invalid_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["10", "test_redditor"]])
        
        try:
            Cli.CheckCli()._check_redditor(args)
            assert False
        except ValueError:
            assert True

class TestCheckCliCheckCommentsMethod():
    """
    Testing CheckCli class _check_comments() method found on line 212 in Cli.py.
    """

    def test_check_comments_with_correct_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["test_url", "2"]])
        Cli.CheckCli()._check_comments(args)

        assert args.comments == [["test_url", "2"]]

    def test_check_comments_with_invalid_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["2", "test_url"]])
        
        try:
            Cli.CheckCli()._check_comments(args)
            print(args.comments)
            assert False
        except ValueError:
            assert True

class TestCheckCliCheckArgsMethod():
    """
    Testing CheckCli class check_args() method found on line 224 in Cli.py.
    """

    def test_check_args_with_valid_subreddit_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])

        Cli.CheckCli().check_args(args, parser)

        assert args.subreddit == [["test_subreddit", "h", "10"]] 

    def test_check_args_with_invalid_subreddit_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "w", "asdf"]])

        try:
            Cli.CheckCli().check_args(args, parser)
            assert False
        except SystemExit:
            assert True

    def test_check_args_with_valid_redditor_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])

        Cli.CheckCli().check_args(args, parser)

        assert args.redditor == [["test_redditor", "10"]]

    def test_check_args_with_invalid_redditor_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["10", "test_redditor"]])

        try:
            Cli.CheckCli().check_args(args, parser)
            assert False
        except SystemExit:
            assert True

    def test_check_args_with_valid_comments_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["test_url", "2"]])

        Cli.CheckCli().check_args(args, parser)

        assert args.comments == [["test_url", "2"]]

    def test_check_args_with_invalid_comments_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["2", "test_url"]])

        try:
            Cli.CheckCli().check_args(args, parser)
            assert False
        except SystemExit:
            assert True
