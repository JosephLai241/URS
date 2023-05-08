"""
Testing `Tools.py`.
"""


import argparse
import os

import praw
from dotenv import load_dotenv

from urs.utils import Global, Tools


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
            username=os.getenv("USERNAME"),
            password=os.getenv("PASSWORD"),
        )


class TestRunInitMethod:
    """
    Testing Run class __init__() method.
    """

    def test_init_instance_variables(self):
        reddit = Login.create_reddit_object()

        try:
            Tools.Run(reddit)
            assert False
        except SystemExit:
            assert True
