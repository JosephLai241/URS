"""
Livestream
==========
Defining methods for livestreaming a Subreddit or Redditor's comments and/or 
submissions.
"""


import json
import logging
import os
import time

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
            "livestream_metadata": {},
            "data": []
        }

        skeleton["livestream_settings"]["included_reddit_objects"] = "submissions" \
            if args.stream_submissions \
            else "comments"

        if args.live_subreddit:
            skeleton["livestream_settings"]["subreddit"] = args.live_subreddit
        elif args.live_redditor:
            skeleton["livestream_settings"]["redditor"] = args.live_redditor

        return skeleton

    @staticmethod
    def _make_livestream_dir(split_stream_info):
        """
        Make the `livestream` directory within the `scrapes/[DATE]` directory.

        Calls public methods from an external module:

            InitializeDirectory.create_dirs()

        Parameters
        ----------
        split_stream_info: list
            List containing stream information

        Returns
        -------
        stream_directory: str
            String denoting the path to the directory in which the stream is saved
        """

        if split_stream_info[0] == "r":
            sub_directory = "subreddits"
        elif split_stream_info[0] == "u":
            sub_directory = "redditors"

        stream_directory = f"../scrapes/{date}/livestream/{sub_directory}"
        InitializeDirectory.create_dirs(stream_directory)

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
        stream_path = stream_directory + "/" + filename

        logging.info(f"Writing stream to temporary file: {stream_path}.")

        return stream_path

    @staticmethod
    def _create_temp_file(skeleton, stream_path):
        """
        Create a temporary file to write stream data in real time.

        Parameters
        ----------
        skeleton: dict
            Dictionary containing data pertaining to the livestream
        stream_path: str
            String denoting the path to the saved livestream

        Returns
        -------
        None
        """

        if not os.path.isfile(stream_path):
            with open(stream_path, "w", encoding = "utf-8") as new_file:
                json.dump(skeleton, new_file)

    @staticmethod
    def _rename(duration, object_info, start_stream, stream_path):
        """
        Rename the livestream file by including the start time and duration.

        Parameters
        ----------
        duration: str
            String denoting the total time spent livestreaming
        object_info: str
            String denoting what kind of Reddit objects were streamed
        start_stream: str
            String denoting the time the stream started
        stream_path: str
            String denoting the path to the saved livestream

        Returns
        -------
        None
        """

        split_stream_path = stream_path.split(".")
        new_filename = f"..{split_stream_path[-2]}-{object_info}-{start_stream.replace(':', '_')}-{duration.replace(':', '_')}.{split_stream_path[-1]}"

        logging.info(f"Renaming livestream file to: {new_filename}.")
        os.rename(stream_path, new_filename)

    @staticmethod
    def write(args, generator, object_info, stream_info):
        """
        Write the livestream to file in real time.

        Calls previously defined private methods:

            SaveStream._create_skeleton()
            SaveStream._get_temp_filename()
            SaveStream._rename()

        Calls a public method from an external module:

            DisplayStream.display()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        generator: Reddit object generator
        object_info: str
            String denoting which Reddit objects are displayed in the stream
        stream_info: str
            String denoting the livestream information

        Returns
        -------
        stream_statistics: str
            String denoting the livestream statistics (Reddit objects, Subreddit
            or Redditor, and duration)
        """
        
        skeleton = SaveStream._create_skeleton(args)
        stream_path = SaveStream._get_temp_filename(stream_info)

        SaveStream._create_temp_file(skeleton, stream_path)

        with open(stream_path, "r+", encoding = "utf-8") as existing_file:
            stream_data = json.load(existing_file)

            start_stream = time.mktime(time.localtime())
            try:
                logging.info("")
                logging.info("STREAMING...")
                logging.info("")

                for obj in generator:
                    DisplayStream.display(obj)
                    stream_data["data"].append(obj)

                    existing_file.seek(0)
                    existing_file.truncate()
                    json.dump(stream_data, existing_file)

            except KeyboardInterrupt:
                end_stream = time.mktime(time.localtime())
                duration = time.strftime("%H:%M:%S", time.gmtime(end_stream - start_stream))
                stream_statistics = f"Streamed {object_info} submitted {stream_info} for {duration}."

                print("\n\n")
                Halo().info(Fore.YELLOW + Style.BRIGHT + "ABORTING LIVESTREAM.")
                logging.info("ABORTING LIVESTREAM.")
                logging.info("")

                Halo().info(stream_statistics)
                print()

                stream_data["livestream_metadata"]["stream_duration"] = duration
                stream_data["livestream_metadata"]["stream_end"] = time.strftime("%H:%M:%S", time.localtime(end_stream))
                stream_data["livestream_metadata"]["stream_start"] = time.strftime("%H:%M:%S", time.localtime(start_stream))

                existing_file.seek(0)
                existing_file.truncate()
                json.dump(stream_data, existing_file, indent = 4)

        save_spinner = Halo().start("Saving livestream.")
        SaveStream._rename(duration, object_info, time.strftime("%H:%M:%S", time.localtime(start_stream)), stream_path)
        save_spinner.info(Fore.GREEN + Style.BRIGHT + "Livestream has been saved to file.")

        logging.info("Livestream has been saved to file.")
        logging.info("")

        print()

        return stream_statistics

