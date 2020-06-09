#===============================================================================
#                           All Scrapers
#===============================================================================
from colorama import Fore, init, Style
from utils import (Basic, Cli, comments_functions, Global,
                   Redditor, Subreddit, Titles)

### Automate sending reset sequences to turn off color changes at the end of 
### every print
init(autoreset = True)

### All scraper functionality is contained within this class
class Run():
    def __init__(self, args, parser, reddit):
        self.args = args
        self.parser = parser
        self.reddit = reddit

        self.options = Global.options
        self.s_t = Global.s_t

    ### Run checks for CLI args and PRAW credentials.
    def check(self):
        parser, args = parse_args()
        Validation().validate_user(parser, reddit)
        check_args(parser, args)

    ### Run Subreddit scraper
    def subreddit(self):
        Subreddit.RunSubreddit().run(self.args, self.parser, self.reddit, self.s_t)

    ### Run Redditor scraper
    def redditor(self):
        Redditor.RunRedditor().run(self.args, self.parser, self.reddit)

    ### Run comments scraper
    def comments(self):
        Titles.Titles().c_title()

        post_list = Cli.GetScrapeSettings().create_list(self.args, self.s_t[2])
        posts = comments_functions.list_posts(self.reddit, post_list, self.parser)
        c_master = comments_functions.c_c_dict(posts)
        Cli.get_cli_settings(self.reddit, self.args, c_master, self.s_t, self.s_t[2])

        comments_functions.w_comments(self.reddit, post_list, c_master, self.args)

    ### Run basic Subreddit scraper
    def basic(self):
        Basic.RunBasic().run(self.args, self.parser, self.reddit)
