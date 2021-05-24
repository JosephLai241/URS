"""
Testing `Comments.py`.
"""


import argparse
import os
import praw

from dotenv import load_dotenv

from urs.praw_scrapers.static_scrapers import Comments
from urs.utils.Export import EncodeNode

class MakeArgs():
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
        parser.add_argument("--raw", action = "store_true")

        return parser

class Login():
    """
    Create a Reddit object with PRAW API credentials.
    """

    @staticmethod
    def create_reddit_object():
        load_dotenv()

        return praw.Reddit(
            client_id = os.getenv("CLIENT_ID"),
            client_secret = os.getenv("CLIENT_SECRET"),
            user_agent = os.getenv("USER_AGENT"),
            username = os.getenv("REDDIT_USERNAME"),
            password = os.getenv("REDDIT_PASSWORD")
        )

class TestCommentNodeInitMethod():
    """
    Testing CommentNode class __init__() method.
    """

    def test_init_method_with_one_id_attribute(self):
        metadata = {
            "id": "test_id"
        }

        test_node = Comments.CommentNode(metadata)

        assert getattr(test_node, "id") == "test_id"
        assert getattr(test_node, "replies") == []

    def test_init_method_with_comment_metadata(self):
        metadata = {
            "author": "u/test",
            "body": "A top level comment here.",
            "created_utc": "06-06-2006 06:06:06",
            "distinguished": None,
            "edited": False,
            "id": "qwerty1",
            "is_submitter": False,
            "link_id": "t3_asdfgh",
            "parent_id": "t3_abc123",
            "score": 666,
            "stickied": False
        }

        test_node = Comments.CommentNode(metadata)

        assert getattr(test_node, "author") == "u/test"
        assert getattr(test_node, "body") == "A top level comment here."
        assert getattr(test_node, "created_utc") == "06-06-2006 06:06:06"
        assert getattr(test_node, "distinguished") == None
        assert getattr(test_node, "edited") == False
        assert getattr(test_node, "id") == "qwerty1"
        assert getattr(test_node, "is_submitter") == False
        assert getattr(test_node, "link_id") == "t3_asdfgh"
        assert getattr(test_node, "parent_id") == "t3_abc123"
        assert getattr(test_node, "score") == 666
        assert getattr(test_node, "stickied") == False

class TestForestInitMethod():
    """
    Testing Forest class __init__() method. 
    """

    def test_init_method_set_root(self):
        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/md0ny3/what_nonsensical_invasive_thoughts_do_you_have/"


        forest = Comments.Forest(
            reddit.submission(url = url),
            url
        )

        assert getattr(forest.root, "id") == "md0ny3"

class TestForestSeedMethod():
    """
    Testing Forest class seed() method.
    """

    def test_valid_reply_to_seed(self):
        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/md0ny3/what_nonsensical_invasive_thoughts_do_you_have/"


        forest = Comments.Forest(
            reddit.submission(url = url),
            url
        )

        metadata = {
            "body": "A test node.",
            "id": "test",
            "parent_id": "t1_md0ny3",
        }
        reply = Comments.CommentNode(metadata)

        EncodeNode().encode(reply)
        forest.seed(reply)

        assert len(forest.root.replies) == 1

    def test_invalid_reply_to_seed(self):
        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/md0ny3/what_nonsensical_invasive_thoughts_do_you_have/"


        forest = Comments.Forest(
            reddit.submission(url = url),
            url
        )

        metadata = {
            "body": "A test node.",
            "id": "test",
            "parent_id": "t1_inv@l1d",
        }
        reply = Comments.CommentNode(metadata)

        EncodeNode().encode(reply)
        
        try:
            forest.seed(reply)
            assert False
        except IndexError:
            assert True
            assert len(forest.root.replies) == 0

class TestSortCommentsSortRawMethod():
    """
    Testing SortComments class sort_raw() method.
    """

    def test_sort_raw_method(self):
        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"


        all_comments = []
        submission = reddit.submission(url = url)

        Comments.SortComments().sort_raw(all_comments, submission)

        assert len(all_comments) > 0

    def test_sort_structured_method(self):
        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"

        submission = reddit.submission(url = url)

        forest_replies = Comments.SortComments().sort_structured(submission, url)

        assert len(forest_replies) > 0

class TestGetSortGetSortMethod():
    """
    Testing GetSort class get_sort() method.
    """

    def test_get_sort_raw_flag_is_included_with_no_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--raw"])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url = url)

        test_get_sort = Comments.GetSort(args, submission, url)

        all_comments = test_get_sort.get_sort(args, 0)
    
        assert len(all_comments) > 0

    def test_get_sort_raw_flag_is_included_with_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(["--raw"])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url = url)

        test_get_sort = Comments.GetSort(args, submission, url)

        all_comments = test_get_sort.get_sort(args, 1)
    
        assert len(all_comments) == 1
    
    def test_get_sort_no_raw_flag_is_included_with_no_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args([])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url = url)

        test_get_sort = Comments.GetSort(args, submission, url)

        all_comments = test_get_sort.get_sort(args, 0)
    
        assert len(all_comments) > 0

    def test_get_sort_no_raw_flag_is_included_with_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args([])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url = url)

        test_get_sort = Comments.GetSort(args, submission, url)

        all_comments = test_get_sort.get_sort(args, 1)
    
        assert len(all_comments) == 1
    
class TestWriteMakeJsonSkeletonMethod():
    """
    Testing Write class _make_json_skeleton() method.
    """

    def test_make_json_skeleton_structured_scrape_with_no_limit(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args([])

        reddit = Login.create_reddit_object()
        url = "https://www.reddit.com/r/AskReddit/comments/mg8fhz/if_you_could_tell_yourself_anything_what_would/"
        submission = reddit.submission(url = url)

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
        submission = reddit.submission(url = url)

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
        submission = reddit.submission(url = url)

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
        submission = reddit.submission(url = url)

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
