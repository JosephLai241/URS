"""
Testing `Cli.py`.
"""


import argparse
import re
import sys

import pytest

from urs.utils import Cli, Global
from urs.Version import __version__


class MakeArgs:
    """
    Making dummy args to test Cli.py methods.
    """

    @staticmethod
    def parser_for_testing_cli():
        parser = argparse.ArgumentParser()
        return parser

    @staticmethod
    def make_scraper_args():
        parser = MakeArgs.parser_for_testing_cli()
        parser.add_argument("--subreddit", nargs=1)
        parser.add_argument("--redditor", nargs=1)
        parser.add_argument("--comments", nargs=1)
        parser.add_argument("--frequencies", nargs=1)
        parser.add_argument("--wordcloud", nargs=1)

        return parser


class TestParserInitMethod:
    """
    Testing Parser class __init__() method.
    """

    def test_parser_init_method_usage_instance_variable(self):
        usage = r"""$ Urs.py
     
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
    [-wc <file_path> [<optional_export_format>]]
        [--nosave]
"""

        assert Cli.Parser()._usage == usage

    def test_parser_init_method_description_instance_variable(self):
        description = r"""
Universal Reddit Scraper v{} - a comprehensive Reddit scraping tool

Author: Joseph Lai
Contact: urs_project@protonmail.com
""".format(
            __version__
        )
        assert Cli.Parser()._description == description

    def test_parser_init_method_epilog_instance_variable(self):
        epilog = r"""
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
        assert Cli.Parser()._epilog == epilog

    def test_parser_init_method_examples_instance_variable(self):
        examples = r"""
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

        assert Cli.Parser()._examples == examples


class TestParserAddExamplesFlagMethod:
    """
    Testing Parser class _add_examples_flag() method.
    """

    def test_add_examples_flag_method_examples_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_examples_flag(parser)

        args = parser.parse_args(["-e"])

        assert args.examples == True


class TestParserAddRateLimitCheckFlagMethod:
    """
    Testing Parser class _add_rate_limit_check_flag() method.
    """

    def test_add_examples_flag_method_examples_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_rate_limit_check_flag(parser)

        args = parser.parse_args(["--check"])

        assert args.check == True


class TestParserAddPrawScraperFlagsMethod:
    """
    Testing Parser class _add_praw_scraper_flags() method.
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


class TestParserAddPrawSubredditOptionsFlagMethod:
    """
    Testing Parser class _add_praw_subreddit_options() method.
    """

    def test_add_praw_subreddit_options_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_praw_subreddit_options(parser)

        args = parser.parse_args(["--rules"])

        assert args.rules == True


class TestParserAddPrawCommentsOptionsFlagMethod:
    """
    Testing Parser class _add_praw_comments_options() method.
    """

    def test_add_praw_comments_options_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_praw_comments_options(parser)

        args = parser.parse_args(["--raw"])

        assert args.raw == True


class TestParserAddPrawLivestreamFlags:
    """
    Testing Parser class _add_praw_livestream_flags() method.
    """

    def test_add_praw_livestream_flags_method_live_subreddit_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_praw_livestream_flags(parser)

        args = parser.parse_args("--live-subreddit askreddit".split())

        assert args.live_subreddit == "askreddit"

    def test_add_praw_livestream_flags_method_live_redditor_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_praw_livestream_flags(parser)

        args = parser.parse_args("--live-redditor spez".split())

        assert args.live_redditor == "spez"


class TestParserAddPrawLivestreamOptions:
    """
    Testing Parser class _add_praw_livestream_options() method.
    """

    def test_add_praw_livestream_options_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_praw_livestream_options(parser)

        args = parser.parse_args(["--stream-submissions"])

        assert args.stream_submissions == True


class TestParserAddAnalyticsFlagMethod:
    """
    Testing Parser class _add_analytics() method.
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


class TestParserAddExtraOptionsMethod:
    """
    Testing Parser class _add_extra_options() method.
    """

    def test_add_extra_options_method_skip_confirmation_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_extra_options(parser)

        args = parser.parse_args(["-y"])

        assert args.y == True

    def test_add_extra_options_method_nosave_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_extra_options(parser)

        args = parser.parse_args(["--nosave"])

        assert args.nosave == True


class TestParserAddExportMethod:
    """
    Testing Parser class _add_export() method.
    """

    def test_add_export_method_csv_flag(self):
        parser = MakeArgs.parser_for_testing_cli()
        Cli.Parser()._add_export(parser)

        args = parser.parse_args(["--csv"])

        assert args.csv == True


