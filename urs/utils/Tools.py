#===============================================================================
#                   All Scrapers and Validation/Args Checking
#===============================================================================
from colorama import Fore, init, Style
from . import (Basic, Cli, Comments, Global,
                   Redditor, Subreddit, Titles, Validation)

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class Run():
    """
    Functions to call Cli and Subreddit, Redditor, Comments, and Basic scrapers.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self, reddit):
        self._reddit = reddit
        self._args, self._parser = self._login_and_args()

        self._s_t = Global.s_t

    ### Print title, then run checks for CLI args and PRAW credentials.
    def _login_and_args(self):
        Titles.Titles.title()

        args, parser = Cli.Parser().parse_args()
        Validation.Validation.validate_user(parser, self._reddit)
        Cli.CheckCli().check_args(args, parser)

        return args, parser

    ### Switch for running scrapers.
    def run_urs(self):
        if self._args.subreddit:
            ### Run Subreddit scraper.
            Subreddit.RunSubreddit.run(self._args, self._parser, self._reddit, self._s_t)
        if self._args.redditor:
            ### Run Redditor scraper.
            Redditor.RunRedditor.run(self._args, self._parser, self._reddit)
        if self._args.comments:
            ### Run comments scraper.
            Comments.RunComments.run(self._args, self._parser, self._reddit)
        elif self._args.basic:
            ### Run basic Subreddit scraper.
            Basic.RunBasic.run(self._args, self._parser, self._reddit)
        