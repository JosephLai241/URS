#===============================================================================
#                      Basic Subreddit Scraper Functions
#===============================================================================
from colorama import init, Style
from . import Global, Subreddit, Titles, validation

### Automate sending reset sequences to turn off color changes at the end of 
### every print
init(autoreset = True)

### Global variables
options = Global.options

class PrintSubs():
    """
    Print found and invalid Subreddits.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self.s_t = Global.s_t

    ### Return a list of valid and invalid Subreddits.
    def find_subs(self, parser, reddit, search_for):
        search_for = " ".join(search_for.split())
        sub_list = [subreddit for subreddit in search_for.split(" ")]
        found, not_found = validation.existence(reddit, sub_list, parser, \
            self.s_t, self.s_t[0])

        return found, not_found

    ### Print valid and invalid Subreddits.
    def print_subreddits(self, parser, reddit, search_for):
        print("\nChecking if Subreddit(s) exist...")
        found, not_found = self.find_subs(parser, reddit, search_for)
        if found:
            print("\nThe following Subreddits were found and will be scraped:")
            print("-" * 56)
            print(*found, sep = "\n")
        if not_found:
            print("\nThe following Subreddits were not found and will be skipped:")
            print("-" * 60)
            print(*not_found, sep = "\n")

        return found

class GetInput():
    """
    Functions for handling user input.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self.categories = Global.categories

    ### Enter Subreddit(s) to scrape and check if they exist.
    def get_subreddits(self, parser, reddit):
        subreddit_prompt = Style.BRIGHT + """
Enter Subreddit or a list of Subreddits (separated by a space) to scrape:

""" + Style.RESET_ALL

        while True:
            try:
                search_for = str(input(subreddit_prompt))
                if not search_for:
                    raise ValueError
                return PrintSubs().print_subreddits(parser, reddit, search_for)
            except ValueError:
                print("No Subreddits were specified! Try again.")

    ### Update Subreddit settings in master dictionary.
    def update_master(self, cat_i, master, search_for, sub):
        user_search = search_for if cat_i == 5 else int(search_for)
        for sub_n, _ in master.items():
            if sub_n == sub:
                settings = [cat_i, user_search]
                master[sub].append(settings)

    ### Get search settings.
    def get_search(self, cat_i, master, sub):
        while True:
            try:
                search_for = str(input(
                    Style.BRIGHT + "\nWhat would you like to search for in r/" + 
                    sub + "? " + Style.RESET_ALL)).strip()
                if not search_for:
                    raise ValueError
                else:
                    self.update_master(cat_i, master, search_for, sub)
                    break
            except ValueError:
                print("Not an option! Try again.")

    ### Get number of results.
    def get_n_results(self, cat_i, master, sub):
        while True:
            try:
                search_for = input(
                    Style.BRIGHT + "\nHow many results do you want to capture from r/" + 
                    sub + "? " + Style.RESET_ALL).strip()
                if search_for.isalpha() or not search_for:
                    raise ValueError
                else:
                    self.update_master(cat_i, master, search_for, sub)
                    break
            except ValueError:
                print("Not an option! Try again.")

    ### Select post category and the number of results returned from each Subreddit.
    def get_settings(self, master, subs):
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
                        self.get_search(cat_i, master, sub)
                    else:
                        print("\nSelected category: %s" % categories[cat_i])
                        self.get_n_results(cat_i, master, sub)
                    break
                except (IndexError, ValueError):
                    print("Not an option! Try again.")

class ConfirmInput():
    """
    Functions for handling user confirmation.
    """

    ### Confirm Subreddits that were entered.
    def confirm_subreddits(self, found, parser):
        while True:
            try:
                confirm = input("\nConfirm selection? [Y/N] ").strip().lower()
                if confirm == options[0]:
                    subs = [sub for sub in found]
                    return subs
                elif confirm not in options:
                    raise ValueError
                else:
                    print(Style.BRIGHT + "\nExiting.")
                    parser.exit()
            except ValueError:
                print("Not an option! Try again.")    

    ### Scrape again?
    def another(self):
        while True:
            try:
                repeat = input("\nScrape again? [Y/N] ").strip().lower()
                if repeat not in options:
                    raise ValueError
                else:
                    return repeat
            except ValueError:
                print("Not an option! Try again.")

class RunBasic():
    """
    Run the basic Subreddit scraper.
    """

    ### Create settings for each user input.
    def create_settings(self, parser, reddit):
        found = GetInput().get_subreddits(parser, reddit)
        subs = ConfirmInput().confirm_subreddits(found, parser)
        master = Global.make_list_dict(subs)
        GetInput().get_settings(master, subs)

        return master

    ### Print Subreddit scraping settings. Then write or quit scraper.
    def print_confirm(self, args, master):
        Subreddit.PrintConfirm().print_settings(args, master)
        return Subreddit.PrintConfirm().confirm_settings()

    ### Run basic Subreddit scraper.
    def run(self, args, parser, reddit):
        Titles.Titles().b_title()
        
        while True:
            while True:                
                master = self.create_settings(parser, reddit)

                confirm = self.print_confirm(args, master)
                if confirm == options[0]:
                    break
                else:
                    print(Style.BRIGHT + "\nExiting.")
                    parser.exit()
            
            Subreddit.GetSortWrite().gsw(args, reddit, master)
            
            repeat = ConfirmInput().another()
            if repeat == options[1]:
                print(Style.BRIGHT + "\nExiting.")
                break
