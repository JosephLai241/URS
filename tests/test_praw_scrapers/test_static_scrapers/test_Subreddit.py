"""
Testing `Subreddit.py`.
"""


import argparse
import os

import praw
from dotenv import load_dotenv
from prettytable import PrettyTable

from urs.praw_scrapers.static_scrapers import Subreddit
from urs.utils import Global


class MakeArgs:
    """
    Making dummy args to test Comments.py methods.
    """

    @staticmethod
    def parser_for_testing():
        parser = argparse.ArgumentParser()
        return parser

    @staticmethod
    def make_scraper_args():
        parser = MakeArgs.parser_for_testing()
        parser.add_argument("--subreddit", action="append", nargs="+")
        parser.add_argument("--redditor", action="append", nargs=2)
        parser.add_argument("--comments", action="append", nargs=2)
        parser.add_argument("--csv", action="store_true")
        parser.add_argument("--rules", action="store_true")

        return parser


class Login:
    """
    Create a Reddit object with PRAW API credentials.
    """

    @staticmethod
    def create_reddit_object():
        load_dotenv()

        return praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
        )


class CreateObject:
    """
    Creating a fake Reddit object for testing.
    """

    def __init__(self, metadata):
        for key, value in metadata.items():
            self.__setattr__(key, value)


class TestPrintConfirmAddEachSettingMethod:
    """
    Testing PrintConfirm class _add_each_setting() method.
    """

    def test_add_each_setting(self):
        pretty_subs = PrettyTable()
        pretty_subs.field_names = [
            "Subreddit",
            "Category",
            "Time Filter",
            "Number of results / Keywords",
        ]

        s_master = {"askreddit": [["h", 100, None]]}

        try:
            Subreddit.PrintConfirm._add_each_setting(pretty_subs, s_master)
            assert True
        except:
            assert False


class TestPrintConfirmPrintSettingsMethod:
    """
    Testing PrintConfirm class print_settings() method.
    """

    def test_print_settings(self):
        s_master = {"askreddit": [["h", 100, None]]}

        try:
            Subreddit.PrintConfirm.print_settings(s_master)
            assert True
        except:
            assert False


class TestGetExtrasGetRulesMethod:
    """
    Testing GetExtras class get_rules() method.
    """

    def test_get_rules(self):
        reddit = Login.create_reddit_object()
        askreddit = reddit.subreddit("askreddit")

        post_requirements, rules = Subreddit.GetExtras.get_rules(askreddit)

        assert isinstance(post_requirements, dict)
        assert isinstance(rules, list)


class TestGetSubmissionsSwitchInitMethod:
    """
    Testing GetSubmissionsSwitch class __init__() method.
    """

    def test_init_method_with_no_time_filter(self):
        search_for = 1

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = None

        switch = Subreddit.GetSubmissionsSwitch(search_for, subreddit, time_filter)

        assert isinstance(
            switch._controversial, praw.models.listing.generator.ListingGenerator
        )
        assert isinstance(switch._hot, praw.models.listing.generator.ListingGenerator)
        assert isinstance(switch._new, praw.models.listing.generator.ListingGenerator)
        assert isinstance(
            switch._rising, praw.models.listing.generator.ListingGenerator
        )
        assert isinstance(switch._top, praw.models.listing.generator.ListingGenerator)

        assert switch._switch.get(0) == switch._hot
        assert switch._switch.get(1) == switch._new
        assert switch._switch.get(2) == switch._controversial
        assert switch._switch.get(3) == switch._top
        assert switch._switch.get(4) == switch._rising


