"""
PRAW validation
===============
Validation methods for PRAW credentials and scrapers.
"""


import logging
import praw
import requests

from colorama import (
    Fore, 
    Style
)
from halo import Halo
from praw import models
from prawcore import (
    NotFound, 
    PrawcoreException
)
from prettytable import PrettyTable

from urs.utils.Global import Status
from urs.utils.Logger import LogError
from urs.utils.Titles import Errors

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

        login_spinner = Halo(color = "white", text = "Logging in.")
        login_spinner.start()

        try:
            redditor = reddit.user.me()

            login_spinner.succeed(Style.BRIGHT + Fore.GREEN + f"Successfully logged in as u/{redditor}.")
            print()

            Validation.print_rate_limit(reddit)

            logging.info(f"Successfully logged in as u/{redditor}.")
            logging.info("")
        except PrawcoreException as error:
            login_spinner.fail(Style.BRIGHT + Fore.RED + "Failed to log in.")

            Errors.p_title(error)
            logging.critical("LOGIN FAILED.")
            logging.critical(f"PRAWCORE EXCEPTION: {error}.")
            logging.critical("ABORTING URS.\n")
            parser.exit()

    @staticmethod
    def _check_subreddits(invalid, object_list, reddit, valid):
        """
        Check if Subreddits are valid.

        Parameters
        ----------
        invalid: list
            Empty list to store invalid Subreddits
        object_list: list
            List of Subreddits to check
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        valid: list
            Empty list to store valid Subreddits

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
                valid.append(sub)
            except NotFound:
                invalid.append(sub)

    @staticmethod
    def _check_redditors(invalid, object_list, reddit, valid):
        """
        Check if Redditors are valid.

        Parameters
        ----------
        invalid: list
            Empty list to store invalid Redditors
        object_list: list
            List of Redditors to check
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        valid: list
            Empty list to store valid Redditors

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
                valid.append(user)
            except NotFound:
                invalid.append(user)

    @staticmethod
    def _check_submissions(invalid, object_list, reddit, valid):
        """
        Check if submission URLs are valid.

        Parameters
        ----------
        invalid: list
            Empty list to store invalid submission URLs
        object_list: list
            List of submission URLs to check
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        valid: list
            Empty list to store valid submission URLs

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
                valid.append(post)
            except Exception:
                invalid.append(post)

    @staticmethod
    def check_existence(object_list, reddit, scraper_type):
        """
        Check whether Reddit objects are valid.

        Parameters
        ----------
        object_list: list
            List of Reddit objects to check
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        scraper_type: str
            String denoting the scraper type

        Exceptions
        ----------
        NotFound:
            Raised if invalid Subreddits or Redditors were provided
        Exception:
            Raised if invalid submission URLs were provided

        Returns
        -------
        valid: list
            List of valid Reddit objects
        invalid: list
            List of invalid Reddit objects
        """

        invalid = []
        valid = []

        if scraper_type == "subreddit":
            Validation._check_subreddits(invalid, object_list, reddit, valid)
        elif scraper_type == "redditor":
            Validation._check_redditors(invalid, object_list, reddit, valid)
        elif scraper_type == "comments":
            Validation._check_submissions(invalid, object_list, reddit, valid)

        return invalid, valid

    @staticmethod
    def validate(object_list, reddit, scraper_type):
        """
        Check if Subreddit(s), Redditor(s), or submission(s) exist and catch PRAW 
        exceptions. Log invalid Reddit objects to `urs.log` if applicable.

        Calls previously defined public method:

            Validation.check_existence()

        Parameters
        ----------
        object_list: list
            List of Reddit objects to check
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        scraper_type: str
            String denoting the scraper type

        Returns
        -------
        invalid: list
            List of invalid Reddit objects
        valid: list
            List of valid Reddit objects
        """

        object_type = "submission" \
            if scraper_type == "comments" \
            else scraper_type.capitalize()

        check_status = Status(
            f"Finished {object_type} validation.",
            f"Validating {object_type}(s)",
            "white"
        )

        check_status.start()

        logging.info(f"Validating {object_type}(s)...")
        logging.info("")

        invalid, valid = Validation.check_existence(object_list, reddit, scraper_type)
        
        check_status.succeed()
        print()

        if invalid:
            warning_message = f"The following {object_type}s were not found and will be skipped:"

            print(Fore.YELLOW + Style.BRIGHT + warning_message)
            print(Fore.YELLOW + Style.BRIGHT + "-" * len(warning_message))
            print(*invalid, sep = "\n")

            logging.warning(f"Failed to validate the following {object_type}s:")
            logging.warning(f"{invalid}")
            logging.warning("Skipping.")
            logging.info("")

        if not valid:
            logging.critical(f"ALL {object_type.upper()}S FAILED VALIDATION.")
            Errors.n_title(object_type + "s")
            logging.critical(f"NO {object_type.upper()}S LEFT TO SCRAPE.")
            logging.critical("ABORTING URS.\n")
            
            quit()

        return invalid, valid
