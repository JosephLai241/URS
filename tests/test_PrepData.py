from urs.analytics.utils import PrepData

### Function names are pretty self-explanatory, so I will not be adding comments 
### above the functions.

class TestGetPathGetScrapeTypeMethod():
    """
    Testing GetPath class get_scrape_type() method found on line 17 in PrepData.py.
    """

    def test_get_scrape_type_method(self):
        test_path = "../scrape/some_date/test/some_other_dir/some_file"

        assert PrepData.GetPath.get_scrape_type(test_path) == "test"

class TestGetPathNameFileMethod():
    """
    Testing GetPath class name_file() method found on line 22 in PrepData.py.
    """

    def test_name_file_method(self):
        test_export_option = "png"
        test_path = "../scrapes/some_date/subreddits/some_file.json"
        test_tool_type = "test_tool"

        date_dir, filename = PrepData.GetPath.name_file(test_export_option, test_path, test_tool_type)

        assert date_dir == "some_date"
        assert filename == "../scrapes/some_date/analytics/test_tool/some_file.png"

class TestExtractExtractMethod():
    """
    Testing Extract class extract() method found on line 41 in PrepData.py.
    """

    def test_extract_method(self):
        pass

class TestCleanDataRemoveExtrasMethod():
    """
    Testing CleanData class _remove_extras() method found on line 52 in PrepData.py.
    """

    def test_remove_extras_method(self):
        test = "[t(e)s,t:i;n.}g{a<s>t`r]ing"

        assert PrepData.CleanData._remove_extras(test) == "t e s t i n  g a s t r ing"

class TestCleanDataCountWordsMethod():
    """
    Testing CleanData class count_words() method found on line 64 in PrepData.py.
    """

    def test_count_words_method(self):
        plt_dict = dict()
        obj = {
            "first": "Some text here in the first field",
            "second": "Another line of words here"
        }

        PrepData.CleanData.count_words("second", obj, plt_dict)

        assert plt_dict["Another"] == 1

class TestPrepSubredditPrepSubredditMethod():
    """
    Testing PrepSubreddit class prep_subreddit() method found on line 83 in PrepData.py.
    """

    def test_prep_subreddit_method(self):
        pass

class TestPrepRedditorPrepRedditorMethod():
    """
    Testing PrepRedditor class prep_redditor() method found on line 99 in PrepData.py.
    """

    def test_prep_redditor_method(self):
        pass

class TestPrepCommentsPrepRawMethod():
    """
    Testing PrepComments class _prep_raw() method found on line 124 in PrepData.py.
    """

    def test_prep_raw_method(self):
        pass

class TestPrepCommentsPrepStructuredMethod():
    """
    Testing PrepComments class _prep_structured() method found on line 129 in PrepData.py.
    """

    def test_prep_structured_method(self):
        pass

class TestPrepCommentsPrepCommentsMethod():
    """
    Testing PrepComments class prep_comments() method found on line 142 in PrepData.py.
    """

    def test_prep_comments_method(self):
        pass