class TestGetSubmissionsScrapeSubMethod:
    """
    Testing GetSubmissionsSwitch class scrape_sub() method.
    """

    def test_scrape_sub(self):
        search_for = 1

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = None

        switch = Subreddit.GetSubmissionsSwitch(search_for, subreddit, time_filter)

        assert isinstance(
            switch.scrape_sub(0), praw.models.listing.generator.ListingGenerator
        )
        assert isinstance(
            switch.scrape_sub(1), praw.models.listing.generator.ListingGenerator
        )
        assert isinstance(
            switch.scrape_sub(2), praw.models.listing.generator.ListingGenerator
        )
        assert isinstance(
            switch.scrape_sub(3), praw.models.listing.generator.ListingGenerator
        )
        assert isinstance(
            switch.scrape_sub(4), praw.models.listing.generator.ListingGenerator
        )


class TestGetSubmissionsCollectSearchMethod:
    """
    Testing GetSubmissions class _collect_search() method.
    """

    def test_collect_search_no_time_filter(self):
        search_for = "test"
        sub = "askreddit"

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = None

        search = Subreddit.GetSubmissions._collect_search(
            search_for, sub, subreddit, time_filter
        )

        assert isinstance(search, praw.models.listing.generator.ListingGenerator)

    def test_collect_search_has_time_filter(self):
        search_for = "test"
        sub = "askreddit"

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = "year"

        search = Subreddit.GetSubmissions._collect_search(
            search_for, sub, subreddit, time_filter
        )

        assert isinstance(search, praw.models.listing.generator.ListingGenerator)


class TestGetSubmissionsCollectOthersMethod:
    """
    Testing GetSubmissions class _collect_others() method.
    """

    def test_collect_others_no_time_filter(self):
        cat_i = "H"
        search_for = 1
        sub = "askreddit"

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = None

        others = Subreddit.GetSubmissions._collect_others(
            cat_i, search_for, sub, subreddit, time_filter
        )

        assert isinstance(others, praw.models.listing.generator.ListingGenerator)

    def test_collect_others_has_time_filter(self):
        cat_i = "C"
        search_for = 1
        sub = "askreddit"

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = "year"

        others = Subreddit.GetSubmissions._collect_others(
            cat_i, search_for, sub, subreddit, time_filter
        )

        assert isinstance(others, praw.models.listing.generator.ListingGenerator)


class TestGetSubmissionsGetMethod:
    """
    Testing GetSubmissions class get() method.
    """

    def test_get_method_trigger_collect_search_no_time_filter(self):
        cat_i = "S"
        search_for = "test"
        sub = "askreddit"

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = None

        results = Subreddit.GetSubmissions.get(
            cat_i, search_for, sub, subreddit, time_filter
        )

        assert isinstance(results, praw.models.listing.generator.ListingGenerator)

    def test_get_method_trigger_collect_search_has_time_filter(self):
        cat_i = "S"
        search_for = "test"
        sub = "askreddit"

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = "year"

        results = Subreddit.GetSubmissions.get(
            cat_i, search_for, sub, subreddit, time_filter
        )

        assert isinstance(results, praw.models.listing.generator.ListingGenerator)

    def test_get_method_trigger_collect_others_no_time_filter(self):
        cat_i = "H"
        search_for = 1
        sub = "askreddit"

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = None

        results = Subreddit.GetSubmissions.get(
            cat_i, search_for, sub, subreddit, time_filter
        )

        assert isinstance(results, praw.models.listing.generator.ListingGenerator)

    def test_get_method_trigger_collect_others_has_time_filter(self):
        cat_i = "C"
        search_for = 1
        sub = "askreddit"

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = "year"

        results = Subreddit.GetSubmissions.get(
            cat_i, search_for, sub, subreddit, time_filter
        )

        assert isinstance(results, praw.models.listing.generator.ListingGenerator)


