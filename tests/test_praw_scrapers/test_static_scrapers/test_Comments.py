"""
Testing `Comments.py`.
"""


import argparse
import os

import praw
from dotenv import load_dotenv

from urs.praw_scrapers.static_scrapers import Comments


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
        parser.add_argument("--raw", action="store_true")

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


class TestSortCommentsSortRawMethod:
    """
    Testing SortComments class sort_raw() method.
    """

    def test_sort_raw_method(self):
        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"

        all_comments = []
        submission = reddit.submission(url=url)

        Comments.SortComments().sort_raw(all_comments, submission)

        assert len(all_comments) > 0

    def test_sort_structured_method(self):
        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"

        submission = reddit.submission(url=url)

        forest_replies = Comments.SortComments().sort_structured(submission, url)

        assert len(forest_replies) > 0


class TestGetSortGetSortMethod:
    """
    Testing GetSort class get_sort() method.
    """

    def test_get_sort_raw_flag_is_included_with_no_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--raw"])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url=url)

        test_get_sort = Comments.GetSort(args, submission, url)

        all_comments = test_get_sort.get_sort(args, 0)

        assert len(all_comments) > 0

    def test_get_sort_raw_flag_is_included_with_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--raw"])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url=url)

        test_get_sort = Comments.GetSort(args, submission, url)

        all_comments = test_get_sort.get_sort(args, 1)

        assert len(all_comments) == 1

    def test_get_sort_no_raw_flag_is_included_with_no_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args([])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url=url)

        test_get_sort = Comments.GetSort(args, submission, url)

        all_comments = test_get_sort.get_sort(args, 0)

        assert len(all_comments) > 0

    def test_get_sort_no_raw_flag_is_included_with_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args([])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url=url)

        test_get_sort = Comments.GetSort(args, submission, url)

        all_comments = test_get_sort.get_sort(args, 1)

        assert len(all_comments) == 1


