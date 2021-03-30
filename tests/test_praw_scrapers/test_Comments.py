"""
Testing `Comments.py`.
"""


import os
import praw

from dotenv import load_dotenv

from urs.praw_scrapers import Comments
from urs.utils.Export import EncodeNode

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
            username = os.getenv("USERNAME"),
            password = os.getenv("PASSWORD")
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
        pass