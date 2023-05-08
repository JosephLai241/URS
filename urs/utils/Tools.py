"""
Tools
=====
Running all tools that URS has to offer.
"""


import logging
from argparse import ArgumentParser, Namespace
from typing import Tuple

from praw import Reddit

from urs.analytics.Frequencies import GenerateFrequencies
from urs.analytics.Wordcloud import GenerateWordcloud
from urs.praw_scrapers.live_scrapers.Livestream import Livestream
from urs.praw_scrapers.static_scrapers.Basic import RunBasic
from urs.praw_scrapers.static_scrapers.Comments import RunComments
from urs.praw_scrapers.static_scrapers.Redditor import RunRedditor
from urs.praw_scrapers.static_scrapers.Subreddit import RunSubreddit
from urs.praw_scrapers.utils.Validation import Validation
from urs.utils.Cli import CheckCli, Parser
from urs.utils.Titles import MainTitle
from urs.utils.Utilities import DateTree


class Run:
    """
    Methods to call CLI and all tools.
    """

    def __init__(self, reddit: Reddit) -> None:
        """
        Initialize variables used in instance methods:

            self._reddit: Reddit instance
            self._args: argparse Namespace object
            self._parser: argparse ArgumentParser object

        :param Reddit reddit: PRAW `Reddit` object.
        """

        self._reddit = reddit
        self._args, self._parser = self._introduce_then_args()

    def _introduce_then_args(self) -> Tuple[Namespace, ArgumentParser]:
        """
        Print title, then run checks for CLI args and PRAW credentials.

        :returns: The `Namespace` and `ArgumentParser` objects.
        :rtype: `(Namespace, ArgumentParser)`
        """

        MainTitle.title()

        args, parser = Parser().parse_args()
        CheckCli().check_args(args)

        return args, parser

    def run_urs(self) -> None:
        """
        Switch for running all URS tools.
        """

        if self._args.check:
            """
            Run rate limit check.
            """

            logging.info("RUNNING API CREDENTIALS CHECK.")
            logging.info("")

            Validation.validate_user(self._parser, self._reddit)

        elif self._args.tree:
            """
            Display visual directory tree for a date (default is the current date).
            """

            DateTree.display_tree(self._args.tree)

        elif (
            self._args.subreddit
            or self._args.redditor
            or self._args.comments
            or self._args.basic
        ):
            """
            Run PRAW scrapers.
            """

            Validation.validate_user(self._parser, self._reddit)

            if self._args.subreddit:
                RunSubreddit.run(self._args, self._reddit)
            if self._args.redditor:
                RunRedditor.run(self._args, self._reddit)
            if self._args.comments:
                RunComments.run(self._args, self._reddit)
            elif self._args.basic:
                RunBasic.run(self._args, self._parser, self._reddit)

        elif self._args.live_subreddit or self._args.live_redditor:
            """
            Run PRAW livestream scrapers.
            """

            Validation.validate_user(self._parser, self._reddit)
            Livestream.stream(self._args, self._reddit)

        elif self._args.frequencies or self._args.wordcloud:
            """
            Run analytical tools.
            """

            if self._args.frequencies:
                GenerateFrequencies.generate(self._args)
            if self._args.wordcloud:
                GenerateWordcloud.generate(self._args)
