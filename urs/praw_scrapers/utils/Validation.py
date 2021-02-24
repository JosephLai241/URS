"""
PRAW validation
===============
Validation methods for PRAW credentials and scrapers.
"""


import praw
import requests

from colorama import (
    init, 
    Fore, 
    Style
)
from praw import models
from prawcore import (
    NotFound, 
    PrawcoreException
)
from prettytable import PrettyTable

from urs.utils.Logger import LogError

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class Validation():
    """
    Methods for validating PRAW credentials and Subreddits, Redditors, and URLs.
    """

    @staticmethod
    @LogError.log_rate_limit
    def get_rate_info(reddit):
        """
        Get user rate limit information. Quits the program if the user does not
        have any requests left in the current rate limit window.

        Parameters
        ----------
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        praw_limits: praw.models
            PRAW rate limits
        """

        return models.Auth(_data = dict(), reddit = reddit).limits

    @staticmethod
    def print_rate_limit(reddit):
        """
        Print user rate limit information. This includes the number of requests
        remaining, a timestamp for when the rate limit counters will be reset, and
        the number of requests that have been made in the current rate limit window.

        Parameters
        ----------
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        None
        """

        user_limits = Validation.get_rate_info(reddit)

        pretty_limits = PrettyTable()
        pretty_limits.field_names = [
            "Remaining Requests", 
            "Used Requests"]
        pretty_limits.add_row([
            int(user_limits["remaining"]), 
            int(user_limits["used"])])
        
        pretty_limits.align = "c"
        
        print(pretty_limits)

    @staticmethod
    @LogError.log_login
    def validate_user(parser, reddit):
        """
        Check if PRAW credentials are valid, then print rate limit PrettyTable.

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser object
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        None
        """

        print(Style.BRIGHT + Fore.GREEN + 
            "\nSuccessfully logged in as u/%s.\n" % reddit.user.me())
        
        Validation.print_rate_limit(reddit)

    @staticmethod
    def _check_subreddits(found, not_found, object_list, reddit):
        """
        Check if Subreddits are valid.

        Parameters
        ----------
        found: list
            Empty list to store valid Subreddits
        not_found: list
            Empty list to store invalid Subreddits
        object_list: list
            List of Subreddits to check
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Exceptions
        ----------
        NotFound:
            Raised if invalid Subreddits were provided

        Returns
        -------
        None
        """

        for sub in object_list:
            try:
                reddit.subreddits.search_by_name(sub, exact = True)
                found.append(sub)
            except NotFound:
                not_found.append(sub)

    @staticmethod
    def _check_redditors(found, not_found, object_list, reddit):
        """
        Check if Redditors are valid.

        Parameters
        ----------
        found: list
            Empty list to store valid Redditors
        not_found: list
            Empty list to store invalid Redditors
        object_list: list
            List of Redditors to check
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Exceptions
        ----------
        NotFound:
            Raised if invalid Redditors were provided

        Returns
        -------
        None
        """

        for user in object_list:
            try:
                reddit.redditor(user).id
                found.append(user)
            except NotFound:
                not_found.append(user)

    @staticmethod
    def _check_submissions(found, not_found, object_list, reddit):
        """
        Check if submission URLs are valid.

        Parameters
        ----------
        found: list
            Empty list to store valid submission URLs
        not_found: list
            Empty list to store invalid submission URLs
        object_list: list
            List of submission URLs to check
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Exceptions
        ----------
        NotFound:
            Raised if invalid submission URLs were provided

        Returns
        -------
        None
        """

        for post in object_list:
            try:
                reddit.submission(url = post).title
                found.append(post)
            except Exception:
                not_found.append(post)

    @staticmethod
    def existence(l_type, object_list, parser, reddit, s_t):
        """
        Check if Subreddit(s), Redditor(s), or submission(s) exist and catch PRAW 
        exceptions.

        Parameters
        ----------
        l_type: str
            String denoting the scraper type
        object_list: list
            List of Reddit objects to check
        parser: ArgumentParser
            argparse ArgumentParser object
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        s_t: list
            List of scraper types

        Exceptions
        ----------
        NotFound:
            Raised if invalid Subreddits or Redditors were provided
        Exception:
            Raised if invalid submission URLs were provided

        Returns
        -------
        found: list
            List of valid Reddit objects
        not_found: list
            List of invalid Reddit objects
        """

        found = []
        not_found = []

        ### Check Subreddits.
        if l_type == s_t[0]:
            Validation._check_subreddits(found, not_found, object_list, reddit)
        ### Check Redditors.
        elif l_type == s_t[1]:
            Validation._check_redditors(found, not_found, object_list, reddit)
        ### Check submission URLs.
        elif l_type == s_t[2]:
            Validation._check_submissions(found, not_found, object_list, reddit)

        return found, not_found
