"""
Display settings
================
Display scrape parameters based on included flags
"""


from colorama import (
    Fore,
    Style
)
from halo import Halo
from prettytable import PrettyTable

class Display():
    """
    Methods to display scrape parameters.
    """

    @staticmethod
    def pull_additional_params(args):
        """
        Pull any additional scrape parameters to store in the settings PrettyTable,
        then display the table if applicable.

        Parameters
        ----------
        args: Namespace
            argparse Namespace object

        Returns
        -------
        None
        """

        additional_params = [
            "after",
            "aggs",
            "author",
            "before",
            "contest_mode",
            "fields",
            "frequency",
            "ids",
            "in_subreddit",
            "is_video",
            "locked",
            "metadata",
            "nsfw",
            "num_comments",
            "score",
            "selftext",
            "size",
            "sort",
            "sort_type",
            "spoiler",
            "stickied",
            "title",
        ]

        pretty_params = PrettyTable()
        pretty_params.field_names = [
            "Parameter",
            "Constraint"
        ]

        param_count = 0
        for key, value in vars(args).items():
            if key in additional_params and value:
                pretty_params.add_row([
                    key,
                    value
                ])
                param_count += 1
        
        if param_count > 0:
            Halo().info(Fore.CYAN + Style.BRIGHT + "Additional scrape parameters")

            pretty_params.align = "l"
            print(pretty_params)

    @staticmethod
    def display_settings(args):
        """
        Display scrape parameters.

        Parameters
        ----------
        args: Namespace
            argparse Namespace object

        Returns
        -------
        None
        """

        pretty_query = PrettyTable()
        pretty_query.field_names = [
            "Reddit Object",
            "Query"
        ]

        query_row = ["Comments", args.search_comments] \
            if args.search_comments \
            else ["Submissions", args.search_submissions]

        pretty_query.add_row(query_row)
        pretty_query.align = "l"
        print(pretty_query)
        print()

        Display.pull_additional_params(args)
