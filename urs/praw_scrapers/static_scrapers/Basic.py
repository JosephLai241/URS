"""
Basic Subreddit scraper
=======================
Defining the interface for the basic Subreddit scraper.
"""


import logging
from argparse import ArgumentParser, Namespace
from typing import Any, Dict, List, Tuple, Union

from colorama import Fore, Style
from halo import Halo
from praw import Reddit

from urs.praw_scrapers.static_scrapers.Subreddit import GetSortWrite, PrintConfirm
from urs.praw_scrapers.utils.Validation import Validation
from urs.utils.Global import categories, confirm_settings, make_list_dict, short_cat
from urs.utils.Logger import LogExport, LogPRAWScraper
from urs.utils.Titles import Errors, PRAWTitles


class PrintSubs:
    """
    Methods for printing found and invalid Subreddits.
    """

    @staticmethod
    def _find_subs(reddit: Reddit, search_for: str) -> Tuple[List[str], List[str]]:
        """
        Return a list of valid and invalid Subreddits.

        :param Reddit reddit: PRAW Reddit object.
        :param str search_for: Subreddit(s) to scrape.

        :returns: A `list[str]` of invalid and valid Subreddits.
        :rtype: `(list[str], list[str])`
        """

        search_for = " ".join(search_for.split())
        sub_list = [subreddit for subreddit in search_for.split(" ")]
        not_subs, subs = Validation.check_existence(sub_list, reddit, "subreddit")

        return not_subs, subs

    @staticmethod
    def print_subreddits(reddit: Reddit, search_for: str) -> List[str]:
        """
        Print valid and invalid Subreddits.

        :param Reddit reddit: PRAW Reddit object.
        :param str search_for: Subreddit(s) to scrape.

        :returns: A `list[str]` of valid Subreddits.
        :rtype: `list[str]`
        """

        check_subs_spinner = Halo(color="white", text="Validating Subreddit(s).")
        print()
        check_subs_spinner.start()
        not_subs, subs = PrintSubs._find_subs(reddit, search_for)
        check_subs_spinner.succeed("Finished Subreddit validation.")

        if subs:
            print(
                Fore.GREEN
                + Style.BRIGHT
                + "\nThe following Subreddits were found and will be scraped:"
            )
            print(Fore.GREEN + Style.BRIGHT + "-" * 56)
            print(*subs, sep="\n")
        if not_subs:
            print(
                Fore.YELLOW
                + Style.BRIGHT
                + "\nThe following Subreddits were not found and will be skipped:"
            )
            print(Fore.YELLOW + Style.BRIGHT + "-" * 60)
            print(*not_subs, sep="\n")

            logging.warning("Failed to validate the following Subreddits:")
            logging.warning(f"{not_subs}")
            logging.warning("Skipping.")
            logging.info("")

        if not subs:
            logging.critical("ALL SUBREDDITS FAILED VALIDATION.")
            Errors.n_title("Subreddits")
            logging.critical("NO SUBREDDITS LEFT TO SCRAPE.")
            logging.critical("ABORTING URS.\n")

            quit()

        return subs


