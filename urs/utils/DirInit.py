#===============================================================================
#                           Initialize Directories
#===============================================================================
import os

from . import Global

class InitializeDirectory():
    """
    On the first run, create the `scrapes/` directory. Then make a sub-directory 
    corresponding with the date in which the user scraped data from Reddit if it 
    does not exist.
    """
    
    @staticmethod
    def make_directory():
        scrapes_dir = "../scrapes"
        if not os.path.isdir(scrapes_dir):
            os.mkdir(scrapes_dir)
        
        dir_path = "../scrapes/%s" % Global.date
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
