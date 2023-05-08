"""
Log decorators
==============
Decorators that log what is happening behind the scenes to `urs.log`.
"""


import logging
import time
from argparse import ArgumentParser, Namespace
from typing import Any, Callable, Dict, List, Literal, Tuple

from colorama import Fore, Style
from praw import Reddit

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Global import categories, convert_time, date, short_cat
from urs.utils.Titles import Errors


class LogMain:
    """
    Decorator for logging URS runtime. Also handles KeyboardInterrupt and adds the
    event to the log if applicable.
    """

    ### Set directory path and log format.
    DIR_PATH = f"../scrapes/{date}"
    LOG_FORMAT = "[%(asctime)s] [%(levelname)s]: %(message)s"

    ### Makes the `scrapes/[DATE]` directory in which the log and scraped files
    ### will be stored.
    InitializeDirectory.create_dirs(DIR_PATH)

    ### Configure logging settings.
    logging.basicConfig(
        filename=DIR_PATH + "/urs.log", format=LOG_FORMAT, level=logging.INFO
    )

    @staticmethod
    def master_timer(function: Callable[[None], None]) -> Callable[[None], None]:
        """
        Wrapper for logging the amount of time it took to execute main(). Handle
        KeyboardInterrupt if user cancels URS.

        :param Callable[[None], None] function: The function to run in the wrapper.

        :raises KeyboardInterrupt: Raised if the user cancels URS.

        :returns: The wrapper function that runs the function passed into the
            decorator.
        :rtype: `Callable[[None], None]`
        """

        def wrapper(*args: Any) -> None:
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

            logging.info(f"URS COMPLETED IN {time.time() - start:.2f} SECONDS.\n")

        return wrapper


class LogError:
    """
    Decorator for logging args, PRAW, or rate limit errors.
    """

    @staticmethod
    def log_no_args(
        function: Callable[[Any], Tuple[Namespace, ArgumentParser]]
    ) -> Callable[[Any], Tuple[Namespace, ArgumentParser]]:
        """
        Wrapper for logging if the help message was printed/if no arguments were
        given.

        :param Callable[[Any], Tuple[Namespace, ArgumentParser]] function: The
            function to run in the wrapper.

        :raises SystemExit: Raised if no, invalid, or example args were entered.

        :returns: The `Namespace` and `ArgumentParser` objects.
        :rtype: `(Namespace, ArgumentParser)`
        """

        def wrapper(self: Any) -> Tuple[Namespace, ArgumentParser]:
            try:
                args, parser = function(self)
                return args, parser
            except SystemExit:
                logging.info("HELP OR VERSION WAS DISPLAYED.\n")
                quit()

        return wrapper

    @staticmethod
    def log_args(error: str) -> Callable[..., Callable[..., None]]:
        """
        Wrapper for logging individual (specific) arg errors.

        :param str error: The specific error that was raised when processing args.

        :returns: The decorator function that runs the function that is passed
            into it.
        :rtype: `Callable[..., Callable[..., None]]`
        """

        def decorator(function: Callable[..., None]) -> Callable[..., None]:
            def wrapper(*args: Any) -> None:
                try:
                    function(*args)
                except ValueError:
                    Errors.e_title(f"INVALID {error}.")
                    logging.critical(f"RECEIVED INVALID {error}.")
                    logging.critical("ABORTING URS.\n")
                    quit()

            return wrapper

        return decorator

    @staticmethod
    def log_rate_limit(
        function: Callable[[Reddit], Dict[str, Any]]
    ) -> Callable[[Reddit], Dict[str, Any]]:
        """
        Wrapper for logging rate limit and errors.

        :param Callable[[Reddit], dict[str, Any]] function: The function to run
            within the wrapper function.

        :returns: The wrapper function that runs the function passed into the
            decorator.
        :rtype: `Callable[[Reddit], Dict[str, Any]]`
        """

        def wrapper(reddit: Reddit) -> Dict[str, Any]:
            user_limits = function(reddit)

            logging.info("RATE LIMIT DISPLAYED.")
            logging.info(f"Remaining requests: {user_limits['remaining']}")
            logging.info(f"Used requests: {user_limits['used']}")
            logging.info("")

            if int(user_limits["remaining"]) == 0:
                Errors.l_title(convert_time(user_limits["reset_timestamp"]))
                logging.critical(
                    f"RATE LIMIT REACHED. RATE LIMIT WILL RESET AT {convert_time(user_limits['reset_timestamp'])}."
                )
                logging.critical("ABORTING URS.\n")
                quit()

            return user_limits

        return wrapper


