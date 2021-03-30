"""
Testing `Export.py`.
"""


import argparse
import csv
import json
import os
import sys

from urs.utils import (
    Export, 
    Global
)

class MakeArgs():
    """
    Making dummy args to test Export.py functions.
    """

    @staticmethod
    def parser_for_testing_export():
        parser = argparse.ArgumentParser()
        parser.add_argument("--subreddit", action = "store_true")
        parser.add_argument("--basic", action = "store_true")
        parser.add_argument("--rules", action = "store_true")

        parser.add_argument("--raw", action = "store_true")

        return parser

class TestFix():
    """
    Testing _fix() function on line 30 in Export.py.
    """

    def test_fix(self):
        name = "/t\\e?s%t*i:n|g<c@h!a#r$ac^t&e*(r)s>}{~+`="
        fixed = "_t_e_s_t_i_n_g_c_h_a_r_ac_t_e__r_s_______"

        assert fixed == Export.NameFile()._fix(name)

class TestRCategory():
    """
    Testing _r_category() function on line 40 in Export.py.
    """

    def test_r_category_first_switch(self):
        assert Export.NameFile()._r_category("H", 0) == Global.categories[5]

    def test_r_category_second_switch(self):
        for index, category in enumerate(Global.short_cat[:5]):
            assert Export.NameFile()._r_category(category, 1) == Global.categories[index]

class TestRGetCategory():
    """
    Testing _r_get_category() function on line 54 in Export.py.
    """
                
    def test_r_get_category_subreddit_arg_returns_zero(self):
        assert Export.NameFile()._r_get_category("S") == 0

    def test_r_get_category_subreddit_arg_returns_one(self):
        assert Export.NameFile()._r_get_category("C") == 1

class TestGetRawN():
    """
    Testing _get_raw_n() function on line 80 in Export.py.
    """

    def test_get_raw_n_returns_search_filename_format_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "S"
        end = "result"
        each_sub = ["s", "test", "all"]
        sub = "askreddit"

        assert Export.NameFile()._get_raw_n(args, cat_i, end, each_sub, sub) == \
            "askreddit-search-'test'"

    def test_get_raw_n_returns_category_filename_format_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "H"
        end = "result"
        each_sub = ["h", "1", None]
        sub = "askreddit"

        assert Export.NameFile()._get_raw_n(args, cat_i, end, each_sub, sub) == \
            "askreddit-hot-1-result"

class TestRFname():
    """
    Testing r_fname() function on line 103 in Export.py.
    """

    def test_r_fname_ignores_end_string_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "S"
        each_sub = ["s", "test", "all"]
        sub = "askreddit"

        assert Export.NameFile().r_fname(args, cat_i, each_sub, sub) == \
            "askreddit-search-'test'"

    def test_r_fname_returns_plural_string_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "H"
        each_sub = ["h", 5, None]
        sub = "askreddit"

        assert Export.NameFile().r_fname(args, cat_i, each_sub, sub) == \
            "askreddit-hot-5-results"

    def test_r_fname_returns_non_plural_string_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "H"
        each_sub = ["h", 1, None]
        sub = "askreddit"

        assert Export.NameFile().r_fname(args, cat_i, each_sub, sub) == \
            "askreddit-hot-1-result"

class TestUFname():
    """
    Testing u_fname() function on line 116 in Export.py.
    """

    def test_u_fname_returns_plural_string(self):
        limit = 2
        string = "test"

        assert Export.NameFile().u_fname(limit, string) == "test-2-results"

    def test_u_fname_returns_non_plural_string(self):
        limit = 1
        string = "test"

        assert Export.NameFile().u_fname(limit, string) == "test-1-result"

