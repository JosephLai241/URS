#===============================================================================
#                   All Scrapers and Validation/Args Checking
#===============================================================================
from colorama import Fore, init, Style
from utils import (Basic, Cli, Comments, Global,
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
        self.reddit = reddit
        self.args, self.parser = self.login_and_args()

        self.options = Global.options
        self.s_t = Global.s_t

    ### Print title, then run checks for CLI args and PRAW credentials.
    def login_and_args(self):
        Titles.Titles().title()

        args, parser = Cli.Parser().parse_args()
        Validation.Validation().validate_user(parser, self.reddit)
        Cli.CheckCli().check_args(args, parser)

        return args, parser

    ### Switch for running scrapers.
    def run_urs(self):
        if self.args.subreddit:
            ### Run Subreddit scraper.
            Subreddit.RunSubreddit().run(self.args, self.parser, self.reddit, self.s_t)
        if self.args.redditor:
            ### Run Redditor scraper.
            Redditor.RunRedditor().run(self.args, self.parser, self.reddit)
        if self.args.comments:
            ### Run comments scraper.
            Comments.RunComments().run(self.args, self.parser, self.reddit)
        elif self.args.basic:
            ### Run basic Subreddit scraper.
            Basic.RunBasic().run(self.args, self.parser, self.reddit)
        