class LogPRAWScraper:
    """
    Decorator for logging scraper runtimes and events.
    """

    @staticmethod
    def _format_subreddit_log(settings_dict: Dict[str, Any]) -> None:
        """
        Format Subreddit log message.

        :param dict[str, Any] settings_dict: A `dict[str, Any]` containing Subreddit
            scraping settings.
        """

        time_filters = ["day", "hour", "month", "week", "year"]

        for subreddit_name, settings in settings_dict.items():
            for each_setting in settings:
                if each_setting[2] in time_filters:
                    logging.info(
                        f"Getting posts from the past {each_setting[2]} for {categories[short_cat.index(each_setting[0].upper())]} results."
                    )
                if each_setting[0].lower() != "s":
                    logging.info(
                        f"Scraping r/{subreddit_name} for {each_setting[1]} {categories[short_cat.index(each_setting[0].upper())]} results..."
                    )
                elif each_setting[0].lower() == "s":
                    logging.info(
                        f"Searching and scraping r/{subreddit_name} for posts containing '{each_setting[1]}'..."
                    )

                logging.info("")

    @staticmethod
    def _format_two_arg_log(
        scraper_type: Literal["comments", "redditor"], settings_dict: Dict[str, Any]
    ) -> None:
        """
        Format Redditor or submission comments log message. Both only take two
        arguments, which is why only one method is needed to format the messages.

        :param str scrape_type: The scraper type (`"comments"` or `"redditor"`)
        :param dict[str, Any] settings_dict: A `dict[str, Any]` containing Redditor
            scraping settings.
        """

        for reddit_object, n_results in settings_dict.items():
            plurality = "results" if int(n_results) > 1 else "result"

            if scraper_type == "redditor":
                logging.info(
                    f"Scraping {n_results} {plurality} for u/{reddit_object}..."
                )
            elif scraper_type == "comments":
                logging.info(
                    f"Processing all comments from Reddit post {reddit_object}..."
                ) if int(n_results) == 0 else logging.info(
                    f"Processing {n_results} {plurality} from Reddit post {reddit_object}..."
                )

            logging.info("")

    @staticmethod
    def _format_scraper_log(
        scraper: Literal["comments", "redditor", "subreddit"],
        settings_dict: Dict[str, Any],
    ) -> None:
        """
        Format log depending on raw or structured export.

        :param str scrape_type: The scraper type (`"comments"`, `"redditor"`, or
            `"subreddit"`).
        :param dict[str, Any] settings_dict: A `dict[str, Any]` containing Redditor
            scraping settings.
        """

        if scraper == "subreddit":
            LogPRAWScraper._format_subreddit_log(settings_dict)
        elif scraper == "redditor":
            LogPRAWScraper._format_two_arg_log("redditor", settings_dict)
        elif scraper == "comments":
            LogPRAWScraper._format_two_arg_log("comments", settings_dict)

    @staticmethod
    def scraper_timer(
        scraper: Literal["comments", "redditor", "subreddit"]
    ) -> Callable[..., Any]:
        """
        Wrapper for logging the amount of time it took to execute a scraper.

        :param str scraper: The scraper that is ran (`"comments"`, `"redditor"`,
            or `"subreddit"`).

        :returns: The decorator function that runs the function passed into this
            function.
        :rtype: `Callable[..., Any]`
        """

        def decorator(function: Callable[..., Any]) -> Callable[..., None]:
            def wrapper(*args: Any) -> None:
                start = time.time()

                logging.info(f"RUNNING {scraper.upper()} SCRAPER.")
                logging.info("")

                settings_dict = function(*args)

                LogPRAWScraper._format_scraper_log(scraper, settings_dict)

                logging.info(
                    f"{scraper.upper()} SCRAPER FINISHED IN {time.time() - start:.2f} SECONDS."
                )
                logging.info("")

            return wrapper

        return decorator

    @staticmethod
    def log_cancel(function: Callable[..., None]) -> Callable[..., None]:
        """
        Wrapper for logging if the user cancelled Subreddit scraping at the
        confirmation page.

        :param Callable[..., None] function: The function to run within the wrapper.

        :returns: The wrapper function that runs the function passed into the
            decorator.
        :rtype: `Callable[..., None]`
        """

        def wrapper(*args: Any) -> None:
            try:
                function(*args)
            except KeyboardInterrupt:
                print(Fore.RED + Style.BRIGHT + "\n\nCancelling.\n")
                logging.info("")
                logging.info("SUBREDDIT SCRAPING CANCELLED BY USER.\n")
                quit()

        return wrapper


