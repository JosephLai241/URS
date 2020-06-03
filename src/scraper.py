#!/usr/bin/python
"""
Created on Tue Jun 2 20:14:43 2020

Universal Reddit Scraper 3.0 - Reddit scraper using the Reddit API (PRAW)

@author: Joseph Lai
"""
from colorama import Style, init
import praw

### Import argparse and scrapers
from . import cli, titles
from .tools import Run

init(autoreset = True)

### Reddit API Credentials
c_id = "14_CHAR_HERE"               # Personal Use Script (14 char)
c_secret = "27_CHAR_HERE"           # Secret key (27 char)
u_a = "APP_NAME_HERE"               # App name
usrnm = "REDDIT_USERNAME_HERE"      # Reddit username
passwd = "REDDIT_PASSWORD_HERE"     # Reddit login password

### Putting it all together
def main():
    ### Reddit Login
    reddit = praw.Reddit(client_id = c_id,
                         client_secret = c_secret,
                         user_agent = u_a,
                         username = usrnm,
                         password = passwd)

    ### Parse and check args, and initialize Subreddit, Redditor, post comments,
    ### or basic Subreddit scraper
    parser, args = cli.parse_args()
    cli.check_args(parser, args)
    titles.title()

    run = Run(args, parser, reddit)
    
    if args.sub:
        ### Subreddit scraper
        run.subreddit()
    if args.user:
        ### Redditor scraper
        run.redditor()
    if args.comments:
        ### Post comments scraper
        run.comments()
    elif args.basic:
        ### Basic Subreddit scraper
        run.basic()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Style.BRIGHT + "\nURS ABORTED.\n")
        quit()
