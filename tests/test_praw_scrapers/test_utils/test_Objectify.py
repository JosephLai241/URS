"""
Testing `Subreddit.py`.
"""


from urs.praw_scrapers.utils.Objectify import Objectify


class CreateObject:
    """
    Creating a fake Reddit object for testing.
    """

    def __init__(self, metadata):
        for key, value in metadata.items():
            self.__setattr__(key, value)


class TestObjectifyMakeCommentMethod:
    """
    Testing Objectify class make_comment() method.
    """

    def test_make_comment_not_including_all_deleted_author_not_edited(self):
        test_comment = CreateObject(
            {
                "author": None,
                "body": "test body",
                "body_html": "<p>test body</p>",
                "created_utc": 1617324719,
                "distinguished": None,
                "edited": False,
                "id": "t35t",
                "is_submitter": True,
                "link_id": "t3_asdf",
                "parent_id": "t3_asdf",
                "score": 666,
                "stickied": False,
            }
        )

        created_comment = Objectify().make_comment(test_comment, False)

        assert created_comment["author"] == "[deleted]"
        assert created_comment["body"] == "test body"
        assert created_comment["body_html"] == "<p>test body</p>"
        assert created_comment["created_utc"] == "2021-04-02 00:51:59"
        assert created_comment["distinguished"] == None
        assert created_comment["edited"] == False
        assert created_comment["id"] == "t35t"
        assert created_comment["is_submitter"] == True
        assert created_comment["link_id"] == "t3_asdf"
        assert created_comment["parent_id"] == "t3_asdf"
        assert created_comment["score"] == 666
        assert created_comment["stickied"] == False

    def test_make_comment_not_including_all_valid_author_edited(self):
        test_comment = CreateObject(
            {
                "author": CreateObject({"name": "test"}),
                "body": "test body",
                "body_html": "<p>test body</p>",
                "created_utc": 1617324719,
                "distinguished": None,
                "edited": 1617324959,
                "id": "t35t",
                "is_submitter": True,
                "link_id": "t3_asdf",
                "parent_id": "t3_asdf",
                "score": 666,
                "stickied": False,
            }
        )

        created_comment = Objectify().make_comment(test_comment, False)

        assert created_comment["author"] == "u/test"
        assert created_comment["body"] == "test body"
        assert created_comment["body_html"] == "<p>test body</p>"
        assert created_comment["created_utc"] == "2021-04-02 00:51:59"
        assert created_comment["distinguished"] == None
        assert created_comment["edited"] == "2021-04-02 00:55:59"
        assert created_comment["id"] == "t35t"
        assert created_comment["is_submitter"] == True
        assert created_comment["link_id"] == "t3_asdf"
        assert created_comment["parent_id"] == "t3_asdf"
        assert created_comment["score"] == 666
        assert created_comment["stickied"] == False

    def test_make_comment_including_all(self):
        test_comment = CreateObject(
            {
                "author": CreateObject({"name": "test"}),
                "body": "test body",
                "body_html": "<p>test body</p>",
                "created_utc": 1617324719,
                "distinguished": None,
                "edited": 1617324959,
                "id": "t35t",
                "is_submitter": True,
                "link_id": "t3_asdf",
                "parent_id": "t3_asdf",
                "score": 666,
                "stickied": False,
                "submission": CreateObject(
                    {
                        "author": CreateObject({"name": "submission_test_name"}),
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
                        "subreddit": CreateObject(
                            {
                                "can_assign_link_flair": False,
                                "can_assign_user_flair": False,
                                "created_utc": 1617324719,
                                "description": "#Description here",
                                "description_html": "<p>Description here</p>",
                                "display_name": "TestSub",
                                "id": 66666,
                                "name": "t5_66666",
                                "over18": False,
                                "public_description": "A test Subreddit",
                                "spoilers_enabled": True,
                                "subscribers": 666,
                                "user_is_banned": False,
                                "user_is_moderator": False,
                                "user_is_subscriber": False,
                            }
                        ),
                        "title": "A title here",
                        "upvote_ratio": 0.5,
                        "url": "https://www.reddit.com/something",
                    }
                ),
                "subreddit_id": "test_id",
            }
        )

        created_comment = Objectify().make_comment(test_comment, True)

        assert created_comment["author"] == "u/test"
        assert created_comment["body"] == "test body"
        assert created_comment["body_html"] == "<p>test body</p>"
        assert created_comment["created_utc"] == "2021-04-02 00:51:59"
        assert created_comment["distinguished"] == None
        assert created_comment["edited"] == "2021-04-02 00:55:59"
        assert created_comment["id"] == "t35t"
        assert created_comment["is_submitter"] == True
        assert created_comment["link_id"] == "t3_asdf"
        assert created_comment["parent_id"] == "t3_asdf"
        assert created_comment["score"] == 666
        assert created_comment["stickied"] == False
        assert created_comment["subreddit_id"] == "test_id"
        assert created_comment["type"] == "comment"

        assert created_comment["submission"]["author"] == "u/submission_test_name"
        assert created_comment["submission"]["created_utc"] == "2021-04-02 00:51:59"
        assert created_comment["submission"]["distinguished"] == None
        assert created_comment["submission"]["edited"] == False
        assert created_comment["submission"]["id"] == "test_submission_id"
        assert created_comment["submission"]["is_original_content"] == True
        assert created_comment["submission"]["is_self"] == True
        assert created_comment["submission"]["link_flair_text"] == None
        assert created_comment["submission"]["locked"] == False
        assert created_comment["submission"]["name"] == "t3_test"
        assert created_comment["submission"]["nsfw"] == False
        assert created_comment["submission"]["num_comments"] == 6
        assert created_comment["submission"]["permalink"] == "r/test_sub"
        assert created_comment["submission"]["score"] == 6
        assert created_comment["submission"]["selftext"] == "Some text here"
        assert created_comment["submission"]["spoiler"] == False
        assert created_comment["submission"]["stickied"] == False
        assert created_comment["submission"]["title"] == "A title here"
        assert created_comment["submission"]["upvote_ratio"] == 0.5
        assert (
            created_comment["submission"]["url"] == "https://www.reddit.com/something"
        )

        assert (
            created_comment["submission"]["subreddit"]["can_assign_link_flair"] == False
        )
        assert (
            created_comment["submission"]["subreddit"]["can_assign_user_flair"] == False
        )
        assert (
            created_comment["submission"]["subreddit"]["created_utc"]
            == "2021-04-02 00:51:59"
        )
        assert (
            created_comment["submission"]["subreddit"]["description"]
            == "#Description here"
        )
        assert (
            created_comment["submission"]["subreddit"]["description_html"]
            == "<p>Description here</p>"
        )
        assert created_comment["submission"]["subreddit"]["display_name"] == "TestSub"
        assert created_comment["submission"]["subreddit"]["id"] == 66666
        assert created_comment["submission"]["subreddit"]["name"] == "t5_66666"
        assert created_comment["submission"]["subreddit"]["nsfw"] == False
        assert (
            created_comment["submission"]["subreddit"]["public_description"]
            == "A test Subreddit"
        )
        assert created_comment["submission"]["subreddit"]["spoilers_enabled"] == True
        assert created_comment["submission"]["subreddit"]["subscribers"] == 666
        assert created_comment["submission"]["subreddit"]["user_is_banned"] == False
        assert created_comment["submission"]["subreddit"]["user_is_moderator"] == False
        assert created_comment["submission"]["subreddit"]["user_is_subscriber"] == False