class TestFormatSubmissionsFormatSubmissionsMethod:
    """
    Testing FormatSubmissions class format_submissions() method.
    """

    def test_format_submissions(self):
        submissions = [
            CreateObject(
                {
                    "author": None,
                    "created_utc": 1617324719,
                    "distinguished": None,
                    "edited": False,
                    "id": "test_submission_id",
                    "is_original_content": True,
                    "is_self": True,
                    "link_flair_text": None,
                    "locked": False,
                    "name": "t3_test",
                    "over_18": False,
                    "num_comments": 6,
                    "permalink": "r/test_sub",
                    "score": 6,
                    "selftext": "Some text here",
                    "spoiler": False,
                    "stickied": False,
                    "title": "A title here",
                    "upvote_ratio": 0.5,
                    "url": "https://www.reddit.com/something",
                }
            ),
            CreateObject(
                {
                    "author": None,
                    "created_utc": 1617324719,
                    "distinguished": None,
                    "edited": False,
                    "id": "test_submission_id",
                    "is_original_content": True,
                    "is_self": True,
                    "link_flair_text": None,
                    "locked": False,
                    "name": "t3_test",
                    "over_18": False,
                    "num_comments": 6,
                    "permalink": "r/test_sub",
                    "score": 6,
                    "selftext": "Some text here",
                    "spoiler": False,
                    "stickied": False,
                    "title": "A title here",
                    "upvote_ratio": 0.5,
                    "url": "https://www.reddit.com/something",
                }
            ),
        ]

        submissions_list = Subreddit.FormatSubmissions.format_submissions(submissions)

        for submission in submissions_list:
            assert submission["author"] == "[deleted]"
            assert submission["created_utc"] == "2021-04-02 00:51:59"
            assert submission["distinguished"] == None
            assert submission["edited"] == False
            assert submission["id"] == "test_submission_id"
            assert submission["is_original_content"] == True
            assert submission["is_self"] == True
            assert submission["link_flair_text"] == None
            assert submission["locked"] == False
            assert submission["name"] == "t3_test"
            assert submission["nsfw"] == False
            assert submission["num_comments"] == 6
            assert submission["permalink"] == "r/test_sub"
            assert submission["score"] == 6
            assert submission["selftext"] == "Some text here"
            assert submission["spoiler"] == False
            assert submission["stickied"] == False
            assert submission["title"] == "A title here"
            assert submission["upvote_ratio"] == 0.5
            assert submission["url"] == "https://www.reddit.com/something"


class TestFormatCSVFormatCsvMethod:
    """
    Testing FormatCSV class format_csv() method.
    """

    def test_format_csv(self):
        submissions = [
            CreateObject(
                {
                    "author": None,
                    "created_utc": 1617324719,
                    "distinguished": None,
                    "edited": False,
                    "id": "test_submission_id",
                    "is_original_content": True,
                    "is_self": True,
                    "link_flair_text": None,
                    "locked": False,
                    "name": "t3_test",
                    "over_18": False,
                    "num_comments": 6,
                    "permalink": "r/test_sub",
                    "score": 6,
                    "selftext": "Some text here",
                    "spoiler": False,
                    "stickied": False,
                    "title": "A title here",
                    "upvote_ratio": 0.5,
                    "url": "https://www.reddit.com/something",
                }
            ),
            CreateObject(
                {
                    "author": None,
                    "created_utc": 1617324719,
                    "distinguished": None,
                    "edited": False,
                    "id": "test_submission_id",
                    "is_original_content": True,
                    "is_self": True,
                    "link_flair_text": None,
                    "locked": False,
                    "name": "t3_test",
                    "over_18": False,
                    "num_comments": 6,
                    "permalink": "r/test_sub",
                    "score": 6,
                    "selftext": "Some text here",
                    "spoiler": False,
                    "stickied": False,
                    "title": "A title here",
                    "upvote_ratio": 0.5,
                    "url": "https://www.reddit.com/something",
                }
            ),
        ]

        submissions_list = Subreddit.FormatSubmissions.format_submissions(submissions)

        overview = Subreddit.FormatCSV.format_csv(submissions_list)

        for key, values in overview.items():
            for value in values:
                if key == "author":
                    assert value == "[deleted]"
                elif key == "created_utc":
                    assert value == "2021-04-02 00:51:59"
                elif key == "distinguished":
                    assert value == None
                elif key == "edited":
                    assert value == False
                elif key == "id":
                    assert value == "test_submission_id"
                elif key == "is_original_content":
                    assert value == True
                elif key == "is_self":
                    assert value == True
                elif key == "link_flair_text":
                    assert value == None
                elif key == "locked":
                    assert value == False
                elif key == "name":
                    assert value == "t3_test"
                elif key == "nsfw":
                    assert value == False
                elif key == "num_comments":
                    assert value == 6
                elif key == "permalink":
                    assert value == "r/test_sub"
                elif key == "score":
                    assert value == 6
                elif key == "selftext":
                    assert value == "Some text here"
                elif key == "spoiler":
                    assert value == False
                elif key == "stickied":
                    assert value == False
                elif key == "title":
                    assert value == "A title here"
                elif key == "upvote_ratio":
                    assert value == 0.5
                elif key == "url":
                    assert value == "https://www.reddit.com/something"


