"""
Initialize directories
======================
Initialize directories in which scraped or analytical data is stored.
"""


import os

class InitializeDirectory():
    """
    Methods for initializing directories for the exported files.
    """

    @staticmethod
    def create_dirs(path):
        """
        Make directories for scrape files.

        Parameters
        ----------
        path: str
            String denoting the path to the directories in which scrape files are
            saved

        Returns
        -------
        None
        """

        if not os.path.isdir(path):
            os.makedirs(path)
