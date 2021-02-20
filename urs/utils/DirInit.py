"""
Initialize directories
======================
Initialize directories in which scraped or analytical data is stored.
"""


import os

from urs.utils.Global import date

class InitializeDirectory():
    """
    Methods for initializing directories for the exported files.
    """
    
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
        if not os.path.isdir(top_dir):
            os.mkdir(top_dir)
        
        date_dir = top_dir + date
        if not os.path.isdir(date_dir):
            os.mkdir(date_dir)

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
        if not os.path.isdir(scrape_dir):
            os.mkdir(scrape_dir)
    
    @staticmethod
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
        if not os.path.isdir(analytics_dir):
            os.mkdir(analytics_dir)

        tool_dir = analytics_dir + tool_type
        if not os.path.isdir(tool_dir):
            os.mkdir(tool_dir)
        