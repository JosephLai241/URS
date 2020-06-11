#===============================================================================
#                                Log Decorators
#===============================================================================
import logging
import time

from colorama import Fore, init, Style

from . import DirInit, Global

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class LogMain():
    """
    Decorator for logging URS runtime. Also handles KeyboardInterrupt and adds the
    event to the log if applicable.
    """

    ### Makes directory in which the log and scraped files will be stored.
    DirInit.InitializeDirectory.make_directory()

    ### Set directory path and log format.
    DIR_PATH = "../scrapes/%s" % Global.date
    LOG_FORMAT = "[%(asctime)s] [%(levelname)s]: %(message)s"

    ### Configure logging settings.
    logging.basicConfig(filename = DIR_PATH + "/scrapes.log", 
                        format = LOG_FORMAT,
                        level = logging.INFO)
    
    ### Wrapper for logging the amount of time it took to execute main(). Handle
    ### KeyboardInterrupt if user cancels scraping.
    @staticmethod
    def master_timer(function):
        def wrapper(*args):
            logging.info("Initializing URS...")
            logging.info("")

            start = time.time()
            
            try:
                function(*args)
            except KeyboardInterrupt:
                print(Style.BRIGHT + Fore.RED + "\n\nURS ABORTED BY USER.\n")
                logging.critical("")
                logging.critical("URS ABORTED BY USER.\n")
                quit()

            runtime = "URS completed scrapes in %.2f seconds.\n" % \
                (time.time() - start)
            
            logging.info((runtime))

        return wrapper

class LogScraper():
    """
    Decorator for logging runtimes and program events. 
    """

    ### Get scraper type for logging.
    @staticmethod
    def _get_args_switch(args, scraper):
        scrapers = {
            Global.s_t[0]: [arg_set for arg_set in args.subreddit] if args.subreddit \
                else None,
            Global.s_t[1]: [arg_set for arg_set in args.redditor] if args.redditor \
                else None,
            Global.s_t[2]: [arg_set for arg_set in args.comments] if args.comments \
                else None
        }

        return scrapers.get(scraper)

    ### Replace the second tuple item with the full category name if Subreddit
    ### scraper is selected.
    @staticmethod
    def _subreddit_tuple(each_arg):
        args_list = list(each_arg)
        args_list[1] = Global.categories[Global.short_cat.index(each_arg[1].upper())] 
        return tuple(args_list)

    ### Get the full Subreddit category name for each Subreddit tuple.
    @staticmethod
    def _format_subreddit_settings(scraper, scraper_args):
        args = []
        for each_arg in scraper_args:
            settings = LogScraper._subreddit_tuple(each_arg) if scraper == Global.s_t[0] \
                else tuple(each_arg)

            args.append(settings)

        return args

    ### Format Subreddit log differently if user searched for keywords.
    @staticmethod
    def _format_subreddit_log(each_arg):
        return "Scraping r/%s for %s %s results..." % each_arg \
            if each_arg[1] != Global.categories[5] else \
                "Searching and scraping r/%s for posts containing '%s'..." % \
                    (each_arg[0], each_arg[2])

    ### Format Redditor log depending on number of results scraped.
    @staticmethod
    def _format_redditor_log(each_arg):
        plurality = "results" if int(each_arg[1]) > 1 else "result"
        return "Scraping %s %s for u/%s..." % (each_arg[1], plurality, each_arg[0])

    ### Format comments log depending on raw or structured export.
    @staticmethod
    def _format_comments_log(each_arg):
        plurality = "comments" if int(each_arg[1]) > 1 else "comment"
        return "Processing %s %s and including second and third-level replies from Reddit post %s" % \
            (each_arg[1], plurality, each_arg[0]) if int(each_arg[1]) > 0 else \
                "Processing all comments in raw format from Reddit post %s" % each_arg[0]

    ### Format string for log file depending on what was scraped, then log the 
    ### string.
    @staticmethod
    def _format_scraper_log(args_list, scraper):
        args = LogScraper._format_subreddit_settings(scraper, args_list)
        for each_arg in args:
            formats = {
                Global.s_t[0]: LogScraper._format_subreddit_log(each_arg) \
                    if scraper == Global.s_t[0] else None,
                Global.s_t[1]: LogScraper._format_redditor_log(each_arg) \
                    if scraper == Global.s_t[1] else None,
                Global.s_t[2]: LogScraper._format_comments_log(each_arg) \
                    if scraper == Global.s_t[2] else None
            }

            logging.info(formats.get(scraper))

    ### Wrapper for logging the amount of time it took to execute a scraper.
    @staticmethod
    def scraper_timer(scraper):
        def decorator(function):
            def wrapper(*args):
                start = time.time()
                
                start_log = "Running %s scraper..." % scraper.capitalize()
                logging.info((start_log))

                function(*args)

                LogScraper._format_scraper_log(
                    LogScraper._get_args_switch(args[1], scraper), scraper)

                runtime = "%s scraper finished in %.2f seconds." %\
                    (scraper.capitalize(), time.time() - start)
                logging.info((runtime))
                logging.info("")

            return wrapper
        return decorator

class LogExport():
    """
    Decorator for logging exporting files.
    """

    @staticmethod
    def log_export(function):
        def wrapper(*args):
            try:
                function(*args)
                export_log = "Exporting scrapes to JSON files." if args[1].json else \
                    "Exporting scrapes to CSV files."
                logging.info(export_log)
                logging.info("")
            except Exception as e:
                logging.critical("AN ERROR HAS OCCURED WHILE EXPORTING SCRAPED DATA.")
                logging.critical(e)

        return wrapper
