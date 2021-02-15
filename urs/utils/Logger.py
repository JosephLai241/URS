#===============================================================================
#                                Log Decorators
#===============================================================================
import logging
import time

from colorama import (
    init, 
    Fore, 
    Style
)
from prawcore import PrawcoreException

from utils.DirInit import InitializeDirectory
from utils.Global import (
    analytical_tools,
    categories,
    convert_time,
    date,
    eo,
    s_t,
    short_cat
)
from utils.Titles import Errors

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class LogMain():
    """
    Decorator for logging URS runtime. Also handles KeyboardInterrupt and adds the
    event to the log if applicable.
    """

    ### Makes directory in which the log and scraped files will be stored.
    InitializeDirectory.make_directory()

    ### Set directory path and log format.
    DIR_PATH = "../scrapes/%s" % date
    LOG_FORMAT = "[%(asctime)s] [%(levelname)s]: %(message)s"

    ### Configure logging settings.
    logging.basicConfig(
        filename = DIR_PATH + "/scrapes.log", 
        format = LOG_FORMAT, 
        level = logging.INFO
    )
    
    ### Wrapper for logging the amount of time it took to execute main(). Handle
    ### KeyboardInterrupt if user cancels scraping.
    @staticmethod
    def master_timer(function):
        def wrapper(*args):
            logging.info("INITIALIZING URS.")
            logging.info("")

            start = time.time()
            
            try:
                function(*args)
            except KeyboardInterrupt:
                print(Style.BRIGHT + Fore.RED + "\n\nURS ABORTED BY USER.\n")
                logging.warning("")
                logging.warning("URS ABORTED BY USER.\n")
                quit()

            logging.info("URS COMPLETED IN %.2f SECONDS.\n" % (time.time() - start))

        return wrapper

class LogError():
    """
    Decorator for logging args, PRAW, or rate limit errors.
    """

    ### Wrapper for logging if the help message was printed/if no arguments were
    ### given.
    @staticmethod
    def log_no_args(function):
        def wrapper(self):
            try:
                args, parser = function(self)
                return args, parser
            except SystemExit:
                logging.info("HELP WAS DISPLAYED.\n")
                quit()
        
        return wrapper

    ### Wrapper for logging argument errors.
    @staticmethod
    def log_args(function):
        def wrapper(self, args, parser):
            try:
                function(self, args, parser)
            except ValueError:
                Errors.e_title()
                logging.critical("INVALID ARGUMENTS GIVEN.\n")
                parser.exit()

        return wrapper

    ### Wrapper for logging PRAW errors.
    @staticmethod
    def log_login(function):
        def wrapper(parser, reddit):
            print("\nLogging in...")

            try:
                function(parser, reddit)
                logging.info("Successfully logged in as u/%s." % reddit.user.me())
                logging.info("")
            except PrawcoreException as error:
                Errors.p_title(error)
                logging.critical("LOGIN FAILED.")
                logging.critical("PRAWCORE EXCEPTION: %s.\n" % error)
                parser.exit()

        return wrapper

    ### Wrapper for logging rate limit and errors.
    @staticmethod
    def log_rate_limit(function):
        def wrapper(reddit):
            user_limits = function(reddit)

            logging.info("RATE LIMIT DISPLAYED")
            logging.info("Remaining requests: %s" % int(user_limits["remaining"]))
            logging.info("Used requests: %s" % user_limits["used"])
            logging.info("")

            if int(user_limits["remaining"]) == 0:
                Errors.l_title(convert_time(user_limits["reset_timestamp"]))
                logging.critical("RATE LIMIT REACHED. RATE LIMIT WILL RESET AT %s.\n" % convert_time(user_limits["reset_timestamp"]))
                quit()
            
            return user_limits
        return wrapper

