"""
Testing `Export.py`.
"""


import argparse
import csv
import json
import os
import sys

from urs.utils.Export import EncodeNode, Export, NameFile
from urs.utils.Global import categories, date, short_cat


class MakeArgs:
    """
    Making dummy args to test Export.py functions.
    """

    @staticmethod
    def parser_for_testing_export():
        parser = argparse.ArgumentParser()
        parser.add_argument("--subreddit", action="store_true")
        parser.add_argument("--basic", action="store_true")
        parser.add_argument("--rules", action="store_true")

        parser.add_argument("--raw", action="store_true")

        return parser


class TestNameFileCheckLenMethod:
    """
    Testing NameFile class _check_len() method.
    """

    def test_check_len_string_is_shorter_than_50_char(self):
        test_string = "poebtcjocweeooijhyltchjarvu"

        cut_string = NameFile()._check_len(test_string)

        assert test_string == cut_string

    def test_check_len_string_is_longer_than_50_char(self):
        test_string = "fegskkxjsacxpusflfccqynqchbqdywvvjsmqmhaxyvhtipropqkzqstsxcx"

        cut_string = NameFile()._check_len(test_string)

        assert cut_string == "fegskkxjsacxpusflfccqynqchbqdywvvjsmqmhaxyvhtipr--"


class TestNameFileFixMethod:
    """
    Testing NameFile class _fix() method.
    """

    def test_fix(self):
        name = "/t\\e?s%t*i:n|g<c@h!a#r$ac^t&e*(r)s>}{~+`="
        fixed = "_t_e_s_t_i_n_g_c_h_a_r_ac_t_e__r_s_______"

        assert fixed == NameFile()._fix(name)


class TestNameFileRCategory:
    """
    Testing NameFile class _r_category() method.
    """

    def test_r_category_first_switch(self):
        assert NameFile()._r_category("H", 0) == categories[5]

    def test_r_category_second_switch(self):
        for index, category in enumerate(short_cat[:5]):
            assert NameFile()._r_category(category, 1) == categories[index]


class TestNameFileRGetCategory:
    """
    Testing NameFile class _r_get_category() method.
    """

    def test_r_get_category_subreddit_arg_returns_zero(self):
        assert NameFile()._r_get_category("S") == 0

    def test_r_get_category_subreddit_arg_returns_one(self):
        assert NameFile()._r_get_category("C") == 1


class TestNameFileGetRawN:
    """
    Testing NameFile class _get_raw_n() method.
    """

    def test_get_raw_n_returns_search_filename_format_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "S"
        end = "result"
        each_sub = ["s", "test", "all"]
        sub = "askreddit"

        assert (
            NameFile()._get_raw_n(args, cat_i, end, each_sub, sub)
            == "askreddit-search-'test'"
        )

    def test_get_raw_n_returns_category_filename_format_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "H"
        end = "result"
        each_sub = ["h", "1", None]
        sub = "askreddit"

        assert (
            NameFile()._get_raw_n(args, cat_i, end, each_sub, sub)
            == "askreddit-hot-1-result"
        )

    def test_get_raw_n_returns_returns_filter_string_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "H"
        end = "result"
        each_sub = ["h", "1", "year"]
        sub = "askreddit"

        assert (
            NameFile()._get_raw_n(args, cat_i, end, each_sub, sub)
            == "askreddit-hot-1-result-past-year"
        )

    def test_get_raw_n_returns_returns_filter_string_with_rules_included(self):
        args = MakeArgs.parser_for_testing_export().parse_args(
            ["--subreddit", "--rules"]
        )
        cat_i = "H"
        end = "result"
        each_sub = ["h", "1", "year"]
        sub = "askreddit"

        assert (
            NameFile()._get_raw_n(args, cat_i, end, each_sub, sub)
            == "askreddit-hot-1-result-past-year-rules"
        )