class TestObjectifyMakeMultireddit:
    """
    Testing Objectify class make_multireddit() method.
    """

    def test_make_multireddit_no_subreddits(self):
        test_multireddit = CreateObject(
            {
                "can_edit": True,
                "copied_from": "somewhere",
                "created_utc": 1617324719,
                "description_html": "<p>Multireddit description here</p>",
                "description_md": "#Multireddit description here",
                "display_name": "Test Multireddit",
                "name": "Test",
                "over_18": False,
                "subreddits": None,
                "visibility": "Some visibility here",
            }
        )

        created_multireddit = Objectify().make_multireddit(test_multireddit)

        assert created_multireddit["can_edit"] == True
        assert created_multireddit["copied_from"] == "somewhere"
        assert created_multireddit["created_utc"] == "2021-04-02 00:51:59"
        assert (
            created_multireddit["description_html"]
            == "<p>Multireddit description here</p>"
        )
        assert created_multireddit["description_md"] == "#Multireddit description here"
        assert created_multireddit["display_name"] == "Test Multireddit"
        assert created_multireddit["name"] == "Test"
        assert created_multireddit["nsfw"] == False
        assert created_multireddit["subreddits"] == []
        assert created_multireddit["visibility"] == "Some visibility here"

    def test_make_multireddit_subreddits_present(self):
        test_multireddit = CreateObject(
            {
                "can_edit": True,
                "copied_from": "somewhere",
                "created_utc": 1617324719,
                "description_html": "<p>Multireddit description here</p>",
                "description_md": "#Multireddit description here",
                "display_name": "Test Multireddit",
                "name": "Test",
                "over_18": False,
                "subreddits": [
                    CreateObject(
                        {
                            "can_assign_link_flair": False,
                            "can_assign_user_flair": False,
                            "created_utc": 1617324719,
                            "description": "#Description here",
                            "description_html": "<p>Description here</p>",
                            "display_name": "TestSub",
                            "id": 66666,
                            "name": "t5_66666",
                            "over18": False,
                            "public_description": "A test Subreddit",
                            "spoilers_enabled": True,
                            "subscribers": 666,
                            "user_is_banned": False,
                            "user_is_moderator": False,
                            "user_is_subscriber": False,
                        }
                    ),
                    CreateObject(
                        {
                            "can_assign_link_flair": False,
                            "can_assign_user_flair": False,
                            "created_utc": 1617324719,
                            "description": "#Description here",
                            "description_html": "<p>Description here</p>",
                            "display_name": "TestSub",
                            "id": 66666,
                            "name": "t5_66666",
                            "over18": False,
                            "public_description": "A test Subreddit",
                            "spoilers_enabled": True,
                            "subscribers": 666,
                            "user_is_banned": False,
                            "user_is_moderator": False,
                            "user_is_subscriber": False,
                        }
                    ),
                ],
                "visibility": "Some visibility here",
            }
        )

        created_multireddit = Objectify().make_multireddit(test_multireddit)

        assert created_multireddit["can_edit"] == True
        assert created_multireddit["copied_from"] == "somewhere"
        assert created_multireddit["created_utc"] == "2021-04-02 00:51:59"
        assert (
            created_multireddit["description_html"]
            == "<p>Multireddit description here</p>"
        )
        assert created_multireddit["description_md"] == "#Multireddit description here"
        assert created_multireddit["display_name"] == "Test Multireddit"
        assert created_multireddit["name"] == "Test"
        assert created_multireddit["nsfw"] == False
        assert created_multireddit["visibility"] == "Some visibility here"

        for subreddit in created_multireddit["subreddits"]:
            assert subreddit["can_assign_link_flair"] == False
            assert subreddit["can_assign_user_flair"] == False
            assert subreddit["created_utc"] == "2021-04-02 00:51:59"
            assert subreddit["description"] == "#Description here"
            assert subreddit["description_html"] == "<p>Description here</p>"
            assert subreddit["display_name"] == "TestSub"
            assert subreddit["id"] == 66666
            assert subreddit["name"] == "t5_66666"
            assert subreddit["nsfw"] == False
            assert subreddit["public_description"] == "A test Subreddit"
            assert subreddit["spoilers_enabled"] == True
            assert subreddit["subscribers"] == 666
            assert subreddit["user_is_banned"] == False
            assert subreddit["user_is_moderator"] == False
            assert subreddit["user_is_subscriber"] == False


