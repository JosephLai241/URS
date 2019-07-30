#!/usr/bin/python3.6
"""
Created on Sat Jul 20 23:45:06 2019

Reddit scraper using the Reddit API (PRAW)

@author: Joseph Lai
"""
import argparse
import sys
import praw
from prawcore import NotFound, PrawcoreException
import csv
import datetime as dt

### Get current date
date = dt.datetime.now().strftime("%m-%d-%Y")

### Reddit API Credentials
c_id = "14_CHAR_HERE"               # Personal Use Script (14 char)
c_secret = "27_CHAR_HERE"           # Secret key (27 char)
u_a = "APP_NAME_HERE"               # App name
usrnm = "REDDIT_USERNAME_HERE"      # Reddit username
passwd = "REDDIT_PASSWORD_HERE"     # Reddit login password

### Subreddit categories
categories = ["Hot","New","Controversial","Top","Rising","Search"]
short_cat = [cat[0] for cat in categories]

### Confirm or deny options
options = ["y","n"]

### Check if subreddit exists and catch PRAW exceptions
def existence(reddit,sub_list,parser):
    found = []
    not_found = []

    try:
        for sub in sub_list:
            try:
                reddit.subreddits.search_by_name(sub, exact = True)
                found.append(sub)
            except NotFound:
                not_found.append(sub)
    except PrawcoreException as error:
        print("\nERROR: %s" % error)
        print("Please recheck Reddit credentials.")
        if parser.parse_args().basic == False:
            print("\nExiting.")
            parser.exit()

    return found,not_found

### Print Reddit scraper title
def title():
    print("""==============================================================
    Reddit Scraper - Scrape Any Subreddit Of Your Choosing
==============================================================
    *Scraper captures posts from all time on the subreddit*""")

#-------------------------------------------------------------------------------
#                       Command-line Interface Functions
#-------------------------------------------------------------------------------
### Get args
def parse_args():
    parser = argparse.ArgumentParser(usage = "scraper.py [-h] [-b] [-s SUBREDDIT [H|N|C|T|R|S] RESULTS_OR_KEYWORDS]", \
                                    formatter_class = argparse.RawDescriptionHelpFormatter, \
                                    description = "Universal Reddit Scraper - Scrape any subreddit of your choosing", \
                                    epilog = """\
subreddit categories:
   H,h     selecting Hot category
   N,n     selecting New category
   C,c     selecting Controversial category
   T,t     selecting Top category
   R,r     selecting Rising category
   S,s     selecting Search category

EXAMPLES

    Get the first 10 posts in r/all in the Hot posts category:

        $ ./scraper.py -s all H 10

    Search for "United States of America" in r/worldnews:

        $ ./scraper.py -s worldnews S "United States of America"

    Like the non-CLI scraper, you can choose to scrape multiple subreddits at a time:

        $ ./scraper.py -s askreddit C 10 -s dankmemes H 15 -s worldnews S "United States of America"

    If you want the basic scraper without flags, you can use the -b flag:

        $ ./scraper.py -b

""")

    ### Parser scraper and basic flags
    parser.add_argument("-s","--sub", action="append", nargs=3, metavar="", help="specify subreddit to scrape")
    parser.add_argument("-b","--basic", action="store_true",help="initialize non-CLI Reddit scraper")

    ### Print help message if no arguments are present
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()
    return parser,args

### Create sub_list if args.basic is False
def create_sub_list(parser,args):
    sub_list = [sub[0] for sub in args.sub]
    return sub_list

### Check args and catching errors
def check_args(parser,args):
    sub_counter = 1
    for subs in args.sub:
        len_counter = 0
        try:
            if subs[1].isdigit() or len(subs[1]) > 1:
                raise ValueError
            for char in short_cat:
                if str(subs[1]).upper() == char:
                    if str(subs[1]).upper() != "S" and subs[2].isalpha():
                        raise ValueError
                    else:
                        sub_counter += 1
                    break
                elif len_counter == len(short_cat) - 1:
                    raise ValueError
                else:
                    len_counter += 1
        except ValueError:
            error = "| ERROR IN FLAG %s |" % sub_counter
            print()
            print("-"*len(error))
            print(error)
            print("-"*len(error))
            print()
            parser.print_help()
            parser.exit()
            break

