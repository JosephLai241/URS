import argparse
import csv
import json
import os
import sys

from urs.utils import Export, Global

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of 26 tests.

class MakeArgs():
    """
    Making dummy args to test Export.py functions.
    """

    @staticmethod
    def parser_for_testing_export():
        parser = argparse.ArgumentParser()
        parser.add_argument("--subreddit", action = "store_true")
        parser.add_argument("--basic", action = "store_true")

        return parser

class TestFix():
    """
    Testing _fix() function on line 19 in Export.py.
    """

    def test_fix(self):
        name = "/t\\e?s%t*i:n|g<c@h!a#r$ac^t&e*(r)s>}{~+`="
        fixed = "_t_e_s_t_i_n_g_c_h_a_r_ac_t_e__r_s_______"

        assert fixed == Export.NameFile()._fix(name)

class TestRCategory():
    """
    Testing _r_category() function on line 24 in Export.py.
    """

    def test_r_category_first_switch(self):
        assert Export.NameFile()._r_category(None, 0) == Global.categories[5]

    def test_r_category_second_switch(self):
        for index, category in enumerate(Global.short_cat[:5]):
            assert Export.NameFile()._r_category(category, 1) == Global.categories[index]

    def test_r_category_third_switch(self):
        for i in range(0, len(Global.categories)):
            assert Export.NameFile()._r_category(i, 2) == Global.categories[i]

class TestRGetCategory():
    """
    Testing _r_get_category() function on line 38 in Export.py.
    """
                
    def test_r_get_category_subreddit_arg_returns_zero(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        assert Export.NameFile()._r_get_category(args, "S") == 0

    def test_r_get_category_subreddit_arg_returns_one(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        assert Export.NameFile()._r_get_category(args, "C") == 1

    def test_r_get_category_basic_arg_returns_two(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--basic"])
        assert Export.NameFile()._r_get_category(args, None) == 2

class TestGetRawNWithSubredditArgs():
    """
    Testing _get_raw_n() function on line 47 in Export.py.
    Testing with Subreddit args.
    """

    def test_get_raw_n_returns_search_filename_format_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "S"
        end = "result"
        each_sub = ["s", "test", "all"]
        sub = "askreddit"

        assert Export.NameFile()._get_raw_n(args, cat_i, end, each_sub, sub) == \
            "r-askreddit-Search-'test'"

    def test_get_raw_n_returns_category_filename_format_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "H"
        end = "result"
        each_sub = ["h", "1", None]
        sub = "askreddit"

        assert Export.NameFile()._get_raw_n(args, cat_i, end, each_sub, sub) == \
            "r-askreddit-Hot-1-result"

class TestGetRawNWithBasicArgs():
    """
    Testing _get_raw_n() function on line 47 in Export.py.
    Testing with Basic args.
    """

    def test_get_raw_n_returns_search_filename_format_with_basic_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--basic"])
        cat_i = 5
        end = "result"
        each_sub = ["s", "test", "all"]
        sub = "askreddit"

        assert Export.NameFile()._get_raw_n(args, cat_i, end, each_sub, sub) == \
            "r-askreddit-Search-'test'"

    def test_get_raw_n_returns_category_filename_format_with_basic_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--basic"])
        cat_i = 0
        end = "result"
        each_sub = ["h", 1, None]
        sub = "askreddit"

        assert Export.NameFile()._get_raw_n(args, cat_i, end, each_sub, sub) == \
            "r-askreddit-Hot-1-result"

class TestRFnameWithSubredditArgs():
    """
    Testing r_fname() function on line 57 in Export.py.
    Testing with Subreddit args.
    """

    def test_r_fname_ignores_end_string_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "S"
        each_sub = ["s", "test", "all"]
        sub = "askreddit"

        assert Export.NameFile().r_fname(args, cat_i, each_sub, sub) == \
            "r-askreddit-Search-'test'"

    def test_r_fname_returns_plural_string_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "H"
        each_sub = ["h", 5, None]
        sub = "askreddit"

        assert Export.NameFile().r_fname(args, cat_i, each_sub, sub) == \
            "r-askreddit-Hot-5-results"

    def test_r_fname_returns_non_plural_string_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "H"
        each_sub = ["h", 1, None]
        sub = "askreddit"

        assert Export.NameFile().r_fname(args, cat_i, each_sub, sub) == \
            "r-askreddit-Hot-1-result"
    
class TestRFnameWithBasicArgs():
    """
    Testing r_fname() function on line 57 in Export.py.
    Testing with Basic args.
    """

    def test_r_fname_ignores_end_string_with_basic_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--basic"])
        cat_i = 5
        each_sub = ["s", "test", "all"]
        sub = "askreddit"

        assert Export.NameFile().r_fname(args, cat_i, each_sub, sub) == \
            "r-askreddit-Search-'test'"

    def test_r_fname_returns_plural_string_with_basic_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--basic"])
        cat_i = 0
        each_sub = ["h", 5, None]
        sub = "askreddit"

        assert Export.NameFile().r_fname(args, cat_i, each_sub, sub) == \
            "r-askreddit-Hot-5-results"

    def test_r_fname_returns_non_plural_string_with_basic_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--basic"])
        cat_i = 0
        each_sub = ["h", 1, None]
        sub = "askreddit"

        assert Export.NameFile().r_fname(args, cat_i, each_sub, sub) == \
            "r-askreddit-Hot-1-result"

class TestUFname():
    """
    Testing u_fname() function on line 68 in Export.py.
    """

    def test_u_fname_returns_plural_string(self):
        limit = 2
        string = "test"

        assert Export.NameFile().u_fname(limit, string) == "u-test-2-results"

    def test_u_fname_returns_non_plural_string(self):
        limit = 1
        string = "test"

        assert Export.NameFile().u_fname(limit, string) == "u-test-1-result"

class TestCFname():
    """
    Testing c_fname() function on line 74 in Export.py.
    """

    def test_c_fname_returns_plural_string(self):
        limit = 2
        string = "test"

        assert Export.NameFile().c_fname(limit, string) == "c-test-2-results"

    def test_c_fname_returns_non_plural_string(self):
        limit = 1
        string = "test"

        assert Export.NameFile().c_fname(limit, string) == "c-test-1-result"

    def test_c_fname_returns_raw_string(self):
        limit = 0
        string = "test"

        assert Export.NameFile().c_fname(limit, string) == "c-test-RAW"

class TestWriteCSVAndWriteJSON():
    """
    Testing _write_csv() function on line 90 and _write_json() function on line 
    98 in Export.py.
    """

    def test_write_csv(self):
        filename = os.path.join(sys.path[0], "test_csv_writing.csv")
        overview = {
            "this": [1, 2],
            "is": [3, 4],
            "a": [5, 6],
            "test": [7, 8]}

        Export.Export._write_csv(filename, overview)

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

        Export.Export._write_json(filename, overview)

        with open(filename, "r") as test_json:
            test_dict = json.load(test_json)

        assert test_dict == overview
        os.remove(filename)

class TestGetFilenameExtension():
    """
    Test _get_filename_extension() function on line 104 in Export.py.
    """

    def test_get_filename_extension_returns_csv(self):
        f_name = "test"
        f_type = "csv"

        assert Export.Export._get_filename_extension(f_name, f_type) == \
            "../scrapes/%s/%s.csv" % (Global.date, f_name)

    def test_get_filename_extension_returns_json(self):
        f_name = "test"
        f_type = "json"

        assert Export.Export._get_filename_extension(f_name, f_type) == \
            "../scrapes/%s/%s.json" % (Global.date, f_name)
