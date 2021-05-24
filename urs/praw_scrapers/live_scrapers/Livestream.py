"""
Livestream
==========
Defining methods for livestreaming a Subreddit or Redditor's comments and/or 
submissions.
"""


import time
import json
import os

from colorama import (
    Fore,
    Style
)
from halo import Halo

from urs.praw_scrapers.live_scrapers.utils.DisplayStream import DisplayStream
from urs.praw_scrapers.live_scrapers.utils.StreamGenerator import StreamGenerator

from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Global import date
from urs.utils.Titles import PRAWTitles

class SaveStream():
    """
    Methods for saving the livestream to file.
    """

    @staticmethod
    def _create_skeleton(args):
        """
        Create a JSON skeleton to store livestream data.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 

        Returns
        -------
        skeleton: dict
            Dictionary containing data pertaining to the livestream
        """

        skeleton = {
            "livestream_settings": {},
            "data": []
        }

        if args.live_subreddit:
            skeleton["livestream_settings"]["subreddit"] = args.live_subreddit
        elif args.live_redditor:
            skeleton["livestream_settings"]["redditor"] = args.live_redditor

        skeleton["livestream_settings"]["included_reddit_objects"] = "submissions" \
            if args.stream_submissions \
            else "comments"

        return skeleton

    @staticmethod
    def _make_livestream_dir(split_stream_info):
        """
        Make the `livestream` directory within the `scrapes/[DATE]` directory.

        Calls public methods from an external module:

            InitializeDirectory.create()
            InitializeDirectory.make_type_directory()

        Parameters
        ----------
        split_stream_info: list
            List containing stream information

        Returns
        -------
        stream_directory: str
            String denoting the path to the directory in which the stream is saved
        """

        InitializeDirectory.make_type_directory("livestream")

        if split_stream_info[0] == "r":
            sub_directory = "subreddits"
        elif split_stream_info[0] == "u":
            sub_directory = "redditors"

        stream_directory = "../scrapes/%s/livestream/%s" % (date, sub_directory)
        InitializeDirectory.create(stream_directory)

        return stream_directory

    @staticmethod
    def _get_temp_filename(stream_info):
        """
        Create a temporary filename to write stream data in real time.

        Calls previously defined private method:

            SaveStream._make_livestream_dir()

        Parameters
        ----------
        stream_info: str
            String denoting the stream information (Subreddit and Subreddit name
            or Redditor and Redditor name)

        Returns
        -------
        stream_path: str
            String denoting the filepath
        """

        split_stream_info = stream_info.split(" ")[1].split("/")
        filename = split_stream_info[1] + ".json"

        stream_directory = SaveStream._make_livestream_dir(split_stream_info)

        return stream_directory + "/" + filename

    @staticmethod
    def _rename_with_duration(duration, object_info, stream_path):
        """
        Rename the livestream file by including the duration.

        Parameters
        ----------
        duration: str
            String denoting the total time spent livestreaming
        object_info: str
            String denoting what kind of Reddit objects were streamed
        stream_path: str
            String denoting the path to the saved livestream

        Returns
        -------
        None
        """

        split_stream_path = stream_path.split(".")
        new_filename = "..{parent_path}-{object_info}-{duration}.{file_type}".format(
            parent_path = split_stream_path[-2],
            object_info = object_info,
            duration = duration.replace(":", "_"),
            file_type = split_stream_path[-1]
        )
        
        os.rename(stream_path, new_filename)

    @staticmethod
    def write(args, generator, object_info, stream_info):
        """
        Save the livestream to file.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        generator: Reddit object generator
        object_info: str
            String denoting which Reddit objects are displayed in the stream

        Returns
        -------
        skeleton: dict
            Dictionary containing all scrape data
        """
        
        skeleton = SaveStream._create_skeleton(args)

        stream_path = SaveStream._get_temp_filename(stream_info)

        if not os.path.isfile(stream_path):
            with open(stream_path, "w", encoding = "utf-8") as new_file:
                json.dump(skeleton, new_file)

        with open(stream_path, "r+", encoding = "utf-8") as existing_file:
            stream_data = json.load(existing_file)

            start_stream = time.time()
            try:
                for obj in generator:
                    DisplayStream.display(obj)
                    stream_data["data"].append(obj)

                    existing_file.seek(0)
                    existing_file.truncate()
                    json.dump(stream_data, existing_file)

            except KeyboardInterrupt:
                duration = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_stream))

                print("\n\n")
                Halo().info(Fore.YELLOW + Style.BRIGHT + "ABORTING LIVESTREAM.")
                Halo().info("Streamed %s submitted %s for %s." % (object_info, stream_info, duration))
                print()

                stream_data["livestream_settings"]["stream_duration"] = duration
                existing_file.seek(0)
                existing_file.truncate()
                json.dump(stream_data, existing_file, indent = 4)

        save_spinner = Halo().start("Saving livestream.")
        SaveStream._rename_with_duration(duration, object_info, stream_path)
        save_spinner.info(Fore.GREEN + Style.BRIGHT + "Livestream has been saved to file.")

        print()

class Livestream():
    """
    Methods for livestreaming a Subreddit or Redditor's new submissions and/or 
    comments.
    """

    @staticmethod
    def _stream_switch(args, reddit_object):
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
        generator: Reddit object generator
        object_info: str
            String denoting which Reddit objects are displayed in the stream
        """

        if args.stream_submissions:
            Halo().info(Fore.WHITE + Style.BRIGHT + "Displaying submissions.")
            object_info = "submissions"
            generator = StreamGenerator.stream_submissions(reddit_object.stream)
        else:
            Halo().info(Fore.WHITE + Style.BRIGHT + "Displaying comments.")
            object_info = "comments"
            generator = StreamGenerator.stream_comments(reddit_object.stream)

        print()

        return generator, object_info

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
            
            stream_info = "in r/%s" % args.live_subreddit
            reddit_object = reddit.subreddit(args.live_subreddit)

        elif args.live_redditor:
            PRAWTitles.lu_title()

            Validation.validate([args.live_redditor], reddit, "redditor")

            Halo().info(Fore.CYAN + Style.BRIGHT + "Initializing Redditor livestream for u/%s." % args.live_redditor)
            
            stream_info = "by u/%s" % args.live_redditor
            reddit_object = reddit.subreddit(args.live_redditor)
        
        Halo().info("New entries will appear when posted to Reddit.")

        generator, object_info = Livestream._stream_switch(args, reddit_object)

        if args.nosave:
            start_stream = time.time()

            try:
                for obj in generator:
                    DisplayStream.display(obj)
            except KeyboardInterrupt:
                duration = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_stream))

                print("\n\n")
                Halo().info(Fore.YELLOW + Style.BRIGHT + "ABORTING LIVESTREAM.")
                Halo().info("Streamed %s submitted %s for %s." % (object_info, stream_info, duration))
                print()
        else:
            SaveStream.write(args, generator, object_info, stream_info)