class TestWriteMakeJsonSkeletonMethod:
    """
    Testing Write class _make_json_skeleton() method.
    """

    def test_make_json_skeleton_structured_scrape_with_no_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args([])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url=url)

        skeleton = Comments.Write._make_json_skeleton(args, 0, submission, url)

        assert skeleton["scrape_settings"]["n_results"] == "all"
        assert skeleton["scrape_settings"]["style"] == "structured"
        assert skeleton["scrape_settings"]["url"] == url

        assert skeleton["data"]["submission_metadata"]["author"] != None
        assert skeleton["data"]["submission_metadata"]["created_utc"] != None
        assert skeleton["data"]["submission_metadata"]["edited"] != None
        assert skeleton["data"]["submission_metadata"]["is_original_content"] != None
        assert skeleton["data"]["submission_metadata"]["is_self"] != None
        assert skeleton["data"]["submission_metadata"]["locked"] != None
        assert skeleton["data"]["submission_metadata"]["num_comments"] > 0
        assert skeleton["data"]["submission_metadata"]["nsfw"] != None
        assert skeleton["data"]["submission_metadata"]["permalink"] != None
        assert skeleton["data"]["submission_metadata"]["score"] != None
        assert skeleton["data"]["submission_metadata"]["selftext"] != None
        assert skeleton["data"]["submission_metadata"]["spoiler"] != None
        assert skeleton["data"]["submission_metadata"]["stickied"] != None
        assert skeleton["data"]["submission_metadata"]["subreddit"] != None
        assert skeleton["data"]["submission_metadata"]["title"] != None
        assert skeleton["data"]["submission_metadata"]["upvote_ratio"] != None

        assert skeleton["data"]["comments"] == None

    def test_make_json_skeleton_structured_scrape_with_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args([])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url=url)

        skeleton = Comments.Write._make_json_skeleton(args, 1, submission, url)

        assert skeleton["scrape_settings"]["n_results"] == 1
        assert skeleton["scrape_settings"]["style"] == "structured"
        assert skeleton["scrape_settings"]["url"] == url

        assert skeleton["data"]["submission_metadata"]["author"] != None
        assert skeleton["data"]["submission_metadata"]["created_utc"] != None
        assert skeleton["data"]["submission_metadata"]["edited"] != None
        assert skeleton["data"]["submission_metadata"]["is_original_content"] != None
        assert skeleton["data"]["submission_metadata"]["is_self"] != None
        assert skeleton["data"]["submission_metadata"]["locked"] != None
        assert skeleton["data"]["submission_metadata"]["num_comments"] > 0
        assert skeleton["data"]["submission_metadata"]["nsfw"] != None
        assert skeleton["data"]["submission_metadata"]["permalink"] != None
        assert skeleton["data"]["submission_metadata"]["score"] != None
        assert skeleton["data"]["submission_metadata"]["selftext"] != None
        assert skeleton["data"]["submission_metadata"]["spoiler"] != None
        assert skeleton["data"]["submission_metadata"]["stickied"] != None
        assert skeleton["data"]["submission_metadata"]["subreddit"] != None
        assert skeleton["data"]["submission_metadata"]["title"] != None
        assert skeleton["data"]["submission_metadata"]["upvote_ratio"] != None

        assert skeleton["data"]["comments"] == None

    def test_make_json_skeleton_raw_with_no_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--raw"])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url=url)

        skeleton = Comments.Write._make_json_skeleton(args, 0, submission, url)

        assert skeleton["scrape_settings"]["n_results"] == "all"
        assert skeleton["scrape_settings"]["style"] == "raw"
        assert skeleton["scrape_settings"]["url"] == url

        assert skeleton["data"]["submission_metadata"]["author"] != None
        assert skeleton["data"]["submission_metadata"]["created_utc"] != None
        assert skeleton["data"]["submission_metadata"]["edited"] != None
        assert skeleton["data"]["submission_metadata"]["is_original_content"] != None
        assert skeleton["data"]["submission_metadata"]["is_self"] != None
        assert skeleton["data"]["submission_metadata"]["locked"] != None
        assert skeleton["data"]["submission_metadata"]["num_comments"] > 0
        assert skeleton["data"]["submission_metadata"]["nsfw"] != None
        assert skeleton["data"]["submission_metadata"]["permalink"] != None
        assert skeleton["data"]["submission_metadata"]["score"] != None
        assert skeleton["data"]["submission_metadata"]["selftext"] != None
        assert skeleton["data"]["submission_metadata"]["spoiler"] != None
        assert skeleton["data"]["submission_metadata"]["stickied"] != None
        assert skeleton["data"]["submission_metadata"]["subreddit"] != None
        assert skeleton["data"]["submission_metadata"]["title"] != None
        assert skeleton["data"]["submission_metadata"]["upvote_ratio"] != None

        assert skeleton["data"]["comments"] == None

    def test_make_json_skeleton_raw_with_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--raw"])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url=url)

        skeleton = Comments.Write._make_json_skeleton(args, 1, submission, url)

        assert skeleton["scrape_settings"]["n_results"] == 1
        assert skeleton["scrape_settings"]["style"] == "raw"
        assert skeleton["scrape_settings"]["url"] == url

        assert skeleton["data"]["submission_metadata"]["author"] != None
        assert skeleton["data"]["submission_metadata"]["created_utc"] != None
        assert skeleton["data"]["submission_metadata"]["edited"] != None
        assert skeleton["data"]["submission_metadata"]["is_original_content"] != None
        assert skeleton["data"]["submission_metadata"]["is_self"] != None
        assert skeleton["data"]["submission_metadata"]["locked"] != None
        assert skeleton["data"]["submission_metadata"]["num_comments"] > 0
        assert skeleton["data"]["submission_metadata"]["nsfw"] != None
        assert skeleton["data"]["submission_metadata"]["permalink"] != None
        assert skeleton["data"]["submission_metadata"]["score"] != None
        assert skeleton["data"]["submission_metadata"]["selftext"] != None
        assert skeleton["data"]["submission_metadata"]["spoiler"] != None
        assert skeleton["data"]["submission_metadata"]["stickied"] != None
        assert skeleton["data"]["submission_metadata"]["subreddit"] != None
        assert skeleton["data"]["submission_metadata"]["title"] != None
        assert skeleton["data"]["submission_metadata"]["upvote_ratio"] != None

        assert skeleton["data"]["comments"] == None
