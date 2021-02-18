#!/usr/bin/python
"""
Created on Wed Feb 10 16:20:04 2021

Universal Reddit Scraper v3.2.0

@author: Joseph Lai
@contact: urs_project@protonmail.com
"""
import praw

from Credentials import API

from utils.Logger import LogMain
from utils.Tools import Run

class Main():
    """
    Run URS.
    """

    @staticmethod
    @LogMain.master_timer
    def main():
        ### Creating a Reddit object with PRAW credentials.
        reddit = praw.Reddit(
            client_id = API["client_id"],
            client_secret = API["client_secret"],
            user_agent = API["user_agent"],
            username = API["username"],
            password = API["password"]
        )

        Run(reddit).run_urs()

if __name__ == "__main__":
    Main.main()
