#!/usr/bin/python
"""
Created on Tue Jun 2 20:14:43 2020

Universal Reddit Scraper 3.1

@author: Joseph Lai
"""
import praw

from Credentials import API
from Tools import Run

from utils.Logger import LogMain

class Main():
    """
    Putting it all together.
    """

    @staticmethod
    @LogMain.master_timer
    def main():
        ### Reddit Login
        reddit = praw.Reddit(
            client_id = API["client_id"],
            client_secret = API["client_secret"],
            user_agent = API["user_agent"],
            username = API["username"],
            password = API["password"])

        run = Run(reddit)
        run.run_urs()

if __name__ == "__main__":
    Main().main()
