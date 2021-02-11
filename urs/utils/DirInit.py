#===============================================================================
#                           Initialize Directories
#===============================================================================
import os

from utils import Global

class InitializeDirectory():
    """
    Methods for initializing directories for the exported files.
    """
    
    ### On the first run, create the `scrapes/` directory. Then make a sub-directory 
    ### corresponding with the date in which the user scraped data from Reddit if it 
    ### does not exist.
    @staticmethod
    def make_directory():
        top_dir = "../scrapes"
        if not os.path.isdir(top_dir):
            os.mkdir(top_dir)
        
        date_dir = "../scrapes/%s" % Global.date
        if not os.path.isdir(date_dir):
            os.mkdir(date_dir)

    ### Make Subreddit, Redditor, or comments directory within the date directory
    ### if it doesn't exist.
    @staticmethod
    def make_type_directory(scrape):
        scrape_dir = "../scrapes/%s/%s" % (Global.date, scrape)
        if not os.path.isdir(scrape_dir):
            os.mkdir(scrape_dir)
    