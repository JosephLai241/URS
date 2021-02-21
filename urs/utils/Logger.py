"""
Log decorators
==============
Decorators that log what is happening behind the scenes to `urs.log`.
"""


import logging
import time

from colorama import (
    init, 
    Fore, 
    Style
)
from prawcore import PrawcoreException

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Global import (
    analytical_tools,
    categories,
    convert_time,
    date,
    eo,
    s_t,
    short_cat
)
from urs.utils.Titles import Errors

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
        filename = DIR_PATH + "/urs.log", 
        format = LOG_FORMAT, 
        level = logging.INFO
    )
    
    @staticmethod
    def master_timer(function):
        """
        Wrapper for logging the amount of time it took to execute main(). Handle
        KeyboardInterrupt if user cancels URS.

        Parameters
        ----------
        function: function()
            Run method within the wrapper

        Exceptions
        ----------
        KeyboardInterrupt:
            Raised if user cancels URS

        Returns
        -------
        wrapper: function()
            Return the wrapper method that runs the method passed into the
            decorator
        """

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
    Decorator for logging args, PRAW, rate limit, or no objects to scrape errors.
    """

    @staticmethod
    def log_no_args(function):
        """
        Wrapper for logging if the help message was printed/if no arguments were
        given.

        Parameters
        ----------
        function: function()
            Run method within the wrapper

        Exceptions
        ----------
        SystemExit:
            Raised if no, invalid, or example args were entered 

        Returns
        -------
        wrapper: function()
            Return the wrapper method that runs the method passed into the
            decorator
        """

        def wrapper(self):
            try:
                args, parser = function(self)
                return args, parser
            except SystemExit:
                logging.info("HELP WAS DISPLAYED.\n")
                quit()
        
        return wrapper

    @staticmethod
    def log_args(error):
        """
        Wrapper for logging individual (specific) arg errors.

        Parameters
        ----------
        error: str
            String denoting the specific error that was raised when processing args

        Returns
        -------
        wrapper: function()
            Return the wrapper method that runs the method passed into the
            decorator
        """

        def decorator(function):
            def wrapper(*args):
                try:
                    function(*args)
                except ValueError:
                    Errors.e_title("INVALID %s." % error)
                    logging.critical("RECEIVED INVALID %s." % error)
                    logging.critical("ABORTING URS.\n")
                    quit()
                
            return wrapper
        return decorator

    @staticmethod
    def log_login(function):
        """
        Wrapper for logging PRAW errors.

        Parameters
        ----------
        function: function()
            Run method within the wrapper

        Exceptions
        ----------
        PrawcoreException:
            Raised if invalid PRAW API credentials are given

        Returns
        -------
        wrapper: function()
            Return the wrapper method that runs the method passed into the
            decorator
        """

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

    @staticmethod
    def log_rate_limit(function):
        """
        Wrapper for logging rate limit and errors.

        Parameters
        ----------
        function: function()
            Run method within the wrapper

        Returns
        -------
        wrapper: function()
            Return the wrapper method that runs the method passed into the
            decorator
        """

        def wrapper(reddit):
            user_limits = function(reddit)

            logging.info("RATE LIMIT DISPLAYED.")
            logging.info("Remaining requests: %s" % int(user_limits["remaining"]))
            logging.info("Used requests: %s" % user_limits["used"])
            logging.info("")

            if int(user_limits["remaining"]) == 0:
                Errors.l_title(convert_time(user_limits["reset_timestamp"]))
                logging.critical("RATE LIMIT REACHED. RATE LIMIT WILL RESET AT %s.\n" % convert_time(user_limits["reset_timestamp"]))
                quit()
            
            return user_limits
        return wrapper

    @staticmethod
    def log_none_left(reddit_object):
        """
        Wrapper for logging if nothing was left to scrape after validation, 
        subsequently terminating URS.

        Parameters
        ----------
        reddit_object: str
            String denoting the Reddit object to pass into the exit message

        Returns
        -------
        decorator: function()
            Return the decorator function that runs the method passed into this
            method
        """

        def decorator(function):
            def wrapper(*args):
                try:
                    return function(*args)
                except ValueError:
                    Errors.n_title(reddit_object)
                    logging.critical("No %s left to scrape." % reddit_object)
                    logging.critical("Exiting.\n")
                    quit()
                
            return wrapper
        return decorator

class LogPRAWScraper():
    """
    Decorator for logging scraper runtimes and events.
    """

    @staticmethod
    def _get_args_switch(args, scraper):
        """
        Get scraper type for logging.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI
        scraper: str
            Scraper type which denotes a key in the dictionary

        Returns
        -------
        scraper_args: list
            List of arguments returned from args
        """

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

    @staticmethod
    def _subreddit_tuple(each_arg):
        """
        Replace the second tuple item with the full category name if Subreddit
        scraper is selected.

        Parameters
        ----------
        each_arg: list
            List of Subreddit args
        
        Returns
        -------
        args: tuple
            Tuple of Subreddit args after correction
        """

        args_list = list(each_arg)
        args_list[1] = categories[short_cat.index(each_arg[1].upper())]
         
        return tuple(args_list)

    @staticmethod
    def _format_subreddit_settings(scraper, scraper_args):
        """
        Get the full Subreddit category name for each Subreddit tuple.

        Parameters
        ----------
        scraper: str
            String which denotes the scraper type
        scraper_args: list
            List of scraper args

        Returns
        -------
        args: list
            List of args
        """

        args = []
        for each_arg in scraper_args:
            settings = LogPRAWScraper._subreddit_tuple(each_arg) \
                if scraper == s_t[0] \
                else tuple(each_arg)

            args.append(settings)

        return args

    @staticmethod
    def _set_subreddit_log(category, n_res_or_kwds, sub_name):
        """
        Set message depending if the Search category was selected.

        Parameters
        ----------
        category: str
            String denoting the Subreddit category
        n_res_or_kwds: str
            String denoting n_results to return or keywords to search for
        sub_name: str
            String denoting the Subreddit name

        Returns
        -------
        log_string: str
            String denoting scrape details
        """

        return "Scraping r/%s for %s %s results..." % (sub_name, n_res_or_kwds, category) \
            if category != categories[5] \
            else "Searching and scraping r/%s for posts containing '%s'..." % (sub_name, n_res_or_kwds)

    @staticmethod
    def _format_subreddit_log(each_arg):
        """
        Format Subreddit log differently if user searched for keywords. Log an
        additional line if the time filter was applied. Calls previously defined
        private methods:
            
            LogPRAWScraper._set_subreddit_log()

        Parameters
        ----------
        each_arg: list
            List of arguments passed

        Returns
        -------
        log_string: str
            String denoting scrape details
        """

        if len(each_arg) == 4:
            logging.info("Getting posts from the past %s for %s results." % (each_arg[3], each_arg[1]))

        return LogPRAWScraper._set_subreddit_log(each_arg[1], each_arg[2], each_arg[0])

    @staticmethod
    def _format_redditor_log(each_arg):
        """
        Format Redditor log depending on number of results scraped.

        Parameters
        ----------
        each_arg: list
            List of arguments passed

        Returns
        -------
        log_string: str
            String denoting scrape details
        """

        plurality = "results" \
            if int(each_arg[1]) > 1 \
            else "result"
        return "Scraping %s %s for u/%s..." % (each_arg[1], plurality, each_arg[0])

    @staticmethod
    def _format_comments_log(each_arg):
        """
        Format comments log depending on raw or structured export.

        Parameters
        ----------
        each_arg: list
            List of arguments passed

        Returns
        -------
        log_string: str
            String denoting scrape details
        """

        plurality = "comments" if int(each_arg[1]) > 1 else "comment"
        return "Processing %s %s in structured format from Reddit post %s" % (each_arg[1], plurality, each_arg[0]) \
            if int(each_arg[1]) > 0 \
            else "Processing all comments in raw format from Reddit post %s" % each_arg[0]

    @staticmethod
    def _format_scraper_log(args_list, scraper):
        """
        Format comments log depending on raw or structured export. Calls previously
        defined private methods:

            LogPRAWScraper._format_subreddit_settings()
            LogPRAWScraper._format_subreddit_log()
            LogPRAWScraper._format_redditor_log()
            LogPRAWScraper._format_comments_log()


        Parameters
        ----------
        args_list: list
            List of scraper args
        scraper: str
            Scraper type which denotes a key in the dictionary

        Returns
        -------
        None
        """

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

    @staticmethod
    def scraper_timer(scraper):
        """
        Wrapper for logging the amount of time it took to execute a scraper.

        Parameters
        ----------
        scraper: str
            String denoting the scraper that is run

        Returns
        -------
        decorator: function()
            Return the decorator function that runs the method passed into this
            method
        """

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

    @staticmethod
    def log_cancel(function):
        """
        Wrapper for logging if the user cancelled Subreddit scraping at the
        confirmation page.

        Parameters
        ----------
        function: function()
            Run method within the wrapper

        Returns
        -------
        wrapper: function()
            Return the wrapper method that runs the method passed into the
            decorator
        """

        def wrapper(*args):
            try:
                function(*args)
            except KeyboardInterrupt:
                print(Fore.RED + Style.BRIGHT + "\n\nCancelling.\n")
                logging.info("")
                logging.info("SUBREDDIT SCRAPING CANCELLED BY USER.\n")
                quit()
            
        return wrapper

class LogAnalyticsErrors():
    """
    Decorator for logging errors while exporting analytical data.
    """

    @staticmethod
    def log_invalid_top_dir(function):
        """
        Log invalid top directory when running analytical tools.

        Parameters
        ----------
        function: function()
            Run method within the wrapper

        Exceptions
        ----------
        ValueError:
            Raised if the file is not located within the scrapes directory

        Returns
        -------
        wrapper: function()
            Return the wrapper method that runs the method passed into the
            decorator
        """

        def wrapper(*args):
            try:
                return function(*args)
            except ValueError:
                Errors.i_title("Scrape data is not located within the `scrapes` directory.")
                logging.critical("AN ERROR HAS OCCURED WHILE PROCESSING SCRAPE DATA.")
                logging.critical("Scrape data is not located within the `scrapes` directory.\n")
                quit()

        return wrapper

class LogAnalytics():
    """
    Decorator for logging analytical tools.
    """

    @staticmethod
    def _get_args_switch(args, tool):
        """
        Get tool type for logging.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI
        tool: str
            Tool type which denotes a key in the dictionary

        Returns
        -------
        scraper_args: list
            List of arguments returned from args
        """

        tools = {
            analytical_tools[0]: [arg_set for arg_set in args.frequencies] \
                if args.frequencies \
                else None,
            analytical_tools[1]: [arg_set for arg_set in args.wordcloud] \
                if args.wordcloud \
                else None
        }

        return tools.get(tool)

    @staticmethod
    def log_save(tool):
        """
        Wrapper for logging if the result was saved.

        Parameters
        ----------
        tool: str
            String denoting the tool that is run

        Returns
        -------
        decorator: function()
            Return the decorator function that runs the method passed into this
            method
        """

        def decorator(function):
            def wrapper(*args):
                filename = function(*args)
                
                logging.info("Saved %s to %s." % (tool, filename))
                logging.info("")
                
            return wrapper
        return decorator

    @staticmethod
    def log_show(tool):
        """
        Wrapper for logging if the result was displayed.

        Parameters
        ----------
        tool: str
            String denoting the tool that is run

        Returns
        -------
        decorator: function()
            Return the decorator method that runs the method passed into this
            method
        """

        def decorator(function):
            def wrapper(*args):
                function(*args)
                
                logging.info("Displayed %s." % tool)
                logging.info("")
                
            return wrapper
        return decorator

    @staticmethod
    def _get_export_switch(f_type):
        """
        Get export type for logging.

        Parameters
        ----------
        f_type: str
            String denoting the file type

        Returns
        -------
        export_message: str
            String denoting export option
        """

        export_options = {
            0: "Exporting to JSON.",
            1: "Exporting to CSV."
        }

        if f_type == eo[0]:
            return export_options.get(1)

        return export_options.get(0)

    @staticmethod
    def log_export(function):
        """
        Log the export format for the frequencies generator.

        Parameters
        ----------
        function: function()
            Run method within the wrapper

        Returns
        -------
        wrapper: function()
            Return the wrapper method that runs the method passed into the
            decorator
        """

        def wrapper(*args):
            try:
                function(*args)

                logging.info(LogAnalytics._get_export_switch(args[2]))
                logging.info("")
            except Exception as e:
                logging.critical("AN ERROR HAS OCCURED WHILE EXPORTING SCRAPED DATA.")
                logging.critical("%s\n" % e)

        return wrapper

    @staticmethod
    def _log_tool(args, tool):
        """
        Log the analytical tool that was used.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI
        tool: str
            String denoting the analytical tool

        Returns
        -------
        None
        """

        args_list = LogAnalytics._get_args_switch(args, tool)

        for file in args_list:
            logging.info("Generating %s for file %s..." % (tool, file[0]))
            logging.info("")

    @staticmethod
    def generator_timer(tool):
        """
        Wrapper for logging the amount of time it took to execute a tool.

        Parameters
        ----------
        tool: str
            String denoting the tool that is run

        Returns
        -------
        decorator: function()
            Return the decorator method that runs the method passed into this
            method
        """

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

    @staticmethod
    def _get_export_switch(args):
        """
        Get export type for logging.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI

        Returns
        -------
        export_message: str
            String denoting export option
        """

        export_options = {
            0: "Exporting to JSON.",
            1: "Exporting to CSV."
        }

        if args.csv:
            return export_options.get(1)

        return export_options.get(0)

    @staticmethod
    def log_export(function):
        """
        Wrapper for logging the export option.

        Parameters
        ----------
        function: function()
            Run method within the wrapper

        Returns
        -------
        wrapper: function()
            Return the wrapper method that runs the method passed into the
            decorator
        """

        def wrapper(*args):
            try:
                function(*args)

                logging.info(LogExport._get_export_switch(args[0]))
                logging.info("")
            except Exception as e:
                logging.critical("AN ERROR HAS OCCURED WHILE EXPORTING SCRAPED DATA.")
                logging.critical("%s\n" % e)

        return wrapper
