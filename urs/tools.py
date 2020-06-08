#===============================================================================
#                           All Scrapers
#===============================================================================
from colorama import Fore, init, Style
from utils import (Basic, cli, comments_functions, global_vars,
                   redditor_functions, Subreddit, titles)

### Automate sending reset sequences to turn off color changes at the end of 
### every print
init(autoreset = True)

### All scraper functionality is contained within this class
class Run():
    def __init__(self, args, parser, reddit):
        self.args = args
        self.parser = parser
        self.reddit = reddit

        self.options = global_vars.options
        self.s_t = global_vars.s_t

    ### Run Subreddit scraper
    def subreddit(self):
        Subreddit.RunSubreddit().run(self.args, self.parser, self.reddit, self.s_t)

    ### Run Redditor scraper
    def redditor(self):
        titles.u_title()

        user_list = cli.create_list(self.args, self.s_t, self.s_t[1])
        users = redditor_functions.list_users(self.reddit, user_list, self.parser)
        u_master = redditor_functions.c_u_dict(users)
        cli.get_cli_settings(self.reddit, self.args, u_master, self.s_t, self.s_t[1])

        redditor_functions.w_user(self.reddit, users, u_master, self.args)

    ### Run comments scraper
    def comments(self):
        titles.c_title()

        post_list = cli.create_list(self.args, self.s_t, self.s_t[2])
        posts = comments_functions.list_posts(self.reddit, post_list, self.parser)
        c_master = comments_functions.c_c_dict(posts)
        cli.get_cli_settings(self.reddit, self.args, c_master, self.s_t, self.s_t[2])

        comments_functions.w_comments(self.reddit, post_list, c_master, self.args)

    ### Run basic Subreddit scraper
    def basic(self):
        Basic.RunBasic().run(self.args, self.parser, self.reddit)
