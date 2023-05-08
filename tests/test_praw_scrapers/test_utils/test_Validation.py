"""
Testing `Validation.py`.
"""


import argparse
import os

import praw
from dotenv import load_dotenv

from urs.praw_scrapers.utils.Validation import Validation


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


class TestValidationValidateUserMethod:
    """
    Testing Validation class validate_user() method.
    """

    def test_validate_user(self):
        parser = MakeArgs.make_scraper_args()
        reddit = Login.create_reddit_object()

        try:
            Validation.validate_user(parser, reddit)
            assert True
        except:
            assert False


class TestValidationCheckSubredditsMethod:
    """
    Testing Validation class _check_subreddits() method.
    """

    def test_check_subreddits_only_valid_subreddits(self):
        invalid, valid = [], []
        reddit = Login.create_reddit_object()

        object_list = ["askreddit", "wallstreetbets", "cscareerquestions"]

        Validation._check_subreddits(invalid, object_list, reddit, valid)

        assert not invalid
        assert len(valid) == 3

    def test_check_subreddits_only_invalid_subreddits(self):
        invalid, valid = [], []
        reddit = Login.create_reddit_object()

        object_list = [
            "shdg8h342842h3gidbsfgjdbs",
            "asdfhauhwspf8912034812hudfghb979023974ht",
            "xcvhcsxiuvbeidefgh3qw48tr324805tyasdguap;l",
        ]

        Validation._check_subreddits(invalid, object_list, reddit, valid)

        assert not valid
        assert len(invalid) == 3

    def test_check_subreddit_both_valid_and_invalid_subreddits(self):
        invalid, valid = [], []
        reddit = Login.create_reddit_object()

        object_list = [
            "askreddit",
            "wallstreetbets",
            "cscareerquestions",
            "shdg8h342842h3gidbsfgjdbs",
            "asdfhauhwspf8912034812hudfghb979023974ht",
            "xcvhcsxiuvbeidefgh3qw48tr324805tyasdguap;l",
            "u0893-45u238hdusafghudsgh982",
        ]

        Validation._check_subreddits(invalid, object_list, reddit, valid)

        assert len(valid) == 3
        assert len(invalid) == 4


class TestValidationCheckRedditorsMethod:
    """
    Testing Validation class _check_redditors() method.
    """

    def test_check_redditor_only_valid_redditors(self):
        invalid, valid = [], []
        reddit = Login.create_reddit_object()

        object_list = ["spez"]

        Validation._check_redditors(invalid, object_list, reddit, valid)

        assert len(valid) == 1
        assert not invalid

    def test_check_redditor_only_invalid_redditors(self):
        invalid, valid = [], []
        reddit = Login.create_reddit_object()

        object_list = ["sdhfgiuoh3284th9enbsprgh8-w-wher9ghwe9hw49"]

        Validation._check_redditors(invalid, object_list, reddit, valid)

        assert not valid
        assert len(invalid) == 1

    def test_check_redditor_both_valid_and_invalid_redditors(self):
        invalid, valid = [], []
        reddit = Login.create_reddit_object()

        object_list = ["spez", "sdhfgiuoh3284th9enbsprgh8-w-wher9ghwe9hw49"]

        Validation._check_redditors(invalid, object_list, reddit, valid)

        assert len(valid) == 1
        assert len(invalid) == 1


class TestValidationCheckSubmissionsMethod:
    """
    Testing Validation class _check_submissions() method.
    """

    def test_check_submissions_only_valid_submissions(self):
        invalid, valid = [], []
        reddit = Login.create_reddit_object()

        object_list = [
            "https://www.reddit.com/r/announcements/comments/mcisdf/an_update_on_the_recent_issues_surrounding_a/"
        ]

        Validation._check_submissions(invalid, object_list, reddit, valid)

        assert len(valid) == 1
        assert not invalid

    def test_check_submissions_only_invalid_submissions(self):
        invalid, valid = [], []
        reddit = Login.create_reddit_object()

        object_list = [
            "https://www.reddit.com/r/heresaninvalidlinkjasdfhuwhrpguhpasdf/"
        ]

        Validation._check_submissions(invalid, object_list, reddit, valid)

        assert not valid
        assert len(invalid) == 1

    def test_check_submissions_both_valid_and_invalid_submissions(self):
        invalid, valid = [], []
        reddit = Login.create_reddit_object()

        object_list = [
            "https://www.reddit.com/r/announcements/comments/mcisdf/an_update_on_the_recent_issues_surrounding_a/",
            "https://www.reddit.com/r/heresaninvalidlinkjasdfhuwhrpguhpasdf/",
        ]

        Validation._check_submissions(invalid, object_list, reddit, valid)

        assert len(valid) == 1
        assert len(invalid) == 1


