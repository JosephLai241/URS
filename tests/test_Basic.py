import argparse
import sys

from io import StringIO

from urs.utils import Basic, Global

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of  tests.

class MakeArgs():
    """
    Making dummy args to test Basic.py functions.
    """

    @staticmethod
    def parser_for_testing_basic():
        parser = argparse.ArgumentParser()
        parser.add_argument("--basic", action = "store_true")
        return parser

class TestPrintSubsInitMethod():
    """
    Testing PrintSubs class __init__() method found on line 21 in Basic.py.
    """

    def test_print_subs_init_method_s_t_instance_variable(self):
        assert Basic.PrintSubs()._s_t == Global.s_t

class TestPrintSubsFindSubsMethod():
    """
    Testing PrintSubs class _find_subs() method found on line 25 in Basic.py.
    I am not quite sure how I can test this without exposing my personal PRAW 
    credentials, so I am just passing these tests until I find a way around the
    problem.
    """

    def test_find_subs_only_returning_found_subreddits(self):
        pass

    def test_find_subs_only_returning_not_found_subreddits(self):
        pass

    def test_find_subs_returning_both_found_and_not_found_subreddits(self):
        pass

class TestPrintSubsPrintSubredditsMethod():
    """
    Testing PrintSubs class print_subreddits() method found on line 34 in Basic.py.
    I am not quite sure how I can test this without exposing my personal PRAW 
    credentials, so I am just passing these tests until I find a way around the
    problem.
    """

    def test_print_subreddits_only_printing_found_subreddits(self):
        pass

    def test_print_subreddits_only_printing_not_found_subreddits(self):
        pass

    def test_print_subreddits_printing_both_found_and_not_found_subreddits(self):
        pass

class TestGetInputInitMethod():
    """
    Testing GetInput class __init__() method found on line 54 in Basic.py.
    """

    def test_get_input_init_method_categories_instance_variable(self):
        assert Basic.GetInput()._categories == Global.categories

class TestGetInputGetSubredditsMethod():
    """
    Testing GetInput class get_subreddits() method found on line 58 in Basic.py.
    """

    def test_get_input_get_subreddits_no_input_from_user(self):
        pass