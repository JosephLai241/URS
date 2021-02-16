"""
Tools
=====
Running all tools that URS has to offer.
"""


from analytics.Frequencies import GenerateFrequencies
from analytics.Wordcloud import GenerateWordcloud

from praw_scrapers.Basic import RunBasic
from praw_scrapers.Comments import RunComments
from praw_scrapers.Redditor import RunRedditor
from praw_scrapers.Subreddit import RunSubreddit

from utils.Cli import (
    CheckCli,
    Parser
)
from utils.Global import s_t
from utils.Titles import MainTitle
from utils.Validation import Validation

class Run():
    """
    Methods to call Cli and Subreddit, Redditor, Comments, and Basic scrapers.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self, reddit):
        self._reddit = reddit
        self._args, self._parser = self._introduce_then_args()
        
    ### Print title, then run checks for CLI args and PRAW credentials.
    def _introduce_then_args(self):
        MainTitle.title()

        args, parser = Parser().parse_args()
        CheckCli().check_args(args, parser)

        return args, parser

    ### Switch for running scrapers.
    def run_urs(self):
        ### Run rate limit check.
        if self._args.check:
            Validation.validate_user(self._parser, self._reddit)

        ### Run PRAW scrapers.
        elif self._args.subreddit or self._args.redditor or self._args.comments or self._args.basic:
            ### Validate PRAW credentials, get user rate limit information, and
            ### finally check for valid Subreddits, Redditors, or submission URLs.
            Validation.validate_user(self._parser, self._reddit)

            ### Run Subreddit scraper.
            if self._args.subreddit:
                RunSubreddit.run(self._args, self._parser, self._reddit, s_t)
            ### Run Redditor scraper.
            if self._args.redditor:
                RunRedditor.run(self._args, self._parser, self._reddit)
            ### Run submission comments scraper.
            if self._args.comments:
                RunComments.run(self._args, self._parser, self._reddit)
            ### Run basic Subreddit scraper.
            elif self._args.basic:
                RunBasic.run(self._args, self._parser, self._reddit)
        
        ### Run analytical tools.
        elif self._args.frequencies or self._args.wordcloud:
            ### Run frequencies generator.
            if self._args.frequencies:
                GenerateFrequencies().generate(self._args)
            ### Run wordcloud generator.
            if self._args.wordcloud:
                GenerateWordcloud().generate(self._args)
        