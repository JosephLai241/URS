#!/usr/bin/python


"""
URS
===

URS, an acronym for "Universal Reddit Scraper", is a comprehensive Reddit scraping 
command-line tool written in Python.

* Scrape Reddit via PRAW (the official Python Reddit API Wrapper)
    + Scrape Subreddits
    + Scrape Redditors
    + Scrape submission comments
* Livestream Reddit via PRAW
    + Livestream comments submitted within Subreddits or by Redditors
    + Livestream submissions submitted within Subreddits or by Redditors
* Analytical tools for scraped data
    + Generate frequencies for words that are found in submission titles, bodies, and/or comments
    + Generate a wordcloud from scrape results

@author: Joseph Lai
@contact: urs_project@protonmail.com
@github: https://github.com/JosephLai241/URS
"""


import os

import praw
from colorama import init
from dotenv import load_dotenv

from urs.utils.Logger import LogMain
from urs.utils.Tools import Run

# Automate sending reset sequences to turn off color changes at the end of
# every print.
init(autoreset=True)


class Main:
    """
    Run URS.
    """

    @staticmethod
    @LogMain.master_timer
    def main() -> None:
        load_dotenv()

        reddit = praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
        )

        Run(reddit).run_urs()


if __name__ == "__main__":
    Main.main()
