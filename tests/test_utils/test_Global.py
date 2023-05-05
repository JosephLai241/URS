"""
Testing `Global.py`.
"""


import datetime as dt

from urs.utils import Global


class TestGlobalVariables:
    """
    Testing all global variables in Global.py.
    """

    def test_date_variable(self):
        assert Global.date == dt.datetime.now().strftime("%Y-%m-%d")

    def test_subreddit_categories_list(self):
        assert Global.categories == [
            "Hot",
            "New",
            "Controversial",
            "Top",
            "Rising",
            "Search",
        ]

    def test_subreddit_short_cat_list(self):
        categories = ["Hot", "New", "Controversial", "Top", "Rising", "Search"]
        assert Global.short_cat == [cat[0] for cat in categories]


class TestConvertTimeFunction:
    """
    Testing convert_time() function.
    """

    def test_convert_time(self):
        unix_time = 1592291124
        converted_time = "2020-06-16 07:05:24"

        assert Global.convert_time(unix_time) == converted_time


class TestMakeListDictFunction:
    """
    Testing make_list_dict() function.
    """

    def test_make_list_dict(self):
        item = [1, 2, 3, 4]
        correct_list_dict = {1: [], 2: [], 3: [], 4: []}

        assert Global.make_list_dict(item) == correct_list_dict


class TestMakeNoneDictFunction:
    """
    Testing make_none_dict() function.
    """

    def test_make_none_dict(self):
        item = [1, 2, 3, 4]
        correct_none_dict = {1: None, 2: None, 3: None, 4: None}

        assert Global.make_none_dict(item) == correct_none_dict


class TestStatus:
    """
    Testing Status class.
    """

    def test_status_init_method(self):
        test_status = Global.Status(
            "test after message", "test before message", "test color"
        )

        assert test_status._after_message == "test after message"
        assert test_status._before_message == "test before message"
        assert test_status._color == "test color"
