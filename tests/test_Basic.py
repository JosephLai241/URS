import argparse
import sys

from io import StringIO

from urs.utils import Basic, Global

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of 30 tests.

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
    I need to find a way to simulate user input for this function. Passing this
    test for now.
    """

    def test_get_input_get_subreddits_no_input_from_user(self):
        pass

    def test_get_input_get_subreddits_valid_input(self):
        pass

class TestGetInputUpdateMasterMethod():
    """
    Testing GetInput class _update_master() method found on line 74 in Basic.py.
    """

    def test_update_master_not_search_category(self):
        cat_i = 0
        test_master = {"test_subreddit": []}
        search_for = 10
        sub = "test_subreddit"

        Basic.GetInput()._update_master(cat_i, test_master, search_for, sub)

        assert test_master == {"test_subreddit": [[0, 10]]}

    def test_update_master_search_category(self):
        cat_i = 5
        test_master = {"test_subreddit": []}
        search_for = "test string"
        sub = "test_subreddit"

        Basic.GetInput()._update_master(cat_i, test_master, search_for, sub)

        assert test_master == {"test_subreddit": [[5, "test string"]]}

class TestGetInputGetSearchMethod():
    """
    Testing GetInput class _get_search() method found on line 82 in Basic.py.
    I need to find a way to simulate user input for this function. Passing this
    test for now. 
    """

    def test_get_input_search_for_is_a_number(self):
        pass

    def test_get_input_search_for_is_a_string(self):
        pass

    def test_get_input_search_for_no_input(self):
        pass

class TestGetInputGetNResultsMethod():
    """
    Testing GetInput class _get_n_results() method found on line 82 in Basic.py.
    I need to find a way to simulate user input for this function. Passing this
    test for now. 
    """

    def test_get_n_results_normal_input(self):
        pass

    def test_get_n_results_invalid_input(self):
        pass

    def test_get_n_results_no_input(self):
        pass

class TestGetInputGetSettingsMethod():
    """
    Testing GetInput class get_settings() method found on line 112 in Basic.py.
    I need to find a way to simulate user input for this function. Passing this
    test for now.
    """

    def test_get_settings_selected_search_option(self):
        pass

    def test_get_settings_selected_other_category_option(self):
        pass

    def test_get_settings_invalid_option_out_of_range(self):
        pass

    def test_get_settings_invalid_option_is_not_a_number(self):
        pass

class TestConfirmInputConfirmSubredditsMethod():
    """
    Testing GetInput class confirm_subreddits() method found on line 145 in Basic.py.
    I need to find a way to simulate user input for this function. Passing this
    test for now.
    """

    def test_confirm_subreddits_selected_yes(self):
        pass

    def test_confirm_subreddits_selected_no(self):
        pass

    def test_confirm_subreddits_invalid_option(self):
        pass

class TestConfirmInputAnotherMethod():
    """
    Testing GetInput class another() method found on line 162 in Basic.py.
    I need to find a way to simulate user input for this function. Passing this
    test for now.
    """

    def test_another_selected_yes(self):
        pass

    def test_another_selected_no(self):
        pass

    def test_another_invalid_option(self):
        pass

class TestRunBasicCreateSettingsMethod():
    """
    Testing RunBasic class _create_settings() method found on line 180 in Basic.py.
    Waiting to figure out how to test user input before testing this function.
    Passing for now.
    """

    def test_create_settings(self):
        pass

class TestRunBasicPrintConfirmMethod():
    """
    Testing RunBasic class _print_confirm() method found on line 190 in Basic.py.
    Waiting to figure out how to test user input before testing this function.
    Passing for now.
    """

    def test_print_confirm(self):
        pass
