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
        parser.add_argument("--frequencies", nargs = 1)
        parser.add_argument("--wordcloud", nargs = 1)

        return parser

class TestParserInitMethod():
    """
    Testing Parser class __init__() method found on line 31 in Cli.py.
    """

    def test_parser_init_method_usage_instance_variable(self):
        usage = r"""$ Urs.py
     
    [-h]
    [-e]

    [--check]

    [-r SUBREDDIT [H|N|C|T|R|S] N_RESULTS_OR_KEYWORDS OPTIONAL_TIME_FILTER] 
    [--rules]
    [-u USER N_RESULTS] 
    [-c URL N_RESULTS] 
    [-b]

    [-f FILE_PATH]
    [-wc FILE_PATH OPTIONAL_EXPORT_FORMAT]
    [--nosave]

    [-y]

    [--csv] 
"""
        
        assert Cli.Parser()._usage == usage
        
    def test_parser_init_method_description_instance_variable(self):
        description = r"""
Universal Reddit Scraper v3.2.0 - a comprehensive Reddit scraping tool

Author: Joseph Lai
Contact: urs_project@protonmail.com
"""
        assert Cli.Parser()._description == description

    def test_parser_init_method_epilog_instance_variable(self):
        epilog = r"""
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
        assert Cli.Parser()._epilog == epilog

    def test_parser_init_method_examples_instance_variable(self):
        examples = r"""
[[EXAMPLES]]

[PRAW SCRAPING]

Arguments:

    [-r SUBREDDIT [H|N|C|T|R|S] N_RESULTS_OR_KEYWORDS OPTIONAL_TIME_FILTER] 
    [--rules]
    [-u USER N_RESULTS] 
    [-c URL N_RESULTS] 
    [-b]

    [-y]

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

    Scraping 25 comments from this r/TIFU post.
    Returns a structured JSON file that includes down to third-level replies:

        $ ./Urs.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 25

    Scraping all comments from the same r/TIFU post.
    Returns an unstructured JSON file of all comments in level order, 
    ie. top-level first, followed by second-level, then third-level, etc.:

        $ ./Urs.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 0

[ANALYTICAL TOOLS]

Arguments:

    [-f FILE_PATH]
    [-wc FILE_PATH OPTIONAL_EXPORT_FORMAT]
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