### Check if the subreddits exist and list invalid subreddits if applicable
def confirm_subs(reddit,sub_list,parser):
    print("\nChecking if subreddit(s) exist...")
    found,not_found = existence(reddit,sub_list,parser)
    if not_found:
        print("\nThe following subreddits were not found and will be skipped:")
        print("-"*60)
        print(*not_found, sep = "\n")

    subs = [sub for sub in found]
    return subs

### Get CLI scraping settings
def get_cli_settings(args,master):
    for sub_n,values in master.items():
        for sub in args.sub:
            settings = [sub[1],sub[2]]
            if sub_n == sub[0]:
                master[sub_n].append(settings)
#-------------------------------------------------------------------------------

### Select subreddit(s) to scrape
def get_subreddits(reddit,parser):
    while True:
        try:
            search_for = str(input("""
Enter subreddit or a list of subreddits (separated by a space) to scrape:

"""))
            if not search_for:
                raise ValueError

            print("\nChecking if subreddit(s) exist...")
            search_for = " ".join(search_for.split())
            sub_list = [subreddit for subreddit in search_for.split(" ")]
            found,not_found = existence(reddit,sub_list,parser)
            if found:
                print("\nThe following subreddits were found and will be scraped:")
                print("-"*56)
                print(*found, sep = "\n")
            if not_found:
                print("\nThe following subreddits were not found and will be skipped:")
                print("-"*60)
                print(*not_found, sep = "\n")

            while True:
                try:
                    confirm = input("\nConfirm selection? [Y/N] ").strip().lower()
                    if confirm == "y":
                        subs = [sub for sub in found]
                        return subs
                    elif confirm == "n":
                        break
                    elif confirm not in options:
                        raise ValueError
                except ValueError:
                    print("Not an option! Try again.")
        except ValueError:
            print("No subreddits were specified! Try again.")
        except:
            pass

### Make master dictionary from subreddit list
def create_dict(subs):
    master = dict((sub,[]) for sub in subs)
    return master

### Select post category and the number of results returned from each subreddit to be scraped
def get_settings(subs,master):
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
                                for sub_n,values in master.items():
                                    if sub_n == sub:
                                        settings = [cat_i,search_for]
                                        master[sub].append(settings)
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
                                for sub_n,values in master.items():
                                    if sub_n == sub:
                                        settings = [cat_i,int(submissions)]
                                        master[sub].append(settings)
                                break
                        except ValueError:
                            print("Not an option! Try again.")
                break
            except IndexError:
                print("Not an option! Try again.")
            except ValueError:
                print("Not an option! Try again.")

### Print scraping details for each subreddit
def print_settings(master,args):
    print("\n------------------Current settings for each subreddit-------------------")
    print("\n{:<25}{:<17}{:<30}".format("Subreddit","Category","Number of results / Keyword(s)"))
    print("-"*72)
    for sub,settings in master.items():
        for each in settings:
            if args.basic == False:
                cat_i = short_cat.index(each[0].upper())
                specific = each[1]
            else:
                cat_i = each[0]
                specific = each[1]
            print("\n{:<25}{:<17}{:<30}".format(sub,categories[cat_i],specific))

    while True:
        try:
            confirm = input("\nConfirm options? [Y/N] ").strip().lower()
            if confirm == "y":
                return confirm
            elif confirm == "n":
                break
            elif confirm not in options:
                raise ValueError
        except ValueError:
            print("Not an option! Try again.")