class TestObjectifyMakeSubmission:
    """
    Testing Objectify class make_submission() method.
    """

    def test_make_submission_not_including_all_deleted_author_not_edited(self):
        test_submission = CreateObject(
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
        )

        created_submission = Objectify().make_submission(False, test_submission)

        assert created_submission["author"] == "[deleted]"
        assert created_submission["created_utc"] == "2021-04-02 00:51:59"
        assert created_submission["distinguished"] == None
        assert created_submission["edited"] == False
        assert created_submission["id"] == "test_submission_id"
        assert created_submission["is_original_content"] == True
        assert created_submission["is_self"] == True
        assert created_submission["link_flair_text"] == None
        assert created_submission["locked"] == False
        assert created_submission["name"] == "t3_test"
        assert created_submission["nsfw"] == False
        assert created_submission["num_comments"] == 6
        assert created_submission["permalink"] == "r/test_sub"
        assert created_submission["score"] == 6
        assert created_submission["selftext"] == "Some text here"
        assert created_submission["spoiler"] == False
        assert created_submission["stickied"] == False
        assert created_submission["title"] == "A title here"
        assert created_submission["upvote_ratio"] == 0.5
        assert created_submission["url"] == "https://www.reddit.com/something"

    def test_make_submission_not_including_all_valid_author_edited(self):
        test_submission = CreateObject(
            {
                "author": CreateObject({"name": "submission_test_name"}),
                "created_utc": 1617324719,
                "distinguished": None,
                "edited": 1617324959,
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
        )

        created_submission = Objectify().make_submission(False, test_submission)

        assert created_submission["author"] == "u/submission_test_name"
        assert created_submission["created_utc"] == "2021-04-02 00:51:59"
        assert created_submission["distinguished"] == None
        assert created_submission["edited"] == "2021-04-02 00:55:59"
        assert created_submission["id"] == "test_submission_id"
        assert created_submission["is_original_content"] == True
        assert created_submission["is_self"] == True
        assert created_submission["link_flair_text"] == None
        assert created_submission["locked"] == False
        assert created_submission["name"] == "t3_test"
        assert created_submission["nsfw"] == False
        assert created_submission["num_comments"] == 6
        assert created_submission["permalink"] == "r/test_sub"
        assert created_submission["score"] == 6
        assert created_submission["selftext"] == "Some text here"
        assert created_submission["spoiler"] == False
        assert created_submission["stickied"] == False
        assert created_submission["title"] == "A title here"
        assert created_submission["upvote_ratio"] == 0.5
        assert created_submission["url"] == "https://www.reddit.com/something"

    def test_make_submission_including_all(self):
        test_submission = CreateObject(
            {
                "author": CreateObject({"name": "submission_test_name"}),
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
                "subreddit": CreateObject(
                    {
                        "can_assign_link_flair": False,
                        "can_assign_user_flair": False,
                        "created_utc": 1617324719,
                        "description": "#Description here",
                        "description_html": "<p>Description here</p>",
                        "display_name": "TestSub",
                        "id": 66666,
                        "name": "t5_66666",
                        "over18": False,
                        "public_description": "A test Subreddit",
                        "spoilers_enabled": True,
                        "subscribers": 666,
                        "user_is_banned": False,
                        "user_is_moderator": False,
                        "user_is_subscriber": False,
                    }
                ),
                "title": "A title here",
                "upvote_ratio": 0.5,
                "url": "https://www.reddit.com/something",
            }
        )

        created_submission = Objectify().make_submission(True, test_submission)

        assert created_submission["author"] == "u/submission_test_name"
        assert created_submission["created_utc"] == "2021-04-02 00:51:59"
        assert created_submission["distinguished"] == None
        assert created_submission["edited"] == False
        assert created_submission["id"] == "test_submission_id"
        assert created_submission["is_original_content"] == True
        assert created_submission["is_self"] == True
        assert created_submission["link_flair_text"] == None
        assert created_submission["locked"] == False
        assert created_submission["name"] == "t3_test"
        assert created_submission["nsfw"] == False
        assert created_submission["num_comments"] == 6
        assert created_submission["permalink"] == "r/test_sub"
        assert created_submission["score"] == 6
        assert created_submission["selftext"] == "Some text here"
        assert created_submission["spoiler"] == False
        assert created_submission["stickied"] == False
        assert created_submission["title"] == "A title here"
        assert created_submission["upvote_ratio"] == 0.5
        assert created_submission["url"] == "https://www.reddit.com/something"

        assert created_submission["subreddit"]["can_assign_link_flair"] == False
        assert created_submission["subreddit"]["can_assign_user_flair"] == False
        assert created_submission["subreddit"]["created_utc"] == "2021-04-02 00:51:59"
        assert created_submission["subreddit"]["description"] == "#Description here"
        assert (
            created_submission["subreddit"]["description_html"]
            == "<p>Description here</p>"
        )
        assert created_submission["subreddit"]["display_name"] == "TestSub"
        assert created_submission["subreddit"]["id"] == 66666
        assert created_submission["subreddit"]["name"] == "t5_66666"
        assert created_submission["subreddit"]["nsfw"] == False
        assert (
            created_submission["subreddit"]["public_description"] == "A test Subreddit"
        )
        assert created_submission["subreddit"]["spoilers_enabled"] == True
        assert created_submission["subreddit"]["subscribers"] == 666
        assert created_submission["subreddit"]["user_is_banned"] == False
        assert created_submission["subreddit"]["user_is_moderator"] == False
        assert created_submission["subreddit"]["user_is_subscriber"] == False
