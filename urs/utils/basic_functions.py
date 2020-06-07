#===============================================================================
#                      Basic Subreddit Scraper Functions
#===============================================================================
from colorama import init, Style
from . import global_vars, validation

### Automate sending reset sequences to turn off color changes at the end of 
### every print
init(autoreset = True)

### Global variables
categories = global_vars.categories
options = global_vars.options

s_t = global_vars.s_t

### Print valid and invalid Subreddits
def print_subreddits(parser, reddit, search_for):
    print("\nChecking if Subreddit(s) exist...")
    search_for = " ".join(search_for.split())
    sub_list = [subreddit for subreddit in search_for.split(" ")]
    found, not_found = validation.existence(reddit, sub_list, parser, s_t, s_t[0])
    if found:
        print("\nThe following Subreddits were found and will be scraped:")
        print("-" * 56)
        print(*found, sep = "\n")
    if not_found:
        print("\nThe following Subreddits were not found and will be skipped:")
        print("-" * 60)
        print(*not_found, sep = "\n")

    return found

### Select Subreddit(s) to scrape and check if they exist
def get_subreddits(parser, reddit):
    subreddit_prompt = """
Enter Subreddit or a list of Subreddits (separated by a space) to scrape:

"""

    while True:
        try:
            search_for = str(input(subreddit_prompt))
            if not search_for:
                raise ValueError

            return print_subreddits(parser, reddit, search_for)
        except ValueError:
            print("No Subreddits were specified! Try again.")

### Confirm Subreddits that were entered
def confirm_subreddits(found):
    while True:
        try:
            confirm = input("\nConfirm selection? [Y/N] ").strip().lower()
            if confirm == options[0]:
                subs = [sub for sub in found]
                return subs
            elif confirm not in options:
                raise ValueError
            else:
                break
        except ValueError:
            print("Not an option! Try again.")

### Get search settings 
def get_search(cat_i, s_master, sub):
    while True:
        try:
            search_for = str(input(
                "\nWhat would you like to search for in r/%s? " % 
                sub)).strip()
            if not search_for:
                raise ValueError
            else:
                for sub_n,values in s_master.items():
                    if sub_n == sub:
                        settings = [cat_i, search_for]
                        s_master[sub].append(settings)
                break
        except ValueError:
            print("Not an option! Try again.")

### Get number of results
def get_n_results(cat_i, s_master, sub):
    while True:
        try:
            submissions = input(
                "\nHow many results do you want to capture from r/%s? " % 
                sub).strip()
            if submissions.isalpha() or not submissions:
                raise ValueError
            else:
                for sub_n,values in s_master.items():
                    if sub_n == sub:
                        settings = [cat_i, int(submissions)]
                        s_master[sub].append(settings)
                break
        except ValueError:
            print("Not an option! Try again.")

### Select post category and the number of results returned from each Subreddit
def get_settings(s_master, subs):
    for sub in subs:
        while True:
            try:
                cat_i = int(input(("""
  Select a category to display for r/%s
  -------------------
    0: Hot
    1: New
    2: Controversial
    3: Top
    4: Rising
    5: Search
  -------------------
           """) % sub))

                if cat_i == 5:
                    print("\nSelected search option")
                    get_search(cat_i, s_master, sub)
                else:
                    print("\nSelected post category: %s" % categories[cat_i])
                    get_n_results(cat_i, s_master, sub)
                break
            except (IndexError, ValueError):
                print("Not an option! Try again.")

### Scrape again?
def another():
    while True:
        try:
            repeat = input("\nScrape again? [Y/N] ").strip().lower()
            if repeat not in options:
                raise ValueError
            else:
                return repeat
        except ValueError:
            print("Not an option! Try again.")