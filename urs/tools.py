#===============================================================================
#                           All Scrapers
#===============================================================================
from utils import (basic_functions, cli, comments_functions, global_vars,
                   redditor_functions, subreddit_functions, titles)

### All scraper functionality is contained within this class
class Run():
    def __init__(self, args, parser, reddit):
        self.args = args
        self.parser = parser
        self.reddit = reddit

        self.options = global_vars.options
        self.s_t = global_vars.s_t

        # self.comments_functions = comments_functions
        # self.redditor_functions = redditor_functions
        # self.subreddit_functions = subreddit_functions

    ### Run Subreddit scraper
    def subreddit(self):
        titles.r_title()

        sub_list = cli.create_list(self.args, self.s_t, self.s_t[0])
        subs = cli.confirm_subs(self.reddit, sub_list, self.parser)
        s_master = subreddit_functions.c_s_dict(subs)
        cli.get_cli_settings(self.reddit, self.args, s_master, self.s_t, self.s_t[0])

        if self.args.y:
            subreddit_functions.gsw_sub(self.reddit, self.args, s_master)
        else:
            confirm = subreddit_functions.print_settings(s_master, self.args)
            if confirm == self.options[0]:
                subreddit_functions.gsw_sub(self.reddit, self.args, s_master)
            else:
                print("\nCancelling.")

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
        titles.b_title()
        
        while True:
            while True:
                subs = basic_functions.get_subreddits(self.reddit, self.parser)
                s_master = subreddit_functions.c_s_dict(subs)
                basic_functions.get_settings(subs, s_master)

                confirm = subreddit_functions.print_settings(s_master, self.args)
                if confirm == self.options[0]:
                    break
                else:
                    print("\nExiting.")
                    self.parser.exit()
            subreddit_functions.gsw_sub(self.reddit, self.args, s_master)
            
            repeat = basic_functions.another()
            if repeat == self.options[1]:
                print("\nExiting.")
                break