class TestCFname():
    """
    Testing c_fname() function on line 126 in Export.py.
    """

    def test_c_fname_returns_plural_string_with_raw_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--raw"])
        limit = 2
        string = "test"

        assert Export.NameFile().c_fname(args, limit, string) == "test-2-results-raw"

    def test_c_fname_returns_plural_string_with_structured_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args()
        limit = 2
        string = "test"

        assert Export.NameFile().c_fname(args, limit, string) == "test-2-results"

    def test_c_fname_returns_non_plural_string_with_raw_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--raw"])
        limit = 1
        string = "test"

        assert Export.NameFile().c_fname(args, limit, string) == "test-1-result-raw"

    def test_c_fname_returns_non_plural_string_with_structured_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args()
        limit = 1
        string = "test"

        assert Export.NameFile().c_fname(args, limit, string) == "test-1-result"

    def test_c_fname_returns_all_comments_with_raw_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--raw"])
        limit = 0
        string = "test"

        assert Export.NameFile().c_fname(args, limit, string) == "test-all-raw"
    
    def test_c_fname_returns_all_comments_with_structured_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args()
        limit = 0
        string = "test"

        assert Export.NameFile().c_fname(args, limit, string) == "test-all"

class TestWriteCSVAndWriteJSON():
    """
    Testing write_csv() function on line 153 and write_json() function on line 
    161 in Export.py.
    """

    def test_write_csv(self):
        filename = os.path.join(sys.path[0], "test_csv_writing.csv")
        overview = {
            "this": [1, 2],
            "is": [3, 4],
            "a": [5, 6],
            "test": [7, 8]}

        Export.Export.write_csv(overview, filename)

        with open(filename, "r") as test_csv:
            reader = csv.reader(test_csv)
            test_dict = dict((header, []) for header in next(reader))
            for row in reader:
                for row_index, key in enumerate(test_dict.keys()):
                    test_dict[key].append(int(row[row_index]))

        assert test_dict == overview
        os.remove(filename)

    def test_write_json(self):
        filename = os.path.join(sys.path[0], "test_json_writing.json")
        overview = {
            'test_1': {'this': 1, 'is': 1, 'a': 1, 'test': 1},
            'test_2': {'this': 2, 'is': 2, 'a': 2, 'test': 2}
        }

        Export.Export.write_json(overview, filename)

        with open(filename, "r") as test_json:
            test_dict = json.load(test_json)

        assert test_dict == overview
        os.remove(filename)

class TestGetFilenameExtension():
    """
    Test _get_filename_extension() function on line 144 in Export.py.
    """

    def test_get_filename_extension_returns_subreddits_csv(self):
        f_name = "test"
        f_type = "csv"

        assert Export.Export._get_filename_extension(f_name, f_type, "subreddits") == "../scrapes/%s/subreddits/%s.csv" % (Global.date, f_name)

    def test_get_filename_extension_returns_redditors_csv(self):
        f_name = "test"
        f_type = "csv"

        assert Export.Export._get_filename_extension(f_name, f_type, "redditors") == "../scrapes/%s/redditors/%s.csv" % (Global.date, f_name)

    def test_get_filename_extension_returns_comments_csv(self):
        f_name = "test"
        f_type = "csv"

        assert Export.Export._get_filename_extension(f_name, f_type, "comments") == "../scrapes/%s/comments/%s.csv" % (Global.date, f_name)

    def test_get_filename_extension_returns_subreddits_json(self):
        f_name = "test"
        f_type = "json"

        assert Export.Export._get_filename_extension(f_name, f_type, "subreddits") == "../scrapes/%s/subreddits/%s.json" % (Global.date, f_name)

    def test_get_filename_extension_returns_redditors_json(self):
        f_name = "test"
        f_type = "json"

        assert Export.Export._get_filename_extension(f_name, f_type, "redditors") == "../scrapes/%s/redditors/%s.json" % (Global.date, f_name)

    def test_get_filename_extension_returns_comments_json(self):
        f_name = "test"
        f_type = "json"

        assert Export.Export._get_filename_extension(f_name, f_type, "comments") == "../scrapes/%s/comments/%s.json" % (Global.date, f_name)
