"""
Initialize directories
======================
Initialize directories in which scraped or analytical data is stored.
"""


import logging
import os

from urs.utils.Global import date
from urs.utils.Titles import Errors

class LogMissingDir():
    """
    Decorator for logging missing `scrapes` directory. This decorator has been
    defined in this file to avoid a circular import error.
    """

    @staticmethod
    def log(function):
        """
        Log missing directory when running analytical tools.

        Parameters
        ----------
        function: function()
            Run method within the wrapper

        Exceptions
        ----------
        FileNotFoundError:
            Raised if the file is not located within the correct sub-directory

        Returns
        -------
        wrapper: function()
            Return the wrapper method that runs the method passed into the
            decorator
        """

        def wrapper(*args):
            try:
                function(*args)
            except FileNotFoundError:
                Errors.i_title("Invalid `scrapes` directory structure.")
                logging.critical("AN ERROR HAS OCCURED WHILE PROCESSING SCRAPE DATA.")
                logging.critical("Invalid `scrapes` directory structure.\n")
                logging.critical("ABORTING URS.\n")
                quit()

        return wrapper

class InitializeDirectory():
    """
    Methods for initializing directories for the exported files.
    """

    @staticmethod
    def _create(destination):
        """
        Create the directory if it does not exist.
        """

        if not os.path.isdir(destination):
            os.mkdir(destination)
    
    @staticmethod
    def make_directory():
        """
        On the first run, create the `scrapes/` directory. Then make a sub-directory 
        corresponding with the date in which the user scraped data from Reddit if it 
        does not exist.

        Returns
        -------
        None
        """

        top_dir = "../scrapes/"
        InitializeDirectory._create(top_dir)
        
        date_dir = top_dir + date
        InitializeDirectory._create(date_dir)

    @staticmethod
    def make_type_directory(scrape):
        """
        Make Subreddit, Redditor, or comments directory within the date directory
        if it does not exist.

        Parameters
        ----------
        scrape: str
            Denotes the scrape type (subreddits, redditors, or comments)

        Returns
        -------
        None
        """

        scrape_dir = "../scrapes/%s/%s" % (date, scrape)
        InitializeDirectory._create(scrape_dir)
    
    @staticmethod
    @LogMissingDir.log
    def make_analytics_directory(date_dir, tool_type):
        """
        Make analytics directory if it does not exist.

        Parameters
        ----------
        date_dir: str
            Denotes the date to append to the directory path
        tool_type: str
            Denotes the analytical tool (frequencies or wordclouds)

        Returns
        -------
        None
        """

        analytics_dir = "../scrapes/%s/analytics/" % date_dir
        InitializeDirectory._create(analytics_dir)

        tool_dir = analytics_dir + tool_type
        InitializeDirectory._create(tool_dir)
        