class TestParserParseArgsMethod:
    """
    Testing Parser class parse_args() method.
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

    def test_parse_args_method_examples_flag_was_included(self):
        sys.argv = [sys.argv[0]]
        sys.argv.append("-e")

        try:
            _, _ = Cli.Parser().parse_args()
        except SystemExit:
            assert True

        sys.argv = [sys.argv[0]]


class TestGetPRAWScrapeSettingsListSwitchMethod:
    """
    Testing GetPRAWScrapeSettings class _list_switch() method.
    """

    def test_list_switch_method_first_switch(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--subreddit", "test_subreddit"])
        index = 0

        assert Cli.GetPRAWScrapeSettings()._list_switch(args, index) == [
            "test_subreddit"
        ]

    def test_list_switch_method_second_switch(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--redditor", "test_redditor"])
        index = 1

        assert Cli.GetPRAWScrapeSettings()._list_switch(args, index) == [
            "test_redditor"
        ]

    def test_list_switch_method_third_switch(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--comments", "test_url"])
        index = 2

        assert Cli.GetPRAWScrapeSettings()._list_switch(args, index) == ["test_url"]


class TestGetPRAWScrapeSettingsCreateListMethod:
    """
    Testing GetPRAWScrapeSettings class create_list() method.
    """

    def test_create_list_from_subreddit_args(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        l_type = "subreddit"

        assert Cli.GetPRAWScrapeSettings().create_list(args, l_type) == [
            "test_subreddit"
        ]

    def test_create_list_from_redditor_args(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])
        l_type = "redditor"

        assert Cli.GetPRAWScrapeSettings().create_list(args, l_type) == [
            "test_redditor"
        ]

    def test_create_list_from_comments_args(self):
        parser = MakeArgs.make_scraper_args()

        args = parser.parse_args(["--comments", ["test_url", "10"]])
        l_type = "comments"

        assert Cli.GetPRAWScrapeSettings().create_list(args, l_type) == ["test_url"]


class TestGetPRAWScrapeSettingsSetSubSettings:
    """
    Testing GetPRAWScrapeSettings class _set_sub_settings() method.
    """

    def test_set_sub_settings_len_is_three_with_filterable_category(self):
        sub = ["test_one", "C", "20"]

        settings = Cli.GetPRAWScrapeSettings()._set_sub_settings(sub)

        assert ["C", "20", "all"] == settings

    def test_set_sub_settings_len_is_three_with_non_filterable_category(self):
        sub = ["test_one", "H", "20"]

        settings = Cli.GetPRAWScrapeSettings()._set_sub_settings(sub)

        assert ["H", "20", None] == settings

    def test_set_sub_settings_len_is_four(self):
        sub = ["test_one", "S", "20", "day"]

        settings = Cli.GetPRAWScrapeSettings()._set_sub_settings(sub)

        assert ["S", "20", "day"] == settings


class TestGetPRAWScrapeSettingsSubredditSettingsMethod:
    """
    Testing GetPRAWScrapeSettings class _subreddit_settings() method.
    """

    def test_subreddit_settings_one_subreddit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        master = {"test_subreddit": []}
        invalids = []
        Cli.GetPRAWScrapeSettings()._subreddit_settings(
            args.subreddit, invalids, master
        )

        assert master == {"test_subreddit": [["h", "10", None]]}


class TestGetPRAWScrapeSettingsTwoArgsSettingsMethod:
    """
    Testing GetPRAWScrapeSettings class _two_arg_settings() method.
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


class TestGetPRAWScrapeSettingsGetSettingsMethod:
    """
    Testing GetPRAWScrapeSettings class get_settings() method.
    """

    def test_get_settings_with_subreddit_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        master = {"test_subreddit": []}
        s_type = "subreddit"
        invalids = []
        Cli.GetPRAWScrapeSettings().get_settings(args, invalids, master, s_type)

        assert master == {"test_subreddit": [["h", "10", None]]}

    def test_get_settings_with_redditor_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])
        master = {"test_redditor": None}
        s_type = "redditor"
        invalids = []
        Cli.GetPRAWScrapeSettings().get_settings(args, invalids, master, s_type)

        assert master == {"test_redditor": "10"}

    def test_get_settings_with_comments_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["test_url", "2"]])
        master = {"test_url": None}
        s_type = "comments"
        invalids = []
        Cli.GetPRAWScrapeSettings().get_settings(args, invalids, master, s_type)

        assert master == {"test_url": "2"}


class TestCheckPRAWCliInitMethod:
    """
    Testing CheckPRAWCli class __init__() method.
    """

    def test_check_praw_cli_init_method_illegal_chars_instance_variable(self):
        assert Cli.CheckPRAWCli()._illegal_chars == re.compile(
            "[@_!#$%^&*()<>?/\\|}{~:+`=]"
        )

    def test_check_praw_cli_init_method_filterables_instance_variable(self):
        assert Cli.CheckPRAWCli()._filterables == [
            Global.short_cat[2],
            Global.short_cat[3],
            Global.short_cat[5],
        ]

    def test_check_praw_cli_init_method_time_filters_instance_variable(self):
        assert Cli.CheckPRAWCli()._time_filters == [
            "all",
            "day",
            "hour",
            "month",
            "week",
            "year",
        ]


