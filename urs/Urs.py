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


import os
import praw

from dotenv import load_dotenv

from urs.utils.Logger import LogMain
from urs.utils.Tools import Run

class Main():
    """
    Run URS.
    """

    @staticmethod
    @LogMain.master_timer
    def main():
        load_dotenv()

        reddit = praw.Reddit(
            client_id = os.getenv("CLIENT_ID"),
            client_secret = os.getenv("CLIENT_SECRET"),
            user_agent = os.getenv("USER_AGENT"),
            username = os.getenv("USERNAME"),
            password = os.getenv("PASSWORD")
        )

        Run(reddit).run_urs()

if __name__ == "__main__":
    Main.main()
