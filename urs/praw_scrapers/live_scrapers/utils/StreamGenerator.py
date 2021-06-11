"""
Stream Generator
================
Defining methods for the stream generator which yields new Reddit objects and
converts them to JSON serializable objects when saving to file.
"""


from urs.praw_scrapers.utils.Objectify import Objectify

class StreamGenerator():
    """
    Methods for creating a generator which yields new Reddit objects while 
    streaming.
    """

    @staticmethod
    def stream_submissions(stream):
        """
        Yield new Reddit submissions.

        Parameters
        ----------
        stream: Reddit stream instance

        Yields
        ------
        submission: Reddit submission object 
        """

        for submission in stream.submissions(skip_existing = True):
            yield Objectify().make_submission(True, submission)

    @staticmethod
    def stream_comments(stream):
        """
        Yield new Reddit comments.

        Parameters
        ----------
        stream: Reddit stream instance

        Yields
        ------
        submission: Reddit comment object 
        """

        for comment in stream.comments(skip_existing = True):
            yield Objectify().make_comment(comment, True)