### Get posts of subreddit. Return the dictionary "collected" when done
def get_posts(reddit,sub,cat_i,search_for,args):
    print("\nGetting posts for r/%s..." % sub)
    subreddit = reddit.subreddit(sub)

    if args.basic == False:
        if cat_i == short_cat[0]:
            collected = subreddit.hot(limit = int(search_for))
        elif cat_i == short_cat[1]:
            collected = subreddit.new(limit = int(search_for))
        elif cat_i == short_cat[2]:
            collected = subreddit.controversial(limit = int(search_for))
        elif cat_i == short_cat[3]:
            collected = subreddit.top(limit = int(search_for))
        elif cat_i == short_cat[4]:
            collected = subreddit.rising(limit = int(search_for))
        elif cat_i == short_cat[5]:
            collected = subreddit.search("%s" % search_for)
    else:
        if cat_i == 0:
            collected = subreddit.hot(limit = search_for)
        elif cat_i == 1:
            collected = subreddit.new(limit = search_for)
        elif cat_i == 2:
            collected = subreddit.controversial(limit = search_for)
        elif cat_i == 3:
            collected = subreddit.top(limit = search_for)
        elif cat_i == 4:
            collected = subreddit.rising(limit = search_for)
        elif cat_i == 5:
            collected = subreddit.search("%s" % search_for)

    return collected

### Sort collected dictionary
def sort_posts(collected):
    print("Sorting posts...")
    overview = {"Title" : [], \
                "Score" : [], \
                "ID" : [], \
                "URL" : [], \
                "Comment Count" : [], \
                "Created" : [], \
                "Text" : []}

    for post in collected:
        overview["Title"].append(post.title)
        overview["Score"].append(post.score)
        overview["ID"].append(post.id)
        overview["URL"].append(post.url)
        overview["Comment Count"].append(post.num_comments)
        overview["Created"].append(dt.datetime.fromtimestamp(post.created).strftime("%m-%d-%Y %H:%M:%S"))    # Convert UNIX time to readable format
        overview["Text"].append(post.selftext)

    return overview

### Write overview dictionary to CSV
def write_csv(sub,cat_i,search_for,overview,args):
    fname = ""
    if args.basic == False:
        if cat_i == short_cat[5]:
            fname = str(("%s-%s-'%s' %s.csv") % (sub,categories[5],search_for,date))
        else:
            fname = str(("%s-%s %s.csv") % (sub,categories[short_cat.index(cat_i)],date))
    else:
        if cat_i == 5:
            fname = str(("%s-%s-'%s' %s.csv") % (sub,categories[cat_i],search_for,date))
        else:
            fname = str(("%s-%s %s.csv") % (sub,categories[cat_i],date))

    with open(fname, "w") as results:
        writer = csv.writer(results, delimiter = ",")
        writer.writerow(overview.keys())
        writer.writerows(zip(*overview.values()))

    print("CSV file for r/%s created." % sub)

### Get, sort, then write posts to CSV
def get_sort_write(reddit,args,master):
    for sub,settings in master.items():
        for each in settings:
            if args.basic == False:
                cat_i = each[0].upper()
            else:
                cat_i = each[0]
            search_for = each[1]

            collected = get_posts(reddit,sub,cat_i,search_for,args)
            overview = sort_posts(collected)
            write_csv(sub,cat_i,search_for,overview,args)

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

def main():
    ### Reddit Login
    reddit = praw.Reddit(client_id = c_id, \
                         client_secret = c_secret, \
                         user_agent = u_a, \
                         username = usrnm, \
                         password = passwd)

    ### Parse args and initialize basic or CLI scraper
    parser,args = parse_args()
    title()
    if args.basic == False:
        ### CLI scraper
        sub_list = create_sub_list(parser,args)
        check_args(parser,args)
        subs = confirm_subs(reddit,sub_list,parser)

        master = create_dict(subs)
        get_cli_settings(args,master)
        confirm = print_settings(master,args)
        if confirm == "y":
            get_sort_write(reddit,args,master)
        else:
            print("\nExiting.")
    else:
        ### Basic scraper
        print("\nSelected basic scraper")
        while True:
            while True:
                subs = get_subreddits(reddit,parser)
                master = create_dict(subs)
                get_settings(subs,master)
                confirm = print_settings(master,args)
                if confirm == "y":
                    break
                else:
                    print("\nExiting.")
                    parser.exit()
            get_sort_write(reddit,args,master)
            repeat = another()
            if repeat == "n":
                print("\nExiting.")
                break

if __name__ == "__main__":
    main()
