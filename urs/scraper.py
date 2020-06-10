#!/usr/bin/python
"""
Created on Tue Jun 2 20:14:43 2020

Universal Reddit Scraper 3.0 - Reddit scraper using the Reddit API (PRAW)

@author: Joseph Lai
"""
from colorama import Fore, init, Style
import praw

from utils.Logger import LogMain
from Tools import Run

### Automate sending reset sequences to turn off color changes at the end of 
### every print
init(autoreset = True)

class Main():
    """
    Putting it all together.
    """

    def __init__(self):
        ### Reddit API Credentials
        self.API = {
            "client_id": "14_CHAR_HERE",        # Personal Use Script (14 char)
            "client_secret": "27_CHAR_HERE",    # Secret key (27 char)
            "user_agent": "APP_NAME_HERE",      # App name
            "username": "REDDIT_USERNAME_HERE", # Reddit username
            "password": "REDDIT_PASSWORD_HERE"  # Reddit login password
        }

    @LogMain.master_timer
    def main(self):
        ### Reddit Login
        reddit = praw.Reddit(client_id = self.API["client_id"],
                            client_secret = self.API["client_secret"],
                            user_agent = self.API["user_agent"],
                            username = self.API["username"],
                            password = self.API["password"])

        run = Run(reddit)
        run.run_urs()

if __name__ == "__main__":
    Main().main()
