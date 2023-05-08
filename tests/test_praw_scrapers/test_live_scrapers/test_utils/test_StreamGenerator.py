"""
Testing `StreamGenerator.py`.
"""


import os
import types

import praw
from dotenv import load_dotenv

from urs.praw_scrapers.live_scrapers.utils import StreamGenerator


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


class TestStreamGeneratorStreamSubmissionsMethod:
    """
    Testing StreamGenerator class stream_submissions() method.
    """

    def test_stream_submissions_method(self):
        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        generator = StreamGenerator.StreamGenerator.stream_submissions(subreddit.stream)

        assert isinstance(generator, types.GeneratorType)

        for obj in generator:
            if isinstance(obj, dict):
                assert True
                break


class TestStreamGeneratorStreamCommentsMethod:
    """
    Testing StreamGenerator class stream_comments() method.
    """

    def test_stream_comments_method(self):
        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        generator = StreamGenerator.StreamGenerator.stream_comments(subreddit.stream)

        assert isinstance(generator, types.GeneratorType)

        for obj in generator:
            if isinstance(obj, dict):
                assert True
                break
