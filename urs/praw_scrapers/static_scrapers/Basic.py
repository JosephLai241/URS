"""
Basic Subreddit scraper
=======================
Defining the interface for the basic Subreddit scraper.
"""


import logging

from colorama import (
    Fore, 
    Style
)
from halo import Halo

from urs.praw_scrapers.static_scrapers.Subreddit import (
    GetSortWrite,
    PrintConfirm
)
from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Global import (
    categories,
    confirm_settings,
    make_list_dict,
    short_cat
)
from urs.utils.Logger import (
    LogError,
    LogExport,
    LogPRAWScraper
)
from urs.utils.Titles import (
    Errors,
    PRAWTitles
)

class PrintSubs():
    """
    Methods for printing found and invalid Subreddits.
    """

    @staticmethod
    def _find_subs(reddit, search_for):
        """
        Return a list of valid and invalid Subreddits.

        Calls a method from an external module:

            Validation.existence()

        Parameters
        ----------
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        search_for: str
            String denoting Subreddits to scrape for

        Returns
        -------
        subs: list
            List of valid Subreddits
        not_subs: list
            List of invalid Subreddits
        """

        search_for = " ".join(search_for.split())
        sub_list = [subreddit for subreddit in search_for.split(" ")]
        not_subs, subs = Validation.check_existence(sub_list, reddit, "subreddit")

        return not_subs, subs

    @staticmethod
    def print_subreddits(reddit, search_for):
        """
        Print valid and invalid Subreddits.

        Calls previously defined private method:

            PrintSubs._find_subs()

        Parameters
        ----------
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        search_for: str
            String denoting Subreddits to scrape for

        Returns
        -------
        subs: list
            List of valid Subreddits
        not_subs: list
            List of invalid Subreddits
        """

        check_subs_spinner = Halo(color = "white", text = "Validating Subreddit(s).")
        print()
        check_subs_spinner.start()
        not_subs, subs = PrintSubs._find_subs(reddit, search_for)
        check_subs_spinner.succeed("Finished Subreddit validation.")

        if subs:
            print(Fore.GREEN + Style.BRIGHT + "\nThe following Subreddits were found and will be scraped:")
            print(Fore.GREEN + Style.BRIGHT + "-" * 56)
            print(*subs, sep = "\n")
        if not_subs:
            print(Fore.YELLOW + Style.BRIGHT + "\nThe following Subreddits were not found and will be skipped:")
            print(Fore.YELLOW + Style.BRIGHT + "-" * 60)
            print(*not_subs, sep = "\n")

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

