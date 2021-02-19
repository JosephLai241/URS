"""
Basic Subreddit scraper
=======================
Defining the interface for the basic Subreddit scraper.
"""


from colorama import (
    init, 
    Fore, 
    Style
)

from urs.praw_scrapers.Subreddit import (
    GetSortWrite,
    PrintConfirm
)
from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Global import (
    categories,
    make_list_dict,
    options,
    s_t
)
from urs.utils.Logger import (
    LogExport,
    LogPRAWScraper
)
from urs.utils.Titles import PRAWTitles

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class PrintSubs():
    """
    Methods for printing found and invalid Subreddits.
    """

    ### Return a list of valid and invalid Subreddits.
    @staticmethod
    def _find_subs(parser, reddit, search_for):
        search_for = " ".join(search_for.split())
        sub_list = [subreddit for subreddit in search_for.split(" ")]
        subs, not_subs = Validation.existence(s_t[0], sub_list, parser, reddit, s_t)

        return subs, not_subs

    ### Print valid and invalid Subreddits.
    @staticmethod
    def print_subreddits(parser, reddit, search_for):
        print("\nChecking if Subreddit(s) exist...")
        subs, not_subs = PrintSubs._find_subs(parser, reddit, search_for)

        if subs:
            print(Fore.GREEN + Style.BRIGHT + "\nThe following Subreddits were found and will be scraped:")
            print(Fore.GREEN + Style.BRIGHT + "-" * 56)
            print(*subs, sep = "\n")
        if not_subs:
            print(Fore.YELLOW + Style.BRIGHT + "\nThe following Subreddits were not found and will be skipped:")
            print(Fore.YELLOW + Style.BRIGHT + "-" * 60)
            print(*not_subs, sep = "\n")

        if not subs:
            print(Fore.RED + Style.BRIGHT + "\nNo Subreddits to scrape!")
            print(Fore.RED + Style.BRIGHT + "\nExiting.\n")
            quit()

        return subs

class GetInput():
    """
    Methods for handling user input.
    """

    ### Enter Subreddit(s) to scrape and check if they exist.
    @staticmethod
    def get_subreddits(parser, reddit):
        subreddit_prompt = Style.BRIGHT + """
Enter Subreddit or a list of Subreddits (separated by a space) to scrape:

""" + Style.RESET_ALL

        while True:
            try:
                search_for = str(input(subreddit_prompt))
                if not search_for:
                    raise ValueError
                return PrintSubs.print_subreddits(parser, reddit, search_for)
            except ValueError:
                print(Fore.RED + Style.BRIGHT + "No Subreddits were specified! Try again.")

    ### Update Subreddit settings in master dictionary.
    @staticmethod
    def _update_master(cat_i, master, search_for, sub):
        user_search = search_for \
            if cat_i == 5 \
            else int(search_for)
        for sub_name in master.keys():
            if sub_name == sub:
                settings = [
                    cat_i, 
                    user_search,
                    "all"
                ]
                master[sub].append(settings)

    ### Get search settings.
    @staticmethod
    def _get_search(cat_i, master, sub):
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

    ### Get number of results.
    @staticmethod
    def _get_n_results(cat_i, master, sub):
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

    ### Select post category and the number of results returned from each Subreddit.
    @staticmethod
    def get_settings(master, subs):
        for sub in subs:
            while True:
                try:
                    cat_i = int(input((Style.BRIGHT + """
Select a category to display for r/%s
-------------------
    0: Hot
    1: New
    2: Controversial
    3: Top
    4: Rising
    5: Search
-------------------
        """ + Style.RESET_ALL) % sub))

                    if cat_i == 5:
                        print("\nSelected search")
                        GetInput._get_search(cat_i, master, sub)
                    else:
                        print("\nSelected category: %s" % categories[cat_i])
                        GetInput._get_n_results(cat_i, master, sub)
                    break
                except (IndexError, ValueError):
                    print(Fore.RED + Style.BRIGHT + "\nNot an option! Try again.")

class ConfirmInput():
    """
    Methods for handling user confirmation.
    """

    ### Confirm Subreddits that were entered.
    @staticmethod
    def confirm_subreddits(subs, parser):
        while True:
            try:
                confirm = input("\nConfirm selection? [Y/N] ").strip().lower()
                if confirm == options[0]:
                    subs = [sub for sub in subs]
                    return subs
                elif confirm not in options:
                    raise ValueError
                else:
                    print(Fore.RED + Style.BRIGHT + "\nExiting.\n")
                    parser.exit()
            except ValueError:
                print(Fore.RED + Style.BRIGHT + "\nNot an option! Try again.")    

    ### Scrape again?
    @staticmethod
    def another():
        while True:
            try:
                repeat = input("\nScrape again? [Y/N] ").strip().lower()
                if repeat not in options:
                    raise ValueError
                else:
                    return repeat
            except ValueError:
                print(Fore.RED + Style.BRIGHT + "\nNot an option! Try again.")

class RunBasic():
    """
    Run the basic Subreddit scraper.
    """

    ### Create settings for each user input.
    @staticmethod
    def _create_settings(parser, reddit):
        subs = GetInput.get_subreddits(parser, reddit)
        subs = ConfirmInput.confirm_subreddits(subs, parser)
        master = make_list_dict(subs)
        GetInput.get_settings(master, subs)

        return master

    ### Print Subreddit scraping settings. Then write or quit scraper.
    @staticmethod
    def _print_confirm(args, master):
        PrintConfirm().print_settings(args, master)
        return PrintConfirm().confirm_settings()

    ### Run basic Subreddit scraper.
    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer(s_t[0])
    def run(args, parser, reddit):
        PRAWTitles.b_title()
        
        while True:
            while True:                
                master = RunBasic._create_settings(parser, reddit)

                confirm = RunBasic._print_confirm(args, master)
                if confirm == options[0]:
                    break
                else:
                    print(Fore.RED + Style.BRIGHT + "\nExiting.\n")
                    parser.exit()
            
            GetSortWrite().gsw(args, reddit, master)
            
            repeat = ConfirmInput.another()
            if repeat == options[1]:
                print(Fore.RED + Style.BRIGHT + "\nExiting.\n")
                break
                