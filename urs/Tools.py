#===============================================================================
#                           All Scrapers
#===============================================================================
from colorama import Fore, init, Style
from utils import (Basic, Cli, comments_functions, Global,
                   Redditor, Subreddit, Titles, Validation)

### Automate sending reset sequences to turn off color changes at the end of 
### every print
init(autoreset = True)

### All scraper functionality is contained within this class
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

    ### Switch for running scrapers
    def run_urs(self):
        if self.args.subreddit:
            ### Subreddit scraper
            Subreddit.RunSubreddit().run(self.args, self.parser, self.reddit, self.s_t)
        if self.args.redditor:
            ### Redditor scraper
            Redditor.RunRedditor().run(self.args, self.parser, self.reddit)
        if self.args.comments:
            ### Post comments scraper
            Titles.Titles().c_title()

            post_list = Cli.GetScrapeSettings().create_list(self.args, self.s_t[2])
            posts = comments_functions.list_posts(self.reddit, post_list, self.parser)
            c_master = comments_functions.c_c_dict(posts)
            Cli.get_cli_settings(self.reddit, self.args, c_master, self.s_t, self.s_t[2])

            comments_functions.w_comments(self.reddit, post_list, c_master, self.args)
        elif self.args.basic:
            ### Basic Subreddit scraper
            Basic.RunBasic().run(self.args, self.parser, self.reddit)
        