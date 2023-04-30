"""
Testing `Livestream.py`.
"""


import argparse
import os
import types

import praw
from dotenv import load_dotenv

from urs.praw_scrapers.live_scrapers import Livestream
from urs.utils.Global import date


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
        parser.add_argument("--live-subreddit")
        parser.add_argument("--live-redditor")
        parser.add_argument("--stream-submissions", action="store_true")

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


class TestSaveStreamCreateSkeletonMethod:
    """
    Testing SaveStream class _create_skeleton() method.
    """

    def test_create_skeleton_method_live_subreddit_default_streaming_comments_args(
        self,
    ):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args("--live-subreddit askreddit".split())

        skeleton = Livestream.SaveStream._create_skeleton(args)

        assert skeleton["livestream_settings"]["subreddit"] == "askreddit"
        assert skeleton["livestream_settings"]["included_reddit_objects"] == "comments"
        assert skeleton["data"] == []

    def test_create_skeleton_method_live_subreddit_streaming_submissions_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(
            "--live-subreddit askreddit --stream-submissions".split()
        )

        skeleton = Livestream.SaveStream._create_skeleton(args)

        assert skeleton["livestream_settings"]["subreddit"] == "askreddit"
        assert (
            skeleton["livestream_settings"]["included_reddit_objects"] == "submissions"
        )
        assert skeleton["data"] == []

    def test_create_skeleton_method_live_redditor_default_streaming_comments_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args("--live-redditor spez".split())

        skeleton = Livestream.SaveStream._create_skeleton(args)

        assert skeleton["livestream_settings"]["redditor"] == "spez"
        assert skeleton["livestream_settings"]["included_reddit_objects"] == "comments"
        assert skeleton["data"] == []

    def test_create_skeleton_method_live_redditor_streaming_submissions_args(self):
        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args("--live-redditor spez --stream-submissions".split())

        skeleton = Livestream.SaveStream._create_skeleton(args)

        assert skeleton["livestream_settings"]["redditor"] == "spez"
        assert (
            skeleton["livestream_settings"]["included_reddit_objects"] == "submissions"
        )
        assert skeleton["data"] == []


class TestSaveStreamMakeLivestreamDirMethod:
    """
    Testing SaveStream class _make_livestream_dir() method.
    """

    def test_make_livestream_dir_method_subreddits_subdirectory(self):
        test_split_stream_info = ["r"]

        stream_directory = Livestream.SaveStream._make_livestream_dir(
            test_split_stream_info
        )

        assert stream_directory == f"../scrapes/{date}/livestream/subreddits"

    def test_make_livestream_dir_method_redditors_subdirectory(self):
        test_split_stream_info = ["u"]

        stream_directory = Livestream.SaveStream._make_livestream_dir(
            test_split_stream_info
        )

        assert stream_directory == f"../scrapes/{date}/livestream/redditors"


class TestSaveStreamGetTempFilenameMethod:
    """
    Testing SaveStream class _get_temp_filename() method.
    """

    def test_get_temp_filename_method_with_subreddit(self):
        test_stream_info = "in r/askreddit"

        stream_path = Livestream.SaveStream._get_temp_filename(test_stream_info)

        assert stream_path == f"../scrapes/{date}/livestream/subreddits/askreddit.json"

    def test_get_temp_filename_method_with_redditor(self):
        test_stream_info = "by u/spez"

        stream_path = Livestream.SaveStream._get_temp_filename(test_stream_info)

        assert stream_path == f"../scrapes/{date}/livestream/redditors/spez.json"


class TestSaveStreamCreateTempFileMethod:
    """
    Testing SaveStream class _create_temp_file() method.
    """

    def test_create_temp_file_method(self):
        test_skeleton = {"test": 1}
        test_stream_path = "../scrapes/livestream/subreddits/askreddit.json"

        if not os.path.isdir("../scrapes/livestream/subreddits"):
            os.makedirs("../scrapes/livestream/subreddits")

        Livestream.SaveStream._create_temp_file(test_skeleton, test_stream_path)

        assert os.path.isfile(test_stream_path)


class TestSaveStreamRenameMethod:
    """
    Testing SaveStream class _rename() method.
    """

    def test_rename_method_with_subreddit(self):
        test_duration = "00:00:15"
        test_object_info = "comments"
        test_start_stream = "18:06:06"
        test_stream_path = f"../scrapes/{date}/livestream/subreddits/askreddit.json"

        with open(test_stream_path, "w", encoding="utf-8") as _:
            pass

        Livestream.SaveStream._rename(
            test_duration, test_object_info, test_start_stream, test_stream_path
        )

        renamed_file = f"../scrapes/{date}/livestream/subreddits/askreddit-comments-18_06_06-00_00_15.json"

        assert os.path.isfile(renamed_file)

    def test_rename_method_with_redditor(self):
        test_duration = "00:00:15"
        test_object_info = "submissions"
        test_start_stream = "18:06:06"
        test_stream_path = f"../scrapes/{date}/livestream/redditors/spez.json"

        with open(test_stream_path, "w", encoding="utf-8") as _:
            pass

        Livestream.SaveStream._rename(
            test_duration, test_object_info, test_start_stream, test_stream_path
        )

        renamed_file = f"../scrapes/{date}/livestream/redditors/spez-submissions-18_06_06-00_00_15.json"

        assert os.path.isfile(renamed_file)


class TestSaveStreamWriteMethod:
    """
    Testing SaveStream class write() method.
    """

    def test_write_method(self):
        pass


class TestLivestreamSetInfoAndObjectMethod:
    """
    Testing Livestream class _set_info_and_object() method.
    """

    def test_set_info_and_object_live_subreddit(self):
        reddit = Login.create_reddit_object()

        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args("--live-subreddit askreddit".split())

        reddit_object, stream_info = Livestream.Livestream._set_info_and_object(
            args, reddit
        )

        assert isinstance(reddit_object, praw.models.Subreddit)
        assert stream_info == "in r/askreddit"

    def test_set_info_and_object_live_redditor(self):
        reddit = Login.create_reddit_object()

        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args("--live-redditor spez".split())

        reddit_object, stream_info = Livestream.Livestream._set_info_and_object(
            args, reddit
        )

        assert isinstance(reddit_object, praw.models.Redditor)
        assert stream_info == "by u/spez"


class TestLivestreamStreamSwitchMethod:
    """
    Testing Livestream class _stream_switch() method.
    """

    def test_stream_switch_method_default_stream_comments(self):
        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args("--live-subreddit askreddit".split())

        generator, object_info = Livestream.Livestream._stream_switch(args, subreddit)

        assert isinstance(generator, types.GeneratorType)
        assert object_info == "comments"

    def test_stream_switch_method_stream_submissions(self):
        reddit = Login.create_reddit_object()
        subreddit = reddit.subreddit("askreddit")

        parser = MakeArgs.make_scraper_args()
        args = parser.parse_args(
            "--live-subreddit askreddit --stream-submissions".split()
        )

        generator, object_info = Livestream.Livestream._stream_switch(args, subreddit)

        assert isinstance(generator, types.GeneratorType)
        assert object_info == "submissions"


class TestLivestreamNoSaveStreamMethod:
    """
    Testing livestream class _no_save_stream() method.
    """

    def test_no_save_stream_method(self):
        pass


class TestLivestreamStreamMethod:
    """
    Testing Livestream class stream() method.
    """

    def test_stream_method_live_subreddit(self):
        pass

    def test_stream_method_live_redditor(self):
        pass