class LogPRAWScraper():
    """
    Decorator for logging scraper runtimes and events.
    """

    ### Get scraper type for logging.
    @staticmethod
    def _get_args_switch(args, scraper):
        scrapers = {
            s_t[0]: [arg_set for arg_set in args.subreddit] \
                if args.subreddit \
                else None,
            s_t[1]: [arg_set for arg_set in args.redditor] \
                if args.redditor \
                else None,
            s_t[2]: [arg_set for arg_set in args.comments] \
                if args.comments \
                else None
        }

        return scrapers.get(scraper)

    ### Replace the second tuple item with the full category name if Subreddit
    ### scraper is selected.
    @staticmethod
    def _subreddit_tuple(each_arg):
        args_list = list(each_arg)
        args_list[1] = categories[short_cat.index(each_arg[1].upper())]
         
        return tuple(args_list)

    ### Get the full Subreddit category name for each Subreddit tuple.
    @staticmethod
    def _format_subreddit_settings(scraper, scraper_args):
        args = []
        for each_arg in scraper_args:
            settings = LogPRAWScraper._subreddit_tuple(each_arg) \
                if scraper == s_t[0] \
                else tuple(each_arg)

            args.append(settings)

        return args

    ### Set message depending if the Search category was selected.
    @staticmethod
    def _set_subreddit_log(category, n_res_or_kwds, sub_name):
        return "Scraping r/%s for %s %s results..." % (sub_name, n_res_or_kwds, category) \
            if category != categories[5] \
            else "Searching and scraping r/%s for posts containing '%s'..." % (sub_name, n_res_or_kwds)

    ### Format Subreddit log differently if user searched for keywords. Log an
    ### additional line if the time filter was applied.
    @staticmethod
    def _format_subreddit_log(each_arg):
        if len(each_arg) == 4:
            logging.info("Getting posts from the past %s for %s results." % (each_arg[3], each_arg[1]))

        return LogPRAWScraper._set_subreddit_log(each_arg[1], each_arg[2], each_arg[0])

    ### Format Redditor log depending on number of results scraped.
    @staticmethod
    def _format_redditor_log(each_arg):
        plurality = "results" \
            if int(each_arg[1]) > 1 \
            else "result"
        return "Scraping %s %s for u/%s..." % (each_arg[1], plurality, each_arg[0])

    ### Format comments log depending on raw or structured export.
    @staticmethod
    def _format_comments_log(each_arg):
        plurality = "comments" if int(each_arg[1]) > 1 else "comment"
        return "Processing %s %s in structured format from Reddit post %s" % (each_arg[1], plurality, each_arg[0]) \
            if int(each_arg[1]) > 0 \
            else "Processing all comments in raw format from Reddit post %s" % each_arg[0]

    ### Format string for log file depending on what was scraped, then log the 
    ### string.
    @staticmethod
    def _format_scraper_log(args_list, scraper):
        args = LogPRAWScraper._format_subreddit_settings(scraper, args_list)
        for each_arg in args:
            formats = {
                s_t[0]: LogPRAWScraper._format_subreddit_log(each_arg) \
                    if scraper == s_t[0] \
                    else None,
                s_t[1]: LogPRAWScraper._format_redditor_log(each_arg) \
                    if scraper == s_t[1] \
                    else None,
                s_t[2]: LogPRAWScraper._format_comments_log(each_arg) \
                    if scraper == s_t[2] \
                    else None
            }

            logging.info(formats.get(scraper))
            logging.info("")

    ### Wrapper for logging the amount of time it took to execute a scraper.
    @staticmethod
    def scraper_timer(scraper):
        def decorator(function):
            def wrapper(*args):
                start = time.time()

                logging.info("RUNNING %s SCRAPER." % scraper.upper())
                logging.info("")

                function(*args)

                LogPRAWScraper._format_scraper_log(LogPRAWScraper._get_args_switch(args[0], scraper), scraper)

                logging.info("%s SCRAPER FINISHED IN %.2f SECONDS." % (scraper.upper(), time.time() - start))
                logging.info("")

            return wrapper
        return decorator

    ### Wrapper for logging if the user cancelled Subreddit scraping at the
    ### confirmation page.
    @staticmethod
    def log_cancel(function):
        def wrapper(*args):
            try:
                function(*args)
            except KeyboardInterrupt:
                print(Fore.RED + Style.BRIGHT + "\n\nCancelling.\n")
                logging.info("")
                logging.info("SUBREDDIT SCRAPING CANCELLED BY USER.\n")
                quit()
            
        return wrapper

