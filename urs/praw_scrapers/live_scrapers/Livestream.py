"""
Livestream
==========
Defining methods for livestreaming a Subreddit or Redditor's comments and/or 
submissions.
"""


from colorama import (
    Fore,
    Style
)
from halo import Halo

from urs.praw_scrapers.live_scrapers.utils.DisplayStream import DisplayStream
from urs.praw_scrapers.live_scrapers.utils.StreamGenerator import StreamGenerator

from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Global import date
from urs.utils.Titles import PRAWTitles

class Livestream():
    """
    Methods for livestreaming a Subreddit or Redditor's new submissions and/or 
    comments.
    """

    @staticmethod
    def stream_switch(args, reddit_object):
        """
        A switch that determines what Reddit objects are yielded (comments,
        submissions, or both).

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        reddit_object: Reddit Subreddit or Redditor object

        Returns
        -------
        None
        """

        if args.only_submissions or args.only_comments:
            if args.only_submissions:
                Halo().info(Fore.WHITE + Style.BRIGHT + "Only displaying submissions.")
                object_type = "submissions"
            elif args.only_comments:
                Halo().info(Fore.WHITE + Style.BRIGHT + "Only displaying comments.")
                object_type = "comments"

            print()

            for obj in StreamGenerator.single_stream(object_type, reddit_object.stream):
                DisplayStream.display(obj, object_type)
        else:
            Halo().info(Fore.WHITE + Style.BRIGHT + "Displaying comments and submissions.")
            print()

            StreamGenerator.dual_stream(reddit_object.stream)

    @staticmethod
    def stream(args, reddit):
        """
        Livestream comments and/or submissions to terminal, then write stream to 
        log if applicable.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        None
        """

        if args.live_subreddit:
            PRAWTitles.lr_title()

            Validation.validate([args.live_subreddit], reddit, "subreddit")

            Halo().info(Fore.CYAN + Style.BRIGHT + "Initializing Subreddit livestream for r/%s." % args.live_subreddit)
            reddit_object = reddit.subreddit(args.live_subreddit)
        elif args.live_redditor:
            PRAWTitles.lu_title()

            Validation.validate([args.live_redditor], reddit, "redditor")

            Halo().info(Fore.CYAN + Style.BRIGHT + "Initializing Redditor livestream for u/%s." % args.live_redditor)
            reddit_object = reddit.subreddit(args.live_redditor)
        
        Halo().info("New entries will appear when posted to Reddit.")

        try:
            Livestream.stream_switch(args, reddit_object)
        except KeyboardInterrupt:
            print(Fore.YELLOW + Style.BRIGHT + "\n\nUSER HAS ENDED LIVESTREAM.\n")

            if not args.nosave:
                Halo().info("Saving livestream to file.")
