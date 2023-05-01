"""
Initialize directories
======================
Initialize directories in which scraped or analytical data is stored.
"""


import os


class InitializeDirectory:
    """
    Methods for initializing directories for the exported files.
    """

    @staticmethod
    def create_dirs(path: str) -> None:
        """
        Make directories for scrape files.

        :param str path: The path to the directories in which scrape files are
            saved.
        """

        if not os.path.isdir(path):
            os.makedirs(path)