class TestFormatJSONAddSubredditRulesMethod:
    """
    Testing FormatJSON class _add_subreddit_rules() method.
    """

    def test_add_subreddit_rules(self):
        skeleton = {
            "scrape_settings": {
                "subreddit": "askreddit",
                "category": "hot",
                "n_results_or_keywords": 100,
                "time_filter": None,
            },
            "data": None,
        }

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        Subreddit.FormatJSON._add_subreddit_rules(skeleton, subreddit)

        assert skeleton["subreddit_rules"]
        assert skeleton["subreddit_rules"]["rules"]
        assert skeleton["subreddit_rules"]["post_requirements"]


class TestFormatJSONMakeJsonSkeletonMethod:
    """
    Testing FormatJSON class make_json_skeleton() method.
    """

    def test_make_json_skeleton(self):
        cat_i = "H"
        search_for = 10
        sub = "askreddit"
        time_filter = None

        skeleton = Subreddit.FormatJSON.make_json_skeleton(
            cat_i, search_for, sub, time_filter
        )

        assert skeleton["scrape_settings"]["subreddit"] == "askreddit"
        assert skeleton["scrape_settings"]["category"] == "hot"
        assert skeleton["scrape_settings"]["n_results_or_keywords"] == 10
        assert skeleton["scrape_settings"]["time_filter"] == None

        assert skeleton["data"] == None


