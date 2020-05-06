#===============================================================================
#                      Basic Subreddit Scraper Functions
#===============================================================================
from .. import global_vars

### Global variables
categories = global_vars.categories
options = global_vars.options

### Select Subreddit(s) to scrape and check if they exist
def get_subreddits(reddit,parser):
    while True:
        try:
            search_for = str(input("""
Enter Subreddit or a list of Subreddits (separated by a space) to scrape:

"""))
            if not search_for:
                raise ValueError

            print("\nChecking if Subreddit(s) exist...")
            search_for = " ".join(search_for.split())
            sub_list = [subreddit for subreddit in search_for.split(" ")]
            found,not_found = existence(reddit,sub_list,parser,s_t,s_t[0])
            if found:
                print("\nThe following Subreddits were found and will be scraped:")
                print("-"*56)
                print(*found, sep = "\n")
            if not_found:
                print("\nThe following Subreddits were not found and will be skipped:")
                print("-"*60)
                print(*not_found, sep = "\n")

            while True:
                try:
                    confirm = input("\nConfirm selection? [Y/N] ").strip().lower()
                    if confirm == options[0]:
                        subs = [sub for sub in found]
                        return subs
                    elif confirm == options[1]:
                        break
                    elif confirm not in options:
                        raise ValueError
                except ValueError:
                    print("Not an option! Try again.")
        except ValueError:
            print("No Subreddits were specified! Try again.")
        except:
            pass

### Select post category and the number of results returned from each Subreddit
def get_settings(subs,s_master):
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
                    while True:
                        try:
                            search_for = str(input("\nWhat would you like to search for in r/%s? " % sub)).strip()
                            if not search_for:
                                raise ValueError
                            else:
                                for sub_n,values in s_master.items():
                                    if sub_n == sub:
                                        settings = [cat_i,search_for]
                                        s_master[sub].append(settings)
                                break
                        except ValueError:
                            print("Not an option! Try again.")
                else:
                    print("\nSelected post category: %s" % categories[cat_i])
                    while True:
                        try:
                            submissions = input("\nHow many results do you want to capture from r/%s? " % sub).strip()
                            if submissions.isalpha() or not submissions:
                                raise ValueError
                            else:
                                for sub_n,values in s_master.items():
                                    if sub_n == sub:
                                        settings = [cat_i,int(submissions)]
                                        s_master[sub].append(settings)
                                break
                        except ValueError:
                            print("Not an option! Try again.")
                break
            except IndexError:
                print("Not an option! Try again.")
            except ValueError:
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