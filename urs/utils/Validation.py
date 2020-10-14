#===============================================================================
#                                 Validation
#===============================================================================
import praw
import requests

from colorama import (
    init, 
    Fore, 
    Style)
from praw import models
from prawcore import (
    NotFound, 
    PrawcoreException)
from prettytable import PrettyTable

from . import (
    Global, 
    Titles)
from .Logger import LogError

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class Validation():
    """
    Methods for validating PRAW credentials and Subreddits, Redditors, and URLs.
    """

    ### Get user rate limit information. Quits the program if the user does not
    ### have any requests left in the current rate limit window.
    @staticmethod
    @LogError.log_rate_limit
    def get_rate_info(reddit):
        return models.Auth(_data = dict(), reddit = reddit).limits

    ### Print user rate limit information. This includes the number of requests
    ### remaining, a timestamp for when the rate limit counters will be reset, and
    ### the number of requests that have been made in the current rate limit window.
    @staticmethod
    def print_rate_limit(reddit):
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

    ### Check if PRAW credentials are valid, then print rate limit PrettyTable.
    @staticmethod
    @LogError.log_login
    def validate_user(parser, reddit):
        print(Style.BRIGHT + Fore.GREEN + 
            "\nYou have successfully logged in as u/%s.\n" % reddit.user.me())
        
        Validation.print_rate_limit(reddit)

    ### Check Subreddits.
    @staticmethod
    def _check_subreddits(found, not_found, object_list, reddit):
        for sub in object_list:
            try:
                reddit.subreddits.search_by_name(sub, exact = True)
                found.append(sub)
            except NotFound:
                not_found.append(sub)

    ### Check Redditors.
    @staticmethod
    def _check_redditors(found, not_found, object_list, reddit):
        for user in object_list:
            try:
                reddit.redditor(user).id
                found.append(user)
            except NotFound:
                not_found.append(user)

    ### Check submissions.
    @staticmethod
    def _check_submissions(found, not_found, object_list, reddit):
        for post in object_list:
            try:
                reddit.submission(url = post).title
                found.append(post)
            except Exception as e:
                not_found.append(e)

    ### Check if Subreddit(s), Redditor(s), or submission(s) exist and catch PRAW 
    ### exceptions.
    @staticmethod
    def existence(l_type, object_list, parser, reddit, s_t):
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