class TestNameFileRFname:
    """
    Testing NameFile class r_fname() method.
    """

    def test_r_fname_ignores_end_string_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "S"
        each_sub = ["s", "test", "all"]
        sub = "askreddit"

        assert (
            NameFile().r_fname(args, cat_i, each_sub, sub) == "askreddit-search-'test'"
        )

    def test_r_fname_returns_plural_string_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "H"
        each_sub = ["h", 5, None]
        sub = "askreddit"

        assert (
            NameFile().r_fname(args, cat_i, each_sub, sub) == "askreddit-hot-5-results"
        )

    def test_r_fname_returns_non_plural_string_with_subreddit_args(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--subreddit"])
        cat_i = "H"
        each_sub = ["h", 1, None]
        sub = "askreddit"

        assert (
            NameFile().r_fname(args, cat_i, each_sub, sub) == "askreddit-hot-1-result"
        )


class TestNameFileUFname:
    """
    Testing NameFile class u_fname() method.
    """

    def test_u_fname_returns_plural_string(self):
        limit = 2
        string = "test"

        assert NameFile().u_fname(limit, string) == "test-2-results"

    def test_u_fname_returns_non_plural_string(self):
        limit = 1
        string = "test"

        assert NameFile().u_fname(limit, string) == "test-1-result"


class TestNameFileCFname:
    """
    Testing NameFile class c_fname() method.
    """

    def test_c_fname_returns_plural_string_with_raw_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--raw"])
        limit = 2
        string = "test"

        assert NameFile().c_fname(args, limit, string) == "test-2-results-raw"

    def test_c_fname_returns_plural_string_with_structured_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args()
        limit = 2
        string = "test"

        assert NameFile().c_fname(args, limit, string) == "test-2-results"

    def test_c_fname_returns_non_plural_string_with_raw_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--raw"])
        limit = 1
        string = "test"

        assert NameFile().c_fname(args, limit, string) == "test-1-result-raw"

    def test_c_fname_returns_non_plural_string_with_structured_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args()
        limit = 1
        string = "test"

        assert NameFile().c_fname(args, limit, string) == "test-1-result"

    def test_c_fname_returns_all_comments_with_raw_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args(["--raw"])
        limit = 0
        string = "test"

        assert NameFile().c_fname(args, limit, string) == "test-all-raw"

    def test_c_fname_returns_all_comments_with_structured_format(self):
        args = MakeArgs.parser_for_testing_export().parse_args()
        limit = 0
        string = "test"

        assert NameFile().c_fname(args, limit, string) == "test-all"


class TestExportGetFilenameExtension:
    """
    Testing Export class _get_filename_extension() method.
    """

    def test_get_filename_extension_returns_subreddits_csv(self):
        f_name = "test"
        f_type = "csv"

        assert (
            Export._get_filename_extension(f_name, f_type, "subreddits")
            == f"../scrapes/{date}/subreddits/{f_name}.csv"
        )

    def test_get_filename_extension_returns_redditors_csv(self):
        f_name = "test"
        f_type = "csv"

        assert (
            Export._get_filename_extension(f_name, f_type, "redditors")
            == f"../scrapes/{date}/redditors/{f_name}.csv"
        )

    def test_get_filename_extension_returns_comments_csv(self):
        f_name = "test"
        f_type = "csv"

        assert (
            Export._get_filename_extension(f_name, f_type, "comments")
            == f"../scrapes/{date}/comments/{f_name}.csv"
        )

    def test_get_filename_extension_returns_subreddits_json(self):
        f_name = "test"
        f_type = "json"

        assert (
            Export._get_filename_extension(f_name, f_type, "subreddits")
            == f"../scrapes/{date}/subreddits/{f_name}.json"
        )

    def test_get_filename_extension_returns_redditors_json(self):
        f_name = "test"
        f_type = "json"

        assert (
            Export._get_filename_extension(f_name, f_type, "redditors")
            == f"../scrapes/{date}/redditors/{f_name}.json"
        )

    def test_get_filename_extension_returns_comments_json(self):
        f_name = "test"
        f_type = "json"

        assert (
            Export._get_filename_extension(f_name, f_type, "comments")
            == f"../scrapes/{date}/comments/{f_name}.json"
        )


class TestExportWriteCSVAndWriteJSON:
    """
    Testing Export class write_csv() method.
    """

    def test_write_csv(self):
        filename = os.path.join(sys.path[0], "test_csv_writing.csv")
        overview = {"this": [1, 2], "is": [3, 4], "a": [5, 6], "test": [7, 8]}

        Export.write_csv(overview, filename)

        with open(filename, "r", newline="", encoding="utf-8") as test_csv:
            reader = csv.reader(test_csv)
            test_dict = dict((header, []) for header in next(reader))
            for row in reader:
                try:
                    for row_index, key in enumerate(test_dict.keys()):
                        test_dict[key].append(int(row[row_index]))
                except IndexError:
                    continue

        assert test_dict == overview
        os.remove(filename)


class TestExportWriteJSONMethod:
    """
    Testing Export class write_json() method.
    """

    def test_write_json(self):
        filename = os.path.join(sys.path[0], "test_json_writing.json")
        overview = {
            "test_1": {"this": 1, "is": 1, "a": 1, "test": 1},
            "test_2": {"this": 2, "is": 2, "a": 2, "test": 2},
        }

        Export.write_json(overview, filename)

        with open(filename, "r", encoding="utf-8") as test_json:
            test_dict = json.load(test_json)
            assert test_dict == overview

        os.remove(filename)


class MockNode:
    """
    Creating a test node to test write_structured_comments() method.
    """

    def __init__(self, string):
        self.string = string
        self.replies = []


class TestExportWriteStructuredCommentsMethod:
    """
    Testing Export class write_structured_comments() method.
    """

    def test_write_structured_comments(self):
        test_nodes = []

        first_node = MockNode("test one")
        EncodeNode().encode(first_node)
        second_node = MockNode("test two")
        EncodeNode().encode(second_node)
        third_node = MockNode("test three")
        EncodeNode().encode(third_node)

        first_node.replies.append(second_node)
        first_node.replies[0].replies.append(third_node)

        test_nodes.append(first_node)

        Export.write_structured_comments(test_nodes, "structured_comments_test")

        with open(
            f"../scrapes/{date}/comments/structured_comments_test.json",
            "r",
            encoding="utf-8",
        ) as test_json:
            test_dict = json.load(test_json)
            assert test_dict == [
                {
                    "string": "test one",
                    "replies": [
                        {
                            "string": "test two",
                            "replies": [{"string": "test three", "replies": []}],
                        }
                    ],
                }
            ]


class TestExportExportMethod:
    """
    Testing Export class export() method.
    """

    def test_export_write_json(self):
        data = {
            "test_1": {"this": 1, "is": 1, "a": 1, "test": 1},
            "test_2": {"this": 2, "is": 2, "a": 2, "test": 2},
        }

        f_name = "export_write_json_test"
        f_type = "json"
        scrape = "subreddits"

        Export.export(data, f_name, f_type, scrape)

        with open(
            f"../scrapes/{date}/subreddits/export_write_json_test.json",
            "r",
            encoding="utf-8",
        ) as test_json:
            test_dict = json.load(test_json)
            assert test_dict == data

    def test_export_write_csv(self):
        data = {"this": [1, 2], "is": [3, 4], "a": [5, 6], "test": [7, 8]}

        f_name = "export_write_csv_test"
        f_type = "csv"
        scrape = "subreddits"

        Export.export(data, f_name, f_type, scrape)

        with open(
            f"../scrapes/{date}/subreddits/export_write_csv_test.csv",
            "r",
            newline="",
            encoding="utf-8",
        ) as test_csv:
            reader = csv.reader(test_csv)
            test_dict = dict((header, []) for header in next(reader))
            for row in reader:
                try:
                    for row_index, key in enumerate(test_dict.keys()):
                        test_dict[key].append(int(row[row_index]))
                except IndexError:
                    continue

            assert test_dict == data