"""

        assert Cli.Parser()._examples == examples

class TestParserAddExamplesFlagMethod():
    """
    Testing Parser class _add_examples_flag() method found on line 208 in Cli.py.
    """

    def test_add_examples_flag_method_examples_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_examples_flag(parser)

        args = parser.parse_args(["-e"])

        assert args.examples == True

class TestParserAddRateLimitCheckFlagMethod():
    """
    Testing Parser class _add_rate_limit_check_flag() method found on line 208 
    in Cli.py.
    """

    def test_add_examples_flag_method_examples_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_rate_limit_check_flag(parser)

        args = parser.parse_args(["--check"])

        assert args.check == True

class TestParserAddPrawScraperFlagsMethod():
    """
    Testing Parser class _add_praw_scraper_flags() method found on line 232 in Cli.py.
    """

    def test_add_praw_scraper_flags_method_subreddit_flag(self):
        test_subreddit_args = [["test_subreddit", "h", "10"]]
        
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_praw_scraper_flags(parser)

        args = parser.parse_args("--subreddit test_subreddit h 10".split())

        assert args.subreddit == test_subreddit_args

    def test_add_praw_scraper_flags_method_redditor_flag(self):
        test_subreddit_args = [["test_redditor", "10"]]
        
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_praw_scraper_flags(parser)

        args = parser.parse_args("--redditor test_redditor 10".split())

        assert args.redditor == test_subreddit_args

    def test_add_praw_scraper_flags_method_comments_flag(self):
        test_subreddit_args = [["test_url", "10"]]
        
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_praw_scraper_flags(parser)

        args = parser.parse_args("--comments test_url 10".split())

        assert args.comments == test_subreddit_args

    def test_add_praw_scraper_flags_method_basic_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_praw_scraper_flags(parser)

        args = parser.parse_args(["--basic"])

        assert args.basic == True

class TestParserAddPrawSubredditOptionsFlagMethod():
    """
    Testing Parser class _add_praw_subreddit_options() method found on line 294 in Cli.py.
    """

    def test_add_skip_method_skip_confirmation_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_praw_subreddit_options(parser)

        args = parser.parse_args(["--rules"])

        assert args.rules == True

class TestParserAddAnalyticsFlagMethod():
    """
    Testing Parser class _add_analytics() method found on line 271 in Cli.py.
    """

    def test_add_analytics_method_frequencies_flag(self):
        test_subreddit_args = [["test_file"]]
        
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_analytics(parser)

        args = parser.parse_args("--frequencies test_file".split())

        assert args.frequencies == test_subreddit_args

    def test_add_analytics_method_wordcloud_flag(self):
        test_subreddit_args = [["test_file"]]
        
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_analytics(parser)

        args = parser.parse_args("--wordcloud test_file".split())

        assert args.wordcloud == test_subreddit_args

    def test_add_analytics_method_nosave_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_analytics(parser)

        args = parser.parse_args(["--nosave"])

        assert args.nosave == True

class TestParserAddSkipFlagMethod():
    """
    Testing Parser class _add_skip() method found on line 294 in Cli.py.
    """

    def test_add_skip_method_skip_confirmation_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_skip(parser)

        args = parser.parse_args(["-y"])

        assert args.y == True

class TestParserAddExportMethod():
    """
    Testing Parser class _add_export() method found on line 132 in Cli.py.
    """

    def test_add_export_method_csv_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_export(parser)

        args = parser.parse_args(["--csv"])

        assert args.csv == True

class TestParserParseArgsMethod():
    """
    Testing Parser class parse_args() method found on line 147 in Cli.py.
    """

    def test_parse_args_method_subreddit_and_csv_flags(self):
        sys.argv = [sys.argv[0]]
        input_args = ["--subreddit", "test_subreddit", "h", "10", "--csv"]
        for arg in input_args:
            sys.argv.append(arg)

        args, _ = Cli.Parser().parse_args()
        
        assert args.subreddit == [["test_subreddit", "h", "10"]]
        assert args.csv == True

    def test_parse_args_method_redditor_flag(self):
        sys.argv = [sys.argv[0]]
        input_args = ["--redditor", "test_redditor", "10"]
        for arg in input_args:
            sys.argv.append(arg)

        args, _ = Cli.Parser().parse_args()
        
        assert args.redditor == [["test_redditor", "10"]]
        assert args.csv == False

    def test_parse_args_method_comments_flag(self):
        sys.argv = [sys.argv[0]]
        input_args = ["--comments", "test_url", "10"]
        for arg in input_args:
            sys.argv.append(arg)

        args, _ = Cli.Parser().parse_args()
        
        assert args.comments == [["test_url", "10"]]
        assert args.csv == False

    def test_parse_args_method_no_args_were_entered(self):
        sys.argv = [sys.argv[0]]

        try:
            _, _ = Cli.Parser().parse_args()
            assert False
        except SystemExit:
            assert True

class TestGetPRAWScrapeSettingsListSwitchMethod():
    """
    Testing GetPRAWScrapeSettings class _list_switch() method found on line 183 in 
    Cli.py.
    """

    def test_list_switch_method_first_switch(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--subreddit", "test_subreddit"])
        index = 0

        assert Cli.GetPRAWScrapeSettings()._list_switch(args, index) == \
            ["test_subreddit"]
    
    def test_list_switch_method_second_switch(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--redditor", "test_redditor"])
        index = 1

        assert Cli.GetPRAWScrapeSettings()._list_switch(args, index) == \
            ["test_redditor"]

    def test_list_switch_method_third_switch(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--comments", "test_url"])
        index = 2

        assert Cli.GetPRAWScrapeSettings()._list_switch(args, index) == \
            ["test_url"]

class TestGetPRAWScrapeSettingsCreateListMethod():
    """
    Testing GetPRAWScrapeSettings class create_list() method found on line 193 in 
    Cli.py.
    """

    def test_create_list_from_subreddit_args(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        l_type = "subreddit"

        assert Cli.GetPRAWScrapeSettings().create_list(args, l_type) == \
            ["test_subreddit"]

    def test_create_list_from_redditor_args(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])
        l_type = "redditor"

        assert Cli.GetPRAWScrapeSettings().create_list(args, l_type) == \
            ["test_redditor"]

    def test_create_list_from_comments_args(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--comments", ["test_url", "10"]])
        l_type = "comments"

        assert Cli.GetPRAWScrapeSettings().create_list(args, l_type) == \
            ["test_url"]

class TestGetPRAWScrapeSettingsSubredditSettingsMethod():
    """
    Testing GetPRAWScrapeSettings class _subreddit_settings() method found on line 
    212 in Cli.py.
    """

    def test_subreddit_settings_one_subreddit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        master = {"test_subreddit": []}
        invalids = []
        Cli.GetPRAWScrapeSettings()._subreddit_settings(args.subreddit, invalids, master)

        assert master == {"test_subreddit": [["h", "10", None]]}

class TestGetPRAWScrapeSettingsTwoArgsSettingsMethod():
    """
    Testing GetPRAWScrapeSettings class _two_arg_settings() method found on line 222
    in Cli.py.
    """

    def test_two_arg_settings_one_arg_redditor(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])
        master = {"test_redditor": None}
        invalids = []
        Cli.GetPRAWScrapeSettings()._two_arg_settings(args.redditor, invalids, master)

        assert master == {"test_redditor": "10"}

    def test_two_arg_settings_one_arg_comments(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["test_url", "2"]])
        master = {"test_url": None}
        invalids = []
        Cli.GetPRAWScrapeSettings()._two_arg_settings(args.comments, invalids, master)

        assert master == {"test_url": "2"}

class TestGetPRAWScrapeSettingsGetSettingsMethod():
    """
    Testing GetPRAWScrapeSettings class get_settings() method found on line 227 in 
    Cli.py.
    """

    def test_get_settings_with_subreddit_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        master = {"test_subreddit": []}
        s_type = Global.s_t[0]
        invalids = []
        Cli.GetPRAWScrapeSettings().get_settings(args, invalids, master, s_type)

        assert master == {"test_subreddit": [["h", "10", None]]}

    def test_get_settings_with_redditor_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])
        master = {"test_redditor": None}
        s_type = Global.s_t[1]
        invalids = []
        Cli.GetPRAWScrapeSettings().get_settings(args, invalids, master, s_type)

        assert master == {"test_redditor": "10"}

    def test_get_settings_with_comments_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["test_url", "2"]])
        master = {"test_url": None}
        s_type = Global.s_t[2]
        invalids = []
        Cli.GetPRAWScrapeSettings().get_settings(args, invalids, master, s_type)

        assert master == {"test_url": "2"}

class TestCheckPRAWCliInitMethod():
    """
    Testing CheckPRAWCli class __init__() method found on line 241 in Cli.py.
    """

    def test_check_praw_cli_init_method_illegal_chars_instance_variable(self):
        assert Cli.CheckPRAWCli()._illegal_chars == \
            re.compile("[@_!#$%^&*()<>?/\\|}{~:+`=]")

    def test_check_praw_cli_init_method_filterables_instance_variable(self):
        assert Cli.CheckPRAWCli()._filterables == \
            [
                Global.short_cat[2], 
                Global.short_cat[3], 
                Global.short_cat[5]
            ]

    def test_check_praw_cli_init_method_time_filters_instance_variable(self):
        assert Cli.CheckPRAWCli()._time_filters == \
            [
                "all", 
                "day", 
                "hour", 
                "month", 
                "week", 
                "year"
            ]

class TestCheckPRAWCliCheckSubredditMethod():
    """
    Testing CheckPRAWCli class check_subreddit() method found on line 270 in Cli.py.
    """

    def test_check_subreddit_with_correct_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        Cli.CheckPRAWCli().check_subreddit(args)

        assert args.subreddit == [["test_subreddit", "h", "10"]]

    def test_check_subreddit_with_invalid_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "w", "asdf"]])
        
        try:
            Cli.CheckPRAWCli().check_subreddit(args)
            assert False
        except SystemExit:
            assert True

class TestCheckPRAWCliCheckRedditorMethod():
    """
    Testing CheckPRAWCli class check_redditor() method found on line 284 in Cli.py.
    """

    def test_check_redditor_with_correct_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])
        Cli.CheckPRAWCli().check_redditor(args)

        assert args.redditor == [["test_redditor", "10"]]

    def test_check_redditor_with_invalid_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["10", "test_redditor"]])
        
        try:
            Cli.CheckPRAWCli().check_redditor(args)
            assert False
        except SystemExit:
            assert True

class TestCheckPRAWCliCheckCommentsMethod():
    """
    Testing CheckPRAWCli class check_comments() method found on line 293 in Cli.py.
    """

    def test_check_comments_with_correct_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["test_url", "2"]])
        Cli.CheckPRAWCli().check_comments(args)

        assert args.comments == [["test_url", "2"]]

    def test_check_comments_with_invalid_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["2", "test_url"]])
        
        try:
            Cli.CheckPRAWCli().check_comments(args)
            print(args.comments)
            assert False
        except SystemExit:
            assert True

class TestCheckAnalyticCliInitMethod():
    """
    Testing CheckAnalyticCli class __init__() method found on line 479 in Cli.py.
    """

    def test_check_analytic_cli_init_method_export_options_instance_variable(self):
        assert Cli.CheckAnalyticCli()._export_options == \
            [
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

class TestCheckAnalyticCliCheckFrequenciesMethod():
    """
    Testing CheckAnalyticCli class check_frequencies() method found on line 500
    in Cli.py.
    """

    def test_check_frequencies_with_valid_file(self):
        pass

    def test_check_frequencies_with_invalid_file(self):
        pass

class TestCheckAnalyticCliCheckWordcloudMethod():
    """
    Testing CheckAnalyticCli class check_wordcloud() method found on line 505
    in Cli.py.
    """

    def test_check_wordcloud_with_valid_file(self):
        pass

    def test_check_wordcloud_with_invalid_file(self):
        pass

class TestCheckCliCheckArgsMethod():
    """
    Testing CheckCli class check_args() method found on line 301 in Cli.py.
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

    def test_check_args_with_valid_frequencies_args(self):
        pass

    def test_check_args_with_invalid_frequencies_args(self):
        pass

    def test_check_args_with_valid_wordcloud_args(self):
        pass

    def test_check_args_with_invalid_wordcloud_args(self):
        pass
    