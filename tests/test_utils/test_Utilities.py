"""
Testing `Utilities.py`.
"""


import os

from rich.tree import Tree

from urs.utils.Utilities import DateTree


class TestDateTreeCheckDateFormatMethod:
    """
    Testing DateTree class _check_date_format() method.
    """

    def test_check_date_format_dash_format(self):
        test_date = "06-28-2021"
        test_search_date = DateTree._check_date_format(test_date)

        assert test_search_date == test_date

    def test_check_date_format_slash_format(self):
        test_date = "06/28/2021"
        test_search_date = DateTree._check_date_format(test_date)

        assert test_search_date == "06-28-2021"

    def test_check_date_wrong_format(self):
        test_date = "06.28.2021"

        try:
            _ = DateTree._check_date_format(test_date)
            assert False
        except TypeError:
            assert True

    def test_check_date_short_date_wrong_format(self):
        test_date = "06-28-21"

        try:
            _ = DateTree._check_date_format(test_date)
            assert False
        except TypeError:
            assert True


class TestDateTreeFindDateDirectoryMethod:
    """
    Testing DateTree class _find_date_directory() method.
    """

    def test_find_date_directory_directory_exists(self):
        os.mkdir("../scrapes/06-28-2021")
        dir_exists = DateTree._find_date_directory("06-28-2021")

        assert dir_exists == True

    def test_find_date_directory_directory_does_not_exist(self):
        os.rmdir("../scrapes/06-28-2021")
        dir_exists = DateTree._find_date_directory("06-28-2021")

        assert dir_exists == False


class TestDateTreeCreateDirectoryTreeMethod:
    """
    Testing DateTree class _create_directory_tree() method.
    """

    def test_create_directory_tree(self):
        os.makedirs("../scrapes/06-28-2021/testing/nested/directories/tree")

        test_tree = Tree("test")

        try:
            DateTree._create_directory_tree("../scrapes/06-28-2021", test_tree)
            assert True
        except Exception as e:
            print(
                f"An exception was thrown when testing DateTree._create_directory_tree(): {e}"
            )
            assert False


class TestDateTreeDisplayTreeMethod:
    """
    Testing DateTree class display_tree() method.
    """

    def test_display_tree_method_valid_search_date(self):
        try:
            DateTree.display_tree("06-28-2021")
            assert True
        except Exception as e:
            print(f"An exception was thrown when testing DateTree.display_tree(): {e}")
            assert False

    def test_display_tree_method_search_date_not_found(self):
        try:
            DateTree.display_tree("00-00-0000")
            assert False
        except SystemExit:
            assert True

    def test_display_tree_method_invalid_search_date(self):
        try:
            DateTree.display_tree("00.00.0000")
            assert False
        except SystemExit:
            assert True
