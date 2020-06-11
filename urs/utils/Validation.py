#===============================================================================
#                                 Validation
#===============================================================================
import praw
import requests

from colorama import Fore, init, Style
from prawcore import NotFound, PrawcoreException

### Automate sending reset sequences to turn off color changes at the end of 
### every print
init(autoreset = True)

class Validation():
    """
    Functions for validating PRAW credentials and Subreddits, Redditors, and URLs.
    """

    ### Check if PRAW credentials are valid.
    @staticmethod
    def validate_user(parser, reddit):
        print("\nLogging in...")
        
        try:
            print(Style.BRIGHT + Fore.GREEN + "\nYou have successfully logged in as u/%s.\n" % 
                    reddit.user.me())
        except PrawcoreException as error:
            print(Style.BRIGHT + Fore.RED + "\nERROR!")
            print(Style.Bright + Fore.RED + "\n%s" % error)
            print(Style.BRIGHT + Fore.RED + 
                "\nPlease recheck Reddit credentials or your internet connection.")
            print(Style.BRIGHT + Fore.RED + "\nExiting.\n")
            parser.exit()

    ### Check Subreddits.
    @staticmethod
    def _check_subs(found, not_found, object_list, reddit):
        for sub in object_list:
            try:
                reddit.subreddits.search_by_name(sub, exact = True)
                found.append(sub)
            except NotFound:
                not_found.append(sub)

    ### Check Redditors.
    @staticmethod
    def _check_users(found, not_found, object_list, reddit):
        for user in object_list:
            try:
                reddit.redditor(user).id
                found.append(user)
            except NotFound:
                not_found.append(user)

    ### Check posts.
    @staticmethod
    def _check_posts(found, not_found, object_list, reddit):
        for post in object_list:
            try:
                reddit.submission(url = post).title
                found.append(post)
            except Exception as e:
                not_found.append(e)

    ### Check if Subreddit(s), Redditor(s), or post exists and catch PRAW exceptions.
    @staticmethod
    def existence(l_type, object_list, parser, reddit, s_t):
        found = []
        not_found = []

        ### Check Subreddits.
        if l_type == s_t[0]:
            Validation._check_subs(found, not_found, object_list, reddit)
        ### Check Redditors.
        elif l_type == s_t[1]:
            Validation._check_users(found, not_found, object_list, reddit)
        ### Check post URLs.
        elif l_type == s_t[2]:
            Validation._check_posts(found, not_found, object_list, reddit)

        return found, not_found