class LogAnalyticsErrors:
    """
    Decorator for logging errors while exporting analytical data.
    """

    @staticmethod
    def log_invalid_top_dir(
        function: Callable[..., Tuple[str, str]]
    ) -> Callable[..., Tuple[str, str]]:
        """
        Log invalid top directory when running analytical tools.

        :param Callable[..., Tuple[str, str]] function: The function to run within
            the wrapper function.

        :raises ValueError: Raise if the file is not located within the `scrapes/`
            directory.

        :returns: The wrapper function that runs the function passed into the
            decorator
        :rtype: `Callable[..., Tuple[str, str]]`
        """

        def wrapper(*args: Any) -> Tuple[str, str]:
            try:
                return function(*args)
            except ValueError:
                Errors.i_title(
                    "Scrape data is not located within the `scrapes` directory."
                )
                logging.critical("AN ERROR HAS OCCURRED WHILE PROCESSING SCRAPE DATA.")
                logging.critical(
                    "Scrape data is not located within the `scrapes` directory."
                )
                logging.critical("ABORTING URS.\n")
                quit()
            except TypeError:
                Errors.i_title("Invalid file. Try again with a valid JSON file.")
                logging.critical("AN ERROR HAS OCCURRED WHILE PROCESSING SCRAPE DATA.")
                logging.critical("Invalid file.")
                logging.critical("ABORTING URS.\n")
                quit()

        return wrapper


