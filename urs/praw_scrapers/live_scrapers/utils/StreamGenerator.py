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

        if object_type == "submissions":
            for submission in stream.submissions(skip_existing = True):
                yield Objectify().make_submission(False, submission)

        elif object_type == "comments":
            for obj in stream.comments(skip_existing = True):
                print(type(obj))
        
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

        for comment, submission in zip(stream.comments(), stream.submissions()):
            print("%s ---- %s" % (type(comment), type(submission)))