class Livestream():
    """
    Methods for livestreaming a Subreddit or Redditor's new comments or submissions.
    """

    @staticmethod
    def _set_info_and_object(args, reddit):
        """
        Set the stream information and Reddit object based on CLI args.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        reddit: PRAW Reddit object

        Returns
        -------
        reddit_object: PRAW Subreddit or Redditor object
        stream_info: str
            String denoting the livestream information
        """

        if args.live_subreddit:
            PRAWTitles.lr_title()

            Validation.validate([args.live_subreddit], reddit, "subreddit")

            initial_message = f"Initializing Subreddit livestream for r/{args.live_subreddit}."
            
            stream_info = f"in r/{args.live_subreddit}"
            reddit_object = reddit.subreddit(args.live_subreddit)

        elif args.live_redditor:
            PRAWTitles.lu_title()

            Validation.validate([args.live_redditor], reddit, "redditor")

            initial_message = f"Initializing Redditor livestream for u/{args.live_redditor}."
            
            stream_info = f"by u/{args.live_redditor}"
            reddit_object = reddit.redditor(args.live_redditor)
        
        Halo().info(Fore.CYAN + Style.BRIGHT + initial_message)
        logging.info(initial_message + "..")
        Halo().info("New entries will appear when posted to Reddit.")

        return reddit_object, stream_info

    @staticmethod
    def _stream_switch(args, reddit_object):
        """
        A switch that determines what Reddit objects are yielded (comments or 
        submissions).

        Calls public methods from an external module:

            StreamGenerator.stream_submissions()
            StreamGenerator.stream_comments()

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
            Halo().info(Fore.BLUE + Style.BRIGHT + "Displaying submissions.")
            object_info = "submissions"
            generator = StreamGenerator.stream_submissions(reddit_object.stream)
        else:
            Halo().info(Fore.BLUE + Style.BRIGHT + "Displaying comments.")
            object_info = "comments"
            generator = StreamGenerator.stream_comments(reddit_object.stream)

        print()

        return generator, object_info

    @staticmethod
    def _no_save_stream(generator, object_info, stream_info):
        """
        Only stream new Reddit comments or submissions. Do not save to file.

        Parameters
        ----------
        generator: Reddit object generator
        object_info: str
            String denoting which Reddit objects are displayed in the stream
        stream_info: str
            String denoting the livestream information

        Returns
        -------
        stream_statistics: str
            String denoting the livestream statistics (Reddit objects, Subreddit
            or Redditor, and duration)
        """

        start_stream = time.time()

        try:
            logging.info("")
            logging.info("STREAMING...")
            logging.info("")

            for obj in generator:
                DisplayStream.display(obj)
        except KeyboardInterrupt:
            duration = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_stream))
            stream_statistics = f"Streamed {object_info} submitted {stream_info} for {duration}."

            print("\n\n")
            Halo().info(Fore.YELLOW + Style.BRIGHT + "ABORTING LIVESTREAM.")
            logging.info("ABORTING LIVESTREAM.")
            logging.info("")

            Halo().info(stream_statistics)
            print()

        return stream_statistics

    @staticmethod
    def stream(args, reddit):
        """
        Livestream comments or submissions to terminal. Write the stream to file
        in real time, if applicable.

        Calls previously defined private methods:

            Livestream._stream_switch()
            SaveStream.write()

        Calls public methods from external modules:

            DisplayStream.display()

            PRAWTitles.lr_title()
            PRAWTitles.lu_title()

            Validation.validate()

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

        reddit_object, stream_info = Livestream._set_info_and_object(args, reddit)
        generator, object_info = Livestream._stream_switch(args, reddit_object)

        stream_statistics = Livestream._no_save_stream(generator, object_info, stream_info) \
            if args.nosave \
            else SaveStream.write(args, generator, object_info, stream_info)

        logging.info(stream_statistics)
        logging.info("")