class LogAnalytics():
    """
    Decorator for logging analytical tools.
    """

    ### Get tool type for logging.
    @staticmethod
    def _get_args_switch(args, tool):
        tools = {
            analytical_tools[0]: [arg_set for arg_set in args.frequencies] \
                if args.frequencies \
                else None,
            analytical_tools[1]: [arg_set for arg_set in args.chart] \
                if args.chart \
                else None,
            analytical_tools[2]: [arg_set for arg_set in args.wordcloud] \
                if args.wordcloud \
                else None
        }

        return tools.get(tool)

    ### Wrapper for logging if the result was saved.
    @staticmethod
    def log_save(tool):
        def decorator(function):
            def wrapper(*args):
                filename = function(*args)
                
                logging.info("Saved %s to %s." % (tool, filename))
                logging.info("")
                
            return wrapper
        return decorator

    ### Wrapper for logging if the result was displayed.
    @staticmethod
    def log_show(tool):
        def decorator(function):
            def wrapper(*args):
                function(*args)
                
                logging.info("Displayed %s." % tool)
                logging.info("")
                
            return wrapper
        return decorator

    ### Get export type for logging.
    @staticmethod
    def _get_export_switch(f_type):
        export_options = {
            0: "Exporting to JSON.",
            1: "Exporting to CSV."
        }

        if f_type == eo[0]:
            return export_options.get(1)

        return export_options.get(0)

    ### Log the export format for the frequencies generator.
    @staticmethod
    def log_export(function):
        def wrapper(*args):
            try:
                function(*args)

                logging.info(LogAnalytics._get_export_switch(args[2]))
                logging.info("")
            except Exception as e:
                logging.critical("AN ERROR HAS OCCURED WHILE EXPORTING SCRAPED DATA.")
                logging.critical("%s\n" % e)

        return wrapper

    ### Log the analytical tool that was used.
    @staticmethod
    def _log_tool(args, tool):
        args_list = LogAnalytics._get_args_switch(args, tool)

        for file in args_list:
            logging.info("Generating %s for file %s..." % (tool, file[0]))
            logging.info("")

    ### Wrapper for logging the amount of time it took to execute a tool.
    @staticmethod
    def generator_timer(tool):
        def decorator(function):
            def wrapper(*args):
                start = time.time()

                logging.info("RUNNING %s GENERATOR." % tool.upper())
                logging.info("")

                LogAnalytics._log_tool(args[0], tool)
                
                function(*args)

                logging.info("%s GENERATOR FINISHED IN %.2f SECONDS." % (tool.upper(), time.time() - start))
                logging.info("")

            return wrapper
        return decorator

class LogExport():
    """
    Decorator for logging exporting files.
    """

    ### Get export type for logging.
    @staticmethod
    def _get_export_switch(args):
        export_options = {
            0: "Exporting to JSON.",
            1: "Exporting to CSV."
        }

        if args.csv:
            return export_options.get(1)

        return export_options.get(0)

    ### Wrapper for logging the export option.
    @staticmethod
    def log_export(function):
        def wrapper(*args):
            try:
                function(*args)

                logging.info(LogExport._get_export_switch(args[0]))
                logging.info("")
            except Exception as e:
                logging.critical("AN ERROR HAS OCCURED WHILE EXPORTING SCRAPED DATA.")
                logging.critical("%s\n" % e)

        return wrapper