class GetInput:
    """
    Methods for handling user input.
    """

    @staticmethod
    def get_subreddits(reddit: Reddit) -> List[str]:
        """
        Enter Subreddit(s) to scrape and check if they exist.

        :param Reddit reddit: PRAW Reddit object.

        :returns: A `list[str]` of valid Subreddits.
        :rtype: `list[str]`
        """

        subreddit_prompt = (
            Style.BRIGHT
            + """
Enter Subreddit or a list of Subreddits (separated by a space) to scrape:

"""
            + Style.RESET_ALL
        )

        while True:
            try:
                search_for = str(input(subreddit_prompt))
                if not search_for:
                    raise ValueError
                return PrintSubs.print_subreddits(reddit, search_for)
            except ValueError:
                print(
                    Fore.RED + Style.BRIGHT + "No Subreddits were specified! Try again."
                )

    @staticmethod
    def _update_master(
        cat_i: int, master: Dict[str, Any], search_for: str, sub: str
    ) -> None:
        """
        Update Subreddit settings in master dictionary.

        :param int cat_i: The index corresponding to the category.
        :param dict[str, Any] master: A `dict[str, Any]` containing all scrape settings.
        :param str search_for: The number of results to return, or keywords to
            search for.
        :param str sub: The Subreddit name.
        """

        for sub_name in master.keys():
            if sub_name == sub:
                time_filter = "all" if cat_i in [2, 3, 5] else None

                settings = [short_cat[cat_i].lower(), search_for, time_filter]
                master[sub].append(settings)

    @staticmethod
    def _get_search(cat_i: int, master: Dict[str, Any], sub: str) -> None:
        """
        Get search settings.

        :param int cat_i: The index corresponding to the category.
        :param dict[str, Any] master: A `dict[str, Any]` containing all scrape settings.
        :param str sub: The Subreddit name.
        """

        while True:
            try:
                search_for = str(
                    input(
                        Style.BRIGHT
                        + "\nWhat would you like to search for in r/"
                        + sub
                        + "? "
                        + Style.RESET_ALL
                    )
                ).strip()
                if not search_for:
                    raise ValueError
                else:
                    GetInput._update_master(cat_i, master, search_for, sub)
                    break
            except ValueError:
                print(Fore.RED + Style.BRIGHT + "\nInvalid input! Try again.")

    @staticmethod
    def _get_n_results(cat_i: int, master: Dict[str, Any], sub: str) -> None:
        """
        Get number of results.

        :param int cat_i: The index corresponding to the category.
        :param dict[str, Any] master: A `dict[str, Any]` containing all scrape settings.
        :param str sub: The Subreddit name.
        """

        while True:
            try:
                search_for = input(
                    Style.BRIGHT
                    + "\nHow many results do you want to capture from r/"
                    + sub
                    + "? "
                    + Style.RESET_ALL
                ).strip()
                if search_for.isalpha() or not search_for:
                    raise ValueError
                else:
                    GetInput._update_master(cat_i, master, search_for, sub)
                    break
            except ValueError:
                print(Fore.RED + Style.BRIGHT + "\nInvalid input! Try again.")

    @staticmethod
    def get_settings(master: Dict[str, Any], subs: List[str]) -> None:
        """
        Select post category and the number of results returned from each Subreddit.

        :param dict[str, Any] master: A `dict[str, Any]` containing all scrape settings.
        :param list[str] subs: A `list[str]` of Subreddits.
        """

        for sub in subs:
            while True:
                try:
                    cat_i = int(
                        input(
                            (
                                Style.BRIGHT
                                + rf"""
Select a category to display for r/{sub}
-------------------
    0: Hot
    1: New
    2: Controversial
    3: Top
    4: Rising
    5: Search
-------------------
        """
                                + Style.RESET_ALL
                            )
                        )
                    )

                    if cat_i == 5:
                        print("\nSelected search")
                        GetInput._get_search(cat_i, master, sub)
                    else:
                        print(f"\nSelected category: {categories[cat_i]}")
                        GetInput._get_n_results(cat_i, master, sub)
                    break
                except (IndexError, ValueError):
                    print(Fore.RED + Style.BRIGHT + "\nNot an option! Try again.")


class ConfirmInput:
    """
    Methods for handling user confirmation.
    """

    @staticmethod
    def confirm_subreddits(subs: List[str], parser: ArgumentParser) -> List[str]:
        """
        Confirm Subreddits that were entered.

        :param list[str] subs: A `list[str]` of Subreddits.
        :param ArgumentParser parser: `ArgumentParser` instance.

        :returns: A `list[str]` of Subreddits.
        :rtype: `list[str]`
        """

        options = ["y", "n"]

        while True:
            try:
                confirm = input("\nConfirm selection? [Y/N] ").strip().lower()
                if confirm == options[0]:
                    return subs
                elif confirm not in options:
                    raise ValueError
                else:
                    print(Fore.RED + Style.BRIGHT + "\nExiting.\n")
                    parser.exit()
            except ValueError:
                print(Fore.RED + Style.BRIGHT + "\nNot an option! Try again.")


class RunBasic:
    """
    Run the basic Subreddit scraper.
    """

    @staticmethod
    def _create_settings(parser: ArgumentParser, reddit: Reddit) -> Dict[str, Any]:
        """
        Create settings for each user input.

        :param ArgumentParser parser: `ArgumentParser` instance.
        :param Reddit reddit: PRAW Reddit object.

        :returns: A `dict[str, Any]` containing all Subreddit scrape settings.
        :rtype: `dict[str, Any]`
        """

        subs = GetInput.get_subreddits(reddit)
        subs = ConfirmInput.confirm_subreddits(subs, parser)
        master = make_list_dict(subs)
        GetInput.get_settings(master, subs)

        return master

    @staticmethod
    def _print_confirm(master: Dict[str, Any]) -> Union[str, None]:
        """
        Print Subreddit scraping settings. Then write or quit scraper.

        :param dict[str, Any] master: A `dict[str, Any]` containing all scrape settings.

        :returns: A `str` indicating whether to continue scraping, or `None` if
            the user cancels the job.
        :rtype: `str | None`
        """

        PrintConfirm.print_settings(master)
        return confirm_settings()

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer("subreddit")
    def run(args: Namespace, parser: ArgumentParser, reddit: Reddit) -> Dict[str, Any]:
        """
        Run basic Subreddit scraper.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param ArgumentParser parser: `ArgumentParser` instance.
        :param Reddit reddit: PRAW Reddit object.

        :returns: A `dict[str, Any]` containing all Subreddit scrape settings.
        :rtype: `dict[str, Any]`
        """

        PRAWTitles.b_title()

        while True:
            master = RunBasic._create_settings(parser, reddit)

            confirm = RunBasic._print_confirm(master)
            if confirm == "y":
                break
            else:
                print(Fore.RED + Style.BRIGHT + "\nExiting.\n")
                parser.exit()

        GetSortWrite().gsw(args, reddit, master)

        return master
