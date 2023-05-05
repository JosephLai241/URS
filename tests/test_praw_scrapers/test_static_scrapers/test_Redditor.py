"""
Testing `Redditor.py`.
"""


import os

import praw
from dotenv import load_dotenv

from urs.praw_scrapers.static_scrapers import Redditor
from urs.utils import Global


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


class TestGetInteractionsMakeJsonSkeletonMethod:
    """
    Testing GetInteractions class _make_json_skeleton() method.
    """

    def test_make_json_skeleton(self):
        reddit = Login.create_reddit_object()
        spez = reddit.redditor("spez")

        test_skeleton = {
            "scrape_settings": {"redditor": "spez", "n_results": 1},
            "data": {"information": None, "interactions": {}},
        }

        redditor, skeleton = Redditor.GetInteractions._make_json_skeleton(
            1, reddit, "spez"
        )

        assert redditor == spez
        assert skeleton == test_skeleton


class TestGetInteractionsGetTrophiesMethod:
    """
    Testing GetInteractions class _get_trophies() method.
    """

    def test_get_trophies(self):
        reddit = Login.create_reddit_object()
        spez = reddit.redditor("spez")

        trophies = Redditor.GetInteractions._get_trophies(spez)

        assert isinstance(trophies, list) == True
        assert len(trophies) > 0


class TestGetUserSubredditMethod:
    """
    Testing GetInteractions class _get_user_subreddit() method.
    """

    def test_get_user_subreddit(self):
        reddit = Login.create_reddit_object()
        spez = reddit.redditor("spez")

        redditor_subreddit = Redditor.GetInteractions._get_user_subreddit(spez)

        dict_fields = [
            "can_assign_link_flair",
            "can_assign_user_flair",
            "created_utc",
            "description",
            "description_html",
            "display_name",
            "id",
            "name",
            "nsfw",
            "public_description",
            "spoilers_enabled",
            "subscribers",
            "user_is_banned",
            "user_is_moderator",
            "user_is_subscriber",
        ]

        assert isinstance(redditor_subreddit, dict) == True

        for key in redditor_subreddit.keys():
            assert key in dict_fields


class TestGetInteractionsGetUserInfoMethod:
    """
    Testing GetInteractions class _get_user_info() method.
    """

    def test_get_user_info(self):
        reddit = Login.create_reddit_object()
        spez = reddit.redditor("spez")

        skeleton = {
            "scrape_settings": {"redditor": "spez", "n_results": 1},
            "data": {"information": None, "interactions": {}},
        }

        Redditor.GetInteractions._get_user_info(spez, skeleton)

        assert skeleton["data"]["information"] != None

        information_fields = [
            "comment_karma",
            "created_utc",
            "fullname",
            "has_verified_email",
            "icon_img",
            "id",
            "is_employee",
            "is_friend",
            "is_mod",
            "is_gold",
            "link_karma",
            "name",
            "subreddit",
            "trophies",
        ]
        for field in skeleton["data"]["information"].keys():
            assert True if field in information_fields else False


class TestGetInteractionsMakeInteractionsListsMethod:
    """
    Testing GetInteractions class _make_interactions_lists() method.
    """

    def test_make_interactions_lists(self):
        skeleton = {"data": {"interactions": {}}}

        Redditor.GetInteractions._make_interactions_lists(skeleton)

        interaction_titles = [
            "comments",
            "controversial",
            "downvoted",
            "gilded",
            "gildings",
            "hidden",
            "hot",
            "moderated",
            "multireddits",
            "new",
            "saved",
            "submissions",
            "top",
            "upvoted",
        ]
        for field in skeleton["data"]["interactions"].keys():
            assert True if field in interaction_titles else False

            assert skeleton["data"]["interactions"][field] == []


class TestGetInteractionsGetUserInteractionsMethod:
    """
    Testing GetInteractions class _get_user_interactions() method.
    """

    def test_get_user_interactions(self):
        reddit = Login.create_reddit_object()
        spez = reddit.redditor("spez")

        skeleton = {
            "scrape_settings": {"redditor": "spez", "n_results": 1},
            "data": {"information": None, "interactions": {}},
        }

        Redditor.GetInteractions._get_user_interactions(1, spez, skeleton)

        assert skeleton["data"]["information"] == None
        assert skeleton["data"]["interactions"]


class TestGetInteractionsGetMethod:
    """
    Testing GetInteractions class get() method.
    """

    def test_get(self):
        reddit = Login.create_reddit_object()
        spez = reddit.redditor("spez")

        skeleton = Redditor.GetInteractions.get(1, reddit, spez)

        assert skeleton["scrape_settings"]["redditor"] == "spez"
        assert skeleton["scrape_settings"]["n_results"] == 1

        assert skeleton["data"]["information"] != None

        assert len(skeleton["data"]["interactions"]["comments"])
        assert len(skeleton["data"]["interactions"]["controversial"])
        assert len(skeleton["data"]["interactions"]["gilded"])
        assert skeleton["data"]["interactions"]["gildings"][0] == "FORBIDDEN"
        assert skeleton["data"]["interactions"]["hidden"][0] == "FORBIDDEN"
        assert not skeleton["data"]["interactions"]["hot"]
        assert len(skeleton["data"]["interactions"]["moderated"])
        assert "multireddits" in skeleton["data"]["interactions"].keys()
        assert not skeleton["data"]["interactions"]["new"]
        assert skeleton["data"]["interactions"]["saved"][0] == "FORBIDDEN"
        assert not skeleton["data"]["interactions"]["submissions"]
        assert len(skeleton["data"]["interactions"]["top"])
        assert skeleton["data"]["interactions"]["upvoted"][0] == "FORBIDDEN"
