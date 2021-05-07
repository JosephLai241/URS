"""
Stream Generator
================
Defining methods for the stream generator which yields new Reddit objects and
converts them to JSON serializable objects when saving to file.
"""


from urs.praw_scrapers.utils.Objectify import Objectify
from urs.utils.Global import convert_time

class StreamGenerator():
    """
    Methods for creating a generator which yields new Reddit objects while 
    streaming.
    """

    @staticmethod
    def single_stream(object_type, stream):
        """
        Yield new Reddit objects based on the `object_type` that is passed into 
        this method.

        Parameters
        ----------
        object_type: str
            String denoting the Reddit object's type
        stream: Reddit stream instance

        Yields
        ------
        reddit_object: 
        """

        if object_type == "submission":
            for submission in stream.submissions(skip_existing = True):
                yield Objectify().make_submission(False, submission)

        elif object_type == "comment":
            for comment in stream.comments(skip_existing = True):
                yield Objectify().make_comment(comment, True)
        
    @staticmethod
    def dual_stream(stream):
        """
        Yield both comments and submissions from the stream.

        Parameters
        ----------
        stream: Reddit stream instance

        Yields
        ------
        reddit_objects:
        """

        for comment, submission in zip(stream.comments(skip_existing = True), stream.submissions(skip_existing = True)):
            yield {
                "obj": Objectify().make_submission(False, submission), 
                "object_type": "submission"
            }

            yield {
                "obj": Objectify().make_comment(comment, True), 
                "object_type": "comment"
            }