class TestFormatJSONFormatJsonMethod:
    """
    Testing FormatJSON class format_json() method.
    """

    def test_format_json_no_rules(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args([])

        skeleton = {
            "scrape_settings": {
                "subreddit": "askreddit",
                "category": "hot",
                "n_results_or_keywords": 100,
                "time_filter": None,
            },
            "data": None,
        }

        submissions = [
            CreateObject(
                {
                    "author": None,
                    "created_utc": 1617324719,
                    "distinguished": None,
                    "edited": False,
                    "id": "test_submission_id",
                    "is_original_content": True,
                    "is_self": True,
                    "link_flair_text": None,
                    "locked": False,
                    "name": "t3_test",
                    "over_18": False,
                    "num_comments": 6,
                    "permalink": "r/test_sub",
                    "score": 6,
                    "selftext": "Some text here",
                    "spoiler": False,
                    "stickied": False,
                    "title": "A title here",
                    "upvote_ratio": 0.5,
                    "url": "https://www.reddit.com/something",
                }
            ),
            CreateObject(
                {
                    "author": None,
                    "created_utc": 1617324719,
                    "distinguished": None,
                    "edited": False,
                    "id": "test_submission_id",
                    "is_original_content": True,
                    "is_self": True,
                    "link_flair_text": None,
                    "locked": False,
                    "name": "t3_test",
                    "over_18": False,
                    "num_comments": 6,
                    "permalink": "r/test_sub",
                    "score": 6,
                    "selftext": "Some text here",
                    "spoiler": False,
                    "stickied": False,
                    "title": "A title here",
                    "upvote_ratio": 0.5,
                    "url": "https://www.reddit.com/something",
                }
            ),
        ]

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        Subreddit.FormatJSON.format_json(args, skeleton, submissions, subreddit)

        assert skeleton["data"]

    def test_format_json_including_rules(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--rules"])

        skeleton = {
            "scrape_settings": {
                "subreddit": "askreddit",
                "category": "hot",
                "n_results_or_keywords": 100,
                "time_filter": None,
            },
            "data": None,
        }

        submissions = [
            CreateObject(
                {
                    "author": None,
                    "created_utc": 1617324719,
                    "distinguished": None,
                    "edited": False,
                    "id": "test_submission_id",
                    "is_original_content": True,
                    "is_self": True,
                    "link_flair_text": None,
                    "locked": False,
                    "name": "t3_test",
                    "over_18": False,
                    "num_comments": 6,
                    "permalink": "r/test_sub",
                    "score": 6,
                    "selftext": "Some text here",
                    "spoiler": False,
                    "stickied": False,
                    "title": "A title here",
                    "upvote_ratio": 0.5,
                    "url": "https://www.reddit.com/something",
                }
            ),
            CreateObject(
                {
                    "author": None,
                    "created_utc": 1617324719,
                    "distinguished": None,
                    "edited": False,
                    "id": "test_submission_id",
                    "is_original_content": True,
                    "is_self": True,
                    "link_flair_text": None,
                    "locked": False,
                    "name": "t3_test",
                    "over_18": False,
                    "num_comments": 6,
                    "permalink": "r/test_sub",
                    "score": 6,
                    "selftext": "Some text here",
                    "spoiler": False,
                    "stickied": False,
                    "title": "A title here",
                    "upvote_ratio": 0.5,
                    "url": "https://www.reddit.com/something",
                }
            ),
        ]

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        Subreddit.FormatJSON.format_json(args, skeleton, submissions, subreddit)

        assert skeleton["data"]
        assert skeleton["subreddit_rules"]
        assert isinstance(skeleton["subreddit_rules"]["rules"], list)
        assert isinstance(skeleton["subreddit_rules"]["post_requirements"], dict)


class TestGetSortWriteGetSortMethod:
    """
    Testing GetSortWrite class _get_sort() method.
    """

    def test_get_sort_default_json_format(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args([])

        cat_i = "H"
        search_for = 1
        sub = "askreddit"

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = None

        skeleton = Subreddit.GetSortWrite._get_sort(
            args, cat_i, search_for, sub, subreddit, time_filter
        )

        assert skeleton["scrape_settings"]["subreddit"] == "askreddit"
        assert skeleton["scrape_settings"]["category"] == "hot"
        assert skeleton["scrape_settings"]["n_results_or_keywords"] == 1
        assert skeleton["scrape_settings"]["time_filter"] == None

        assert isinstance(skeleton["data"], list)

    def test_get_sort_csv_format(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--csv"])

        cat_i = "H"
        search_for = 1
        sub = "askreddit"

        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        time_filter = None

        overview = Subreddit.GetSortWrite._get_sort(
            args, cat_i, search_for, sub, subreddit, time_filter
        )

        fields = [
            "author",
            "created_utc",
            "distinguished",
            "edited",
            "id",
            "is_original_content",
            "is_self",
            "link_flair_text",
            "locked",
            "name",
            "nsfw",
            "num_comments",
            "permalink",
            "score",
            "selftext",
            "spoiler",
            "stickied",
            "title",
            "upvote_ratio",
            "url",
        ]

        for key in overview.keys():
            assert True if key in fields else False


class TestRunSubredditCreateSettingsMethod:
    """
    Testing RunSubreddit class create_settings() method.
    """

    def test_create_settings(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--subreddit", "askreddit", "h", "100"])
        reddit = Login.create_reddit_object()

        s_master = Subreddit.RunSubreddit._create_settings(args, reddit)

        assert s_master == {"askreddit": [["h", "100", None]]}