class TestCheckPRAWCliCheckNResultsMethod:
    """
    Testing CheckPRAWCli class _check_n_results() method.
    """

    def test_check_n_results_invalid_int(self):
        n_results = "a"
        sub = ["test", "H", "100"]

        try:
            Cli.CheckPRAWCli()._check_n_results(n_results, sub)
            assert False
        except SystemExit:
            assert True

    def test_check_n_results_invalid_n_results(self):
        n_results = "0"
        sub = ["test", "H", "asdf"]

        try:
            Cli.CheckPRAWCli()._check_n_results(n_results, sub)
            assert False
        except SystemExit:
            assert True

    def test_check_n_results_valid_n_results(self):
        n_results = "10"
        sub = ["test", "H", "10"]

        try:
            Cli.CheckPRAWCli()._check_n_results(n_results, sub)
            assert True
        except SystemExit:
            assert False


class TestCheckPRAWCliCheckSubredditMethod:
    """
    Testing CheckPRAWCli class check_subreddit() method.
    """

    def test_check_subreddit_without_time_filter_with_correct_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])
        Cli.CheckPRAWCli().check_subreddit(args)

        assert args.subreddit == [["test_subreddit", "h", "10"]]

    def test_check_subreddit_without_time_filter_with_invalid_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "w", "asdf"]])

        try:
            Cli.CheckPRAWCli().check_subreddit(args)
            assert False
        except SystemExit:
            assert True

    def test_check_subreddit_time_filter_applied_to_invalid_category(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10", "year"]])

        try:
            Cli.CheckPRAWCli().check_subreddit(args)
            assert False
        except SystemExit:
            assert True

    def test_check_subreddit_with_time_filter_with_correct_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(
            ["--subreddit", ["test_subreddit", "s", "test", "year"]]
        )

        assert args.subreddit == [["test_subreddit", "s", "test", "year"]]

    def test_check_subreddit_with_time_filter_with_invalid_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(
            ["--subreddit", ["test_subreddit", "s", "test", "asdf"]]
        )

        try:
            Cli.CheckPRAWCli().check_subreddit(args)
            assert False
        except SystemExit:
            assert True


class TestCheckPRAWCliCheckRedditorMethod:
    """
    Testing CheckPRAWCli class check_redditor() method.
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


class TestCheckPRAWCliCheckCommentsMethod:
    """
    Testing CheckPRAWCli class check_comments() method.
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
            assert False
        except SystemExit:
            assert True


class TestCheckAnalyticCliInitMethod:
    """
    Testing CheckAnalyticCli class __init__() method.
    """

    def test_check_analytic_cli_init_method_export_options_instance_variable(self):
        assert Cli.CheckAnalyticCli()._export_options == [
            "eps",
            "jpeg",
            "jpg",
            "pdf",
            "png",
            "ps",
            "rgba",
            "tif",
            "tiff",
        ]


class TestCheckAnalyticCliCheckFrequenciesMethod:
    """
    Testing CheckAnalyticCli class check_frequencies() method.
    """

    def test_check_frequencies_with_valid_file(self):
        pass

    def test_check_frequencies_with_invalid_file(self):
        pass


class TestCheckAnalyticCliCheckWordcloudMethod:
    """
    Testing CheckAnalyticCli class check_wordcloud() method.
    """

    def test_check_wordcloud_len_is_greater_than_two(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--wordcloud", ["test_file", "png", "asdf"]])

        try:
            Cli.CheckAnalyticCli().check_wordcloud(args)
            assert False
        except SystemExit:
            assert True

    def test_check_wordcloud_with_valid_file(self):
        pass

    def test_check_wordcloud_with_invalid_file(self):
        pass


class TestCheckCliCheckArgsMethod:
    """
    Testing CheckCli class check_args() method.
    """

    def test_check_args_with_valid_subreddit_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "h", "10"]])

        Cli.CheckCli().check_args(args)

        assert args.subreddit == [["test_subreddit", "h", "10"]]

    def test_check_args_with_invalid_subreddit_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", ["test_subreddit", "w", "asdf"]])

        try:
            Cli.CheckCli().check_args(args)
            assert False
        except SystemExit:
            assert True

    def test_check_args_with_valid_redditor_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["test_redditor", "10"]])

        Cli.CheckCli().check_args(args)

        assert args.redditor == [["test_redditor", "10"]]

    def test_check_args_with_invalid_redditor_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--redditor", ["10", "test_redditor"]])

        try:
            Cli.CheckCli().check_args(args)
            assert False
        except SystemExit:
            assert True

    def test_check_args_with_valid_comments_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["test_url", "2"]])

        Cli.CheckCli().check_args(args)

        assert args.comments == [["test_url", "2"]]

    def test_check_args_with_invalid_comments_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--comments", ["2", "test_url"]])

        try:
            Cli.CheckCli().check_args(args)
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