class GetInput():
    """
    Methods for handling user input.
    """

    @staticmethod
    def get_subreddits(reddit):
        """
        Enter Subreddit(s) to scrape and check if they exist.

        Calls previously defined public method:

            PrintSubs.print_subreddits()

        Parameters
        ----------
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        subs: list
            List of valid Subreddits
        """

        subreddit_prompt = Style.BRIGHT + """
Enter Subreddit or a list of Subreddits (separated by a space) to scrape:

""" + Style.RESET_ALL

        while True:
            try:
                search_for = str(input(subreddit_prompt))
                if not search_for:
                    raise ValueError
                return PrintSubs.print_subreddits(reddit, search_for)
            except ValueError:
                print(Fore.RED + Style.BRIGHT + "No Subreddits were specified! Try again.")

    @staticmethod
    def _update_master(cat_i, master, search_for, sub):
        """
        Update Subreddit settings in master dictionary.

        Parameters
        ----------
        cat_i: int
            Integer denoting the category index
        master: dict
            Dictionary denoting all scrape settings
        search_for: str
            String denoting n_results to return or keywords to search for 
        sub: str
            Subreddit name

        Returns
        -------
        None
        """

        for sub_name in master.keys():
            if sub_name == sub:
                time_filter = "all" \
                    if cat_i in [2, 3, 5] \
                    else None
                
                settings = [
                    short_cat[cat_i].lower(), 
                    search_for,
                    time_filter
                ]
                master[sub].append(settings)

    @staticmethod
    def _get_search(cat_i, master, sub):
        """
        Get search settings.

        Calls previously defined private method:

            GetInput._update_master()

        Parameters
        ----------
        cat_i: int
            Integer denoting the category index
        master: dict
            Dictionary denoting all scrape settings
        sub: str
            Subreddit name

        Returns
        -------
        None
        """

        while True:
            try:
                search_for = str(input(Style.BRIGHT + "\nWhat would you like to search for in r/" + sub + "? " + Style.RESET_ALL)).strip()
                if not search_for:
                    raise ValueError
                else:
                    GetInput._update_master(cat_i, master, search_for, sub)
                    break
            except ValueError:
                print(Fore.RED + Style.BRIGHT + "\nInvalid input! Try again.")

    @staticmethod
    def _get_n_results(cat_i, master, sub):
        """
        Get number of results.

        Calls previously defined private method:

            GetInput._update_master()

        Parameters
        ----------
        cat_i: int
            Integer denoting the category index
        master: dict
            Dictionary denoting all scrape settings
        sub: str
            Subreddit name

        Returns
        -------
        None
        """

        while True:
            try:
                search_for = input(Style.BRIGHT + "\nHow many results do you want to capture from r/" + sub + "? " + Style.RESET_ALL).strip()
                if search_for.isalpha() or not search_for:
                    raise ValueError
                else:
                    GetInput._update_master(cat_i, master, search_for, sub)
                    break
            except ValueError:
                print(Fore.RED + Style.BRIGHT + "\nInvalid input! Try again.")

    @staticmethod
    def get_settings(master, subs):
        """
        Select post category and the number of results returned from each Subreddit.

        Calls previously defined private methods:

            GetInput._get_search()
            GetInput._get_n_results()

        Parameters
        ----------
        master: dict
            Dictionary denoting all scrape settings
        subs: list
            List of Subreddits

        Returns
        -------
        None
        """

        for sub in subs:
            while True:
                try:
                    cat_i = int(input((Style.BRIGHT + fr"""
Select a category to display for r/{sub}
-------------------
    0: Hot
    1: New
    2: Controversial
    3: Top
    4: Rising
    5: Search
-------------------
        """ + Style.RESET_ALL)))

                    if cat_i == 5:
                        print("\nSelected search")
                        GetInput._get_search(cat_i, master, sub)
                    else:
                        print(f"\nSelected category: {categories[cat_i]}")
                        GetInput._get_n_results(cat_i, master, sub)
                    break
                except (IndexError, ValueError):
                    print(Fore.RED + Style.BRIGHT + "\nNot an option! Try again.")

class ConfirmInput():
    """
    Methods for handling user confirmation.
    """

    @staticmethod
    def confirm_subreddits(subs, parser):
        """
        Confirm Subreddits that were entered.

        Parameters
        ----------
        subs: list
            List of Subreddits
        parser: ArgumentParser
            argparse ArgumentParser object

        Returns
        -------
        subs: list
            List of Subreddits
        """

        options = [
            "y", 
            "n"
        ]

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

class RunBasic():
    """
    Run the basic Subreddit scraper.
    """

    @staticmethod
    def _create_settings(parser, reddit):
        """
        Create settings for each user input.

        Calls previously defined public methods:

            GetInput.get_settings()
            GetInput.get_subreddits()
            ConfirmInput.confirm_subreddits()
        
        Calls a public method from an external module:

            Global.make_list_dict()

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser object
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        master: dict
            Dictionary denoting all Subreddit scrape settings
        """

        subs = GetInput.get_subreddits(reddit)
        subs = ConfirmInput.confirm_subreddits(subs, parser)
        master = make_list_dict(subs)
        GetInput.get_settings(master, subs)

        return master

    @staticmethod
    def _print_confirm(args, master):
        """
        Print Subreddit scraping settings. Then write or quit scraper.

        Calls previously defined public methods:

            PrintConfirm().print_settings()
            Global().confirm_settings()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        master: dict
            Dictionary denoting all Subreddit scrape settings

        Returns
        -------
        master: dict
            Dictionary denoting all Subreddit scrape settings
        """

        PrintConfirm.print_settings(master)
        return confirm_settings()

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer("subreddit")
    def run(args, parser, reddit):
        """
        Run basic Subreddit scraper.

        Calls previously defined public and private methods:

            ConfirmInput.another()
            RunBasic._create_settings()
            RunBasic._print_confirm()

        Calls public methods from external modules:

            GetSortWrite().gsw()
            PRAWTitles.b_title()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        parser: ArgumentParser
            argparse ArgumentParser object
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
            
        Returns
        -------
        master: dict
            Dictionary containing all Subreddit scrape settings
        """

        PRAWTitles.b_title()
                    
        while True:                
            master = RunBasic._create_settings(parser, reddit)

            confirm = RunBasic._print_confirm(args, master)
            if confirm == "y":
                break
            else:
                print(Fore.RED + Style.BRIGHT + "\nExiting.\n")
                parser.exit()
        
        GetSortWrite().gsw(args, reddit, master)

        return master