class TestValidationCheckExistenceMethod:
    """
    Testing Validation class check_existence() method.
    """

    def test_check_existence_only_valid_subreddits(self):
        reddit = Login.create_reddit_object()

        object_list = ["askreddit", "wallstreetbets", "cscareerquestions"]

        scraper_type = "subreddit"

        invalid, valid = Validation.check_existence(object_list, reddit, scraper_type)

        assert len(valid) == 3
        assert not invalid

    def test_check_existence_only_invalid_subreddits(self):
        reddit = Login.create_reddit_object()

        object_list = [
            "shdg8h342842h3gidbsfgjdbs",
            "asdfhauhwspf8912034812hudfghb979023974ht",
            "xcvhcsxiuvbeidefgh3qw48tr324805tyasdguap;l",
        ]

        scraper_type = "subreddit"

        invalid, valid = Validation.check_existence(object_list, reddit, scraper_type)

        assert not valid
        assert len(invalid) == 3

    def test_check_existence_both_valid_and_invalid_subreddits(self):
        reddit = Login.create_reddit_object()

        object_list = [
            "askreddit",
            "wallstreetbets",
            "cscareerquestions",
            "shdg8h342842h3gidbsfgjdbs",
            "asdfhauhwspf8912034812hudfghb979023974ht",
            "xcvhcsxiuvbeidefgh3qw48tr324805tyasdguap;l",
        ]

        scraper_type = "subreddit"

        invalid, valid = Validation.check_existence(object_list, reddit, scraper_type)

        assert len(valid) == 3
        assert len(invalid) == 3

    def test_check_existence_only_valid_redditors(self):
        reddit = Login.create_reddit_object()

        object_list = ["spez"]

        scraper_type = "redditor"

        invalid, valid = Validation.check_existence(object_list, reddit, scraper_type)

        assert len(valid) == 1
        assert not invalid

    def test_check_existence_only_invalid_redditors(self):
        reddit = Login.create_reddit_object()

        object_list = ["sdhfgiuoh3284th9enbsprgh8-w-wher9ghwe9hw49"]

        scraper_type = "redditor"

        invalid, valid = Validation.check_existence(object_list, reddit, scraper_type)

        assert not valid
        assert len(invalid) == 1

    def test_check_existence_both_valid_and_invalid_redditors(self):
        reddit = Login.create_reddit_object()

        object_list = ["spez", "sdhfgiuoh3284th9enbsprgh8-w-wher9ghwe9hw49"]

        scraper_type = "redditor"

        invalid, valid = Validation.check_existence(object_list, reddit, scraper_type)

        assert len(valid) == 1
        assert len(invalid) == 1

    def test_check_existence_only_valid_submissions(self):
        reddit = Login.create_reddit_object()

        object_list = [
            "https://www.reddit.com/r/announcements/comments/mcisdf/an_update_on_the_recent_issues_surrounding_a/"
        ]

        scraper_type = "comments"

        invalid, valid = Validation.check_existence(object_list, reddit, scraper_type)

        assert len(valid) == 1
        assert not invalid

    def test_check_existence_only_invalid_submissions(self):
        reddit = Login.create_reddit_object()

        object_list = [
            "https://www.reddit.com/r/heresaninvalidlinkjasdfhuwhrpguhpasdf/"
        ]

        scraper_type = "comments"

        invalid, valid = Validation.check_existence(object_list, reddit, scraper_type)

        assert not valid
        assert len(invalid) == 1

    def test_check_existence_both_valid_and_invalid_submissions(self):
        reddit = Login.create_reddit_object()

        object_list = [
            "https://www.reddit.com/r/announcements/comments/mcisdf/an_update_on_the_recent_issues_surrounding_a/",
            "https://www.reddit.com/r/heresaninvalidlinkjasdfhuwhrpguhpasdf/",
        ]

        scraper_type = "comments"

        invalid, valid = Validation.check_existence(object_list, reddit, scraper_type)

        assert len(valid) == 1
        assert len(invalid) == 1


class TestValidationValidateMethod:
    """
    Testing Validation class validate() method.
    """

    def test_validate_all_valid_reddit_objects(self):
        reddit = Login.create_reddit_object()

        object_list = ["askreddit", "wallstreetbets", "cscareerquestions"]

        scraper_type = "subreddit"

        invalid, valid = Validation.validate(object_list, reddit, scraper_type)

        assert len(valid) == 3
        assert not invalid

    def test_validate_both_valid_and_invalid_reddit_objects(self):
        reddit = Login.create_reddit_object()

        object_list = [
            "askreddit",
            "wallstreetbets",
            "cscareerquestions",
            "shdg8h342842h3gidbsfgjdbs",
            "asdfhauhwspf8912034812hudfghb979023974ht",
            "xcvhcsxiuvbeidefgh3qw48tr324805tyasdguap;l",
        ]

        scraper_type = "subreddit"

        invalid, valid = Validation.validate(object_list, reddit, scraper_type)

        assert len(valid) == 3
        assert len(invalid) == 3

    def test_validate_all_invalid_reddit_objects_force_quit(self):
        reddit = Login.create_reddit_object()

        object_list = [
            "shdg8h342842h3gidbsfgjdbs",
            "asdfhauhwspf8912034812hudfghb979023974ht",
            "xcvhcsxiuvbeidefgh3qw48tr324805tyasdguap;l",
        ]

        scraper_type = "subreddit"

        try:
            _, _ = Validation.validate(object_list, reddit, scraper_type)
            assert False
        except SystemExit:
            assert True
