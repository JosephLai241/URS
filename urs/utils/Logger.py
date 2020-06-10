#===============================================================================
#                                Log Wrappers
#===============================================================================
import logging
import time

from . import Global

class LogRuntime():
    """
    Decorator for logging URS runtime.
    """

    ### Set directory path and log format.
    DIR_PATH = "../scrapes/%s" % Global.date
    LOG_FORMAT = "[%(asctime)s] [%(levelname)s]: %(message)s"

    ### Configure logging settings.
    logging.basicConfig(filename = DIR_PATH + "/scrapes.log", 
                        format = LOG_FORMAT,
                        level = logging.INFO)

    ### Wrapper for logging the amount of time it took to execute main().
    @staticmethod
    def main_timer(function):
        def wrapper(*args):
            start = time.time()
            function(*args)

            runtime = "Completed scraping in %.2f seconds" % (time.time() - start)
            logging.info((runtime))

        return wrapper
