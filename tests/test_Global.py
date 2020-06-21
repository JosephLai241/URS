import datetime as dt

from urs.utils import Global

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

### Includes a total of 9 tests.

class TestGlobalVariables():
    """
    Testing all global variables found on lines 7-23 in Global.py.
    """

    def test_date_variable(self):
        assert Global.date == dt.datetime.now().strftime("%m-%d-%Y")

    def test_export_options_list(self):
        assert Global.eo == ["csv", "json"]

    def test_options_list(self):
        assert Global.options == ["y", "n"]

    def test_scrape_types_list(self):
        assert Global.s_t == ["subreddit", "redditor", "comments"]

    def test_subreddit_categories_list(self):
        assert Global.categories == ["Hot", "New", "Controversial", "Top", \
            "Rising", "Search"]

    def test_subreddit_short_cat_list(self):
        categories = ["Hot", "New", "Controversial", "Top", "Rising", "Search"]
        assert Global.short_cat == [cat[0] for cat in categories]

class TestConvertTime():
    """
    Test convert_time() function on line 26 in Global.py.
    """

    def test_convert_time(self):
        unix_time = 1592291124
        converted_time = "06-16-2020 07:05:24"

        assert Global.convert_time(unix_time) == converted_time

class TestMakeDictionary():
    """
    Test make_list_dict() function on line 30 and make_none_dict() function on
    line 34 in Global.py.
    """

    def test_make_list_dict(self):
        item = [1, 2, 3, 4]
        correct_list_dict = {
            1: [],
            2: [],
            3: [],
            4: []
        }

        assert Global.make_list_dict(item) == correct_list_dict

    def test_make_none_dict(self):
        item = [1, 2, 3, 4]
        correct_none_dict = {
            1: None,
            2: None,
            3: None,
            4: None
        }

        assert Global.make_none_dict(item) == correct_none_dict