"""
Testing `PrepData.py`.
"""


from urs.analytics.utils import PrepData


class TestGetPathGetScrapeTypeMethod:
    """
    Testing GetPath class get_scrape_type() method.
    """

    def test_get_scrape_type_method_valid_filepath(self):
        test_path = "../scrapes/some_date/test/some_other_dir/some_file.json"

        analytics_dir, scrape_dir = PrepData.GetPath.get_scrape_type(
            test_path, "frequencies"
        )

        assert (
            analytics_dir
            == "../scrapes/some_date/analytics/frequencies/test/some_other_dir"
        )
        assert scrape_dir == "test"

    def test_get_scrape_type_method_invalid_directory(self):
        test_path = "../scrapes/some_date/test/some_other_dir/some_file.txt"

        try:
            PrepData.GetPath.get_scrape_type(test_path, "frequencies")
            assert False
        except SystemExit:
            assert True

    def test_get_scrape_type_method_invalid_file_type(self):
        test_path = "../scrapes/some_date/analytics/some_other_dir/some_file.json"

        try:
            PrepData.GetPath.get_scrape_type(test_path, "wordcloud")
            assert False
        except SystemExit:
            assert True


class TestGetPathNameFileMethod:
    """
    Testing GetPath class name_file() method.
    """

    def test_name_file_method(self):
        test_analytics = (
            "../scrapes/some_date/analytics/frequencies/test/some_other_dir"
        )
        test_path = "../something/another_thing/a_third_thing/test.json"

        filename = PrepData.GetPath.name_file(test_analytics, test_path)

        assert (
            filename
            == "..\\scrapes\\some_date\\analytics\\frequencies\\test\\some_other_dir/test.json"
            if "\\" in filename
            else "../scrapes/some_date/analytics/frequencies/test/some_other_dir/test.json"
        )


class TestExtractExtractMethod:
    """
    Testing Extract class extract() method.
    """

    def test_extract_method(self):
        pass


class TestCleanDataRemoveExtrasMethod:
    """
    Testing CleanData class _remove_extras() method.
    """

    def test_remove_extras_method(self):
        test = "[t(e)s,t:i;n.}g{a<s>t`r]ing"

        assert PrepData.CleanData._remove_extras(test) == "t e s t i n  g a s t r ing"


class TestCleanDataCountWordsMethod:
    """
    Testing CleanData class count_words() method.
    """

    def test_count_words_method(self):
        plt_dict = dict()
        obj = {
            "first": "Some text here in the first field [(,",
            "second": "Another line of words here",
        }

        PrepData.CleanData.count_words("second", obj, plt_dict)

        assert plt_dict["Another"] == 1


class TestPrepSubredditPrepSubredditMethod:
    """
    Testing PrepSubreddit class prep_subreddit() method.
    """

    def test_prep_subreddit_method(self):
        data = [
            {"selftext": "This is a test selftext", "title": "This is a test title"},
            {"selftext": "This is a test selftext", "title": "This is a test title"},
        ]

        word_count = PrepData.PrepSubreddit.prep_subreddit(data)

        assert word_count["This"] == 4


class TestPrepRedditorPrepRedditorMethod:
    """
    Testing PrepRedditor class prep_redditor() method.
    """

    def test_prep_redditor_method(self):
        data = {
            "interactions": {
                "comments": [
                    {
                        "type": "comment",
                        "body": "This is a test body",
                    }
                ],
                "submissions": [
                    {
                        "type": "submission",
                        "selftext": "This is a test selftext",
                        "title": "This is a test title",
                    }
                ],
                "hidden": ["FORBIDDEN"],
            }
        }

        word_count = PrepData.PrepRedditor.prep_redditor(data)

        assert word_count["This"] == 3
        assert word_count["selftext"] == 1
        assert word_count["body"] == 1
        assert "FORBIDDEN" not in word_count.keys()


class TestPrepCommentsPrepCommentsMethod:
    """
    Testing PrepComments class prep_comments() method.
    """

    def test_prep_comments_method_prep_raw_comments(self):
        data = {
            "scrape_settings": {"style": "raw"},
            "data": {
                "comments": [
                    {"body": "This is a test body"},
                    {"body": "This is a test body"},
                ]
            },
        }

        word_count = PrepData.PrepComments.prep_comments(data)

        assert word_count["This"] == 2

    def test_prep_comments_method_prep_structured_comments(self):
        data = {
            "scrape_settings": {"style": "structured"},
            "data": {
                "comments": [
                    {
                        "body": "This is a test body",
                        "replies": [{"body": "This is a test body", "replies": []}],
                    }
                ]
            },
        }

        word_count = PrepData.PrepComments.prep_comments(data)

        assert word_count["test"] == 2
