"""
Stream Generator
================
Defining methods for the stream generator which yields new Reddit objects and
converts them to JSON serializable objects when saving to file.
"""


from typing import Any, Dict, Generator, Union

from praw.models.reddit.redditor import RedditorStream
from praw.models.reddit.subreddit import SubredditStream

from urs.praw_scrapers.utils.Objectify import Objectify


class StreamGenerator:
    """
    Methods for creating a generator which yields new Reddit objects while
    streaming.
    """

    @staticmethod
    def stream_submissions(
        stream: Union[RedditorStream, SubredditStream]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Yield new Reddit submissions.

        :param RedditorStream | SubredditStream stream: The Reddit stream instance.

        :yields: Reddit submission object.
        """

        for submission in stream.submissions(skip_existing=True):
            yield Objectify().make_submission(True, submission)

    @staticmethod
    def stream_comments(
        stream: Union[RedditorStream, SubredditStream]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Yield new Reddit comments.

        :param RedditorStream | SubredditStream stream: The Reddit stream instance.

        :yields: Reddit comment object.
        """

        for comment in stream.comments(skip_existing=True):
            yield Objectify().make_comment(comment, True)
