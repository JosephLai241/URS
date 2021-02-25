#!/usr/bin/python

"""
URS
===

URS, an acronym for "Universal Reddit Scraper", is a comprehensive Reddit scraping 
command-line tool written in Python.

* Scrape Reddit via PRAW (the official Python Reddit API Wrapper)
    * Scrape Subreddits
    * Scrape Redditors
    * Scrape submission comments
* Analytical tools for scraped data
    * Generate word frequencies for words that are found in submission titles,
        bodies, and/or comments
    * Generate a wordcloud from scrape results

@author: Joseph Lai
@contact: urs_project@protonmail.com
@github: https://github.com/JosephLai241/URS
"""


import praw

from urs.Credentials import API

from urs.utils.Logger import LogMain
from urs.utils.Tools import Run

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