class LogAnalytics:
    """
    Decorator for logging analytical tools.
    """

    @staticmethod
    def _get_args_switch(
        args: Namespace, tool: Literal["frequencies", "wordcloud"]
    ) -> List[List[str]]:
        """
        Get tool type for logging.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param str tool: The name of the tool that is run (`"frequencies"` or
            `"wordcloud"`).

        :returns: A `list[list[str]]` of scraping arguments.
        :rtype: `list[list[str]]`
        """

        tools = {
            "frequencies": [arg_set for arg_set in args.frequencies]
            if args.frequencies
            else None,
            "wordcloud": [arg_set for arg_set in args.wordcloud]
            if args.wordcloud
            else None,
        }

        return tools.get(tool)

    @staticmethod
    def log_save(tool: str) -> Callable[..., Callable[..., None]]:
        """
        Wrapper for logging if the result was saved.

        :param str tool: The name of the tool that is run.

        :returns: The decorator function that runs the function passed into this
            function.
        :rtype: `Callable[..., Callable[..., None]]`
        """

        def decorator(function: Callable[..., None]) -> Callable[..., None]:
            def wrapper(*args: Any) -> None:
                filename = function(*args)

                logging.info(f"Saved {tool} to {filename}.")
                logging.info("")

            return wrapper

        return decorator

    @staticmethod
    def log_show(tool: str) -> Callable[..., Callable[..., None]]:
        """
        Wrapper for logging if the result was displayed.

        :param str tool: The name of the tool that is run.

        :returns: The decorator function that runs the function passed into this
            function.
        :rtype: `Callable[..., Callable[..., None]]`
        """

        def decorator(function: Callable[..., None]) -> Callable[..., None]:
            def wrapper(*args: Any) -> None:
                function(*args)

                logging.info(f"Displayed {tool}.")
                logging.info("")

            return wrapper

        return decorator

    @staticmethod
    def _get_export_switch(f_type: Literal["csv", "json"]) -> str:
        """
        Get export type for logging.

        :param str f_type: The file type (`"csv"` or `"json"`).

        :returns: The export option.
        :rtype: `str`
        """

        export_options = {0: "Exporting to JSON.", 1: "Exporting to CSV."}

        if f_type == "csv":
            return export_options.get(1)

        return export_options.get(0)

    @staticmethod
    def log_export(function: Callable[..., None]) -> Callable[..., None]:
        """
        Log the export format for the frequencies generator.

        :param Callable[..., None] function: Run this function within the wrapper.

        :returns: The decorator function that runs the function passed into this
            function.
        :rtype: `Callable[..., None]`
        """

        def wrapper(*args: Any) -> None:
            try:
                function(*args)

                logging.info(LogAnalytics._get_export_switch(args[1]))
                logging.info("")
            except Exception as e:
                Errors.ex_title(e)
                logging.critical("AN ERROR HAS OCCURRED WHILE EXPORTING SCRAPED DATA.")
                logging.critical(f"{e}")
                logging.critical("ABORTING URS.\n")
                quit()

        return wrapper

    @staticmethod
    def _log_tool(args: Namespace, tool: str) -> None:
        """
        Log the analytical tool that was used.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param str tool: The name of the tool that is run.
        """

        args_list = LogAnalytics._get_args_switch(args, tool)

        for filename in args_list:
            logging.info(f"Generating {tool} for file {filename[0]}...")
            logging.info("")

    @staticmethod
    def generator_timer(tool: str) -> Callable[..., Callable[..., None]]:
        """
        Wrapper for logging the amount of time it took to execute a tool.

        :param str tool: The name of the tool that is run.

        :returns: The decorator function that runs the function passed into this
            function.
        :rtype: `Callable[..., Callable[..., None]]`
        """

        def decorator(function: Callable[..., None]) -> Callable[..., None]:
            def wrapper(*args: Any) -> None:
                start = time.time()

                logging.info(f"RUNNING {tool.upper()} GENERATOR.")
                logging.info("")

                LogAnalytics._log_tool(args[0], tool)

                function(*args)

                logging.info(
                    f"{tool.upper()} GENERATOR FINISHED IN {time.time() - start:.2f} SECONDS."
                )
                logging.info("")

            return wrapper

        return decorator


class LogExport:
    """
    Decorator for logging exporting files.
    """

    @staticmethod
    def _get_export_switch(args: Namespace) -> str:
        """
        Get export type for logging.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.

        :returns: The export option.
        :rtype: `str`
        """

        export_options = {0: "Exporting to JSON.", 1: "Exporting to CSV."}

        if args.csv:
            return export_options.get(1)

        return export_options.get(0)

    @staticmethod
    def log_export(function: Callable[..., None]) -> Callable[..., None]:
        """
        Wrapper for logging the export option.

        :param Callable[..., None] function: Run this function within the wrapper.

        :returns: The decorator function that runs the function passed into this
            function.
        :rtype: `Callable[..., Callable[..., None]]`
        """

        def wrapper(*args: Any) -> None:
            try:
                function(*args)

                logging.info(LogExport._get_export_switch(args[0]))
                logging.info("")
            except Exception as e:
                Errors.ex_title(e)
                logging.critical("AN ERROR HAS OCCURRED WHILE EXPORTING SCRAPED DATA.")
                logging.critical(f"{e}")
                logging.critical("ABORTING URS.\n")
                quit()

        return wrapper
