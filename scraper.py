#!/usr/bin/python3.6
"""
Created on Sat Jul 20 23:45:06 2019

Universal Reddit Scraper 3.0 - Reddit scraper using the Reddit API (PRAW)

@author: Joseph Lai
"""
import argparse
import sys
import praw
from prawcore import NotFound, PrawcoreException
import csv
import json
import datetime as dt

### Get current date
date = dt.datetime.now().strftime("%m-%d-%Y")

### Reddit API Credentials
c_id = "14_CHAR_HERE"               # Personal Use Script (14 char)
c_secret = "27_CHAR_HERE"           # Secret key (27 char)
u_a = "APP_NAME_HERE"               # App name
usrnm = "REDDIT_USERNAME_HERE"      # Reddit username
passwd = "REDDIT_PASSWORD_HERE"     # Reddit login password

### Scrape types
s_t = ["sub","user","comments"]

### Export options
eo = ["csv","json"]

### Subreddit categories
categories = ["Hot","New","Controversial","Top","Rising","Search"]
short_cat = [cat[0] for cat in categories]

### Confirm or deny options
options = ["y","n"]

#===============================================================================
#                                   Titles
#===============================================================================
### Print Reddit scraper title
def title():
    print(r"""
               __  ______  _____    _____  ____
              / / / / __ \/ ___/   |__  / / __ \
             / / / / /_/ /\__ \     /_ < / / / /
            / /_/ / _, _/___/ /   ___/ // /_/ /
            \____/_/ |_|/____/   /____(_)____/
            ====================================
        Scrape Subreddits, Redditors, and post comments
""")

### Print Subreddit scraper title
def r_title():
    print(r"""
       _____       __                  __    ___ __
      / ___/__  __/ /_  ________  ____/ /___/ (_) /______
      \__ \/ / / / __ \/ ___/ _ \/ __  / __  / / __/ ___/
     ___/ / /_/ / /_/ / /  /  __/ /_/ / /_/ / / /_(__  )
    /____/\__,_/_.___/_/   \___/\__,_/\__,_/_/\__/____/
""")

### Print Redditor scraper title
def u_title():
    print(r"""
        ____           __    ___ __
       / __ \___  ____/ /___/ (_) /_____  __________
      / /_/ / _ \/ __  / __  / / __/ __ \/ ___/ ___/
     / _, _/  __/ /_/ / /_/ / / /_/ /_/ / /  (__  )
    /_/ |_|\___/\__,_/\__,_/_/\__/\____/_/  /____/
""")

### Print comments scraper title
def c_title():
    print(r"""
       ______                                     __
      / ____/___  ____ ___  ____ ___  ___  ____  / /______
     / /   / __ \/ __ `__ \/ __ `__ \/ _ \/ __ \/ __/ ___/
    / /___/ /_/ / / / / / / / / / / /  __/ / / / /_(__  )
    \____/\____/_/ /_/ /_/_/ /_/ /_/\___/_/ /_/\__/____/
""")

### Print basic scraper title
def b_title():
    print(r"""
                __               _
               / /_  ____ ______(_)____
              / __ \/ __ `/ ___/ / ___/
             / /_/ / /_/ (__  ) / /__
            /_.___/\__,_/____/_/\___/
            ---------------------------
             *Only scrapes Subreddits*
""")

### Print error title
def e_title():
    print(r"""
                __________  ____  ____  ____
               / ____/ __ \/ __ \/ __ \/ __ \
              / __/ / /_/ / /_/ / / / / /_/ /
             / /___/ _, _/ _, _/ /_/ / _, _/
            /_____/_/ |_/_/ |_|\____/_/ |_|
            ---------------------------------
    Please recheck args or refer to help for usage examples.
""")

#===============================================================================
#                                 Validation
#===============================================================================
### Check if Subreddit(s) or Redditor(s) exist and catch PRAW exceptions
def existence(reddit,list,parser,s_t,l_type):
    found = []
    not_found = []
    try:
        if l_type == s_t[0]:
            for sub in list:
                try:
                    reddit.subreddits.search_by_name(sub, exact = True)
                    found.append(sub)
                except NotFound:
                    not_found.append(sub)
        elif l_type == s_t[1]:
            for user in list:
                try:
                    reddit.redditor(user).id
                    found.append(user)
                except NotFound:
                    not_found.append(user)
        elif l_type == s_t[2]:
            for post in list:
                try:
                    reddit.submission(url=post)
                    found.append(post)
                except praw.exceptions.ClientException:
                    not_found.append(post)
    except PrawcoreException as error:
        print("\nERROR: %s" % error)
        print("Please recheck Reddit credentials.")
        if parser.parse_args().basic == False:
            print("\nExiting.")
            parser.exit()

    return found,not_found

#===============================================================================
#                       Command-line Interface Functions
#===============================================================================
### Get args
def parse_args():
    parser = argparse.ArgumentParser(usage = "scraper.py [-h] [-r SUBREDDIT [H|N|C|T|R|S] RESULTS_OR_KEYWORDS] [-u USER RESULTS] [-c URL RESULTS] [-b] [--csv|--json]", \
                                    formatter_class = argparse.RawDescriptionHelpFormatter, \
                                    description = "Universal Reddit Scraper 3.0 - Scrape Subreddits, Redditors, or comments from posts", \
                                    epilog = r"""
subreddit categories:
   H,h     selecting Hot category
   N,n     selecting New category
   C,c     selecting Controversial category
   T,t     selecting Top category
   R,r     selecting Rising category
   S,s     selecting Search category

EXAMPLES

    Get the first 10 posts in r/all in the Hot category and export to JSON:

        $ ./scraper.py -r all h 10 --json

    Search for "United States of America" in r/worldnews and export to CSV:

        $ ./scraper.py -r worldnews s "United States of America" --csv

    Scraping 50 results from u/spez's Reddit account:

        $ ./scraper.py -u spez 50 --json

    Scraping 25 comments from this r/TIFU post:

        $ ./scraper.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 25 --csv

    You can choose to scrape multiple items at once:

        $ ./scraper.py -r askreddit h 15 -u spez 25 -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 50 --json

    You can also still use URS 1.0 (SUBREDDIT SCRAPING ONLY), but you cannot include this flag with any items besides export options:

        $ ./scraper.py -b --csv

""")

    ### Parser Subreddit, basic, Redditor, comments scraper, and skip confirmation flags
    scraper = parser.add_argument_group("Scraping options")
    scraper.add_argument("-r","--sub",action="append",nargs=3,metavar="",help="specify Subreddit to scrape")
    scraper.add_argument("-b","--basic",action="store_true",help="initialize non-CLI Subreddit scraper")
    scraper.add_argument("-u","--user",action="append",nargs=2,metavar="",help="specify Redditor profile to scrape")
    scraper.add_argument("-c","--comments",action="append",nargs=2,metavar="",help="specify the URL of the post to scrape comments")
    scraper.add_argument("-y",action="store_true",help="skip subreddit options confirmation and scrape immediately")

    ### Export to CSV or JSON flags
    expt = parser.add_mutually_exclusive_group(required=True)
    expt.add_argument("--csv",action="store_true",help="export to CSV")
    expt.add_argument("--json",action="store_true",help="export to JSON")

    ### Print help message if no arguments are present
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()
    return parser,args

### Create either Subreddit, Redditor, or posts list
def create_list(args,s_t,l_type):
    if l_type == s_t[0]:
        list = [sub[0] for sub in args.sub]
    elif l_type == s_t[1]:
        list = [user[0] for user in args.user]
    elif l_type == s_t[2]:
        list = [post[0] for post in args.comments]

    return list

### Check args and catching errors
def check_args(parser,args):
    try:
        if args.sub:
            for subs in args.sub:
                len_counter = 0
                if subs[1].upper() not in short_cat:
                    raise ValueError
                for char in short_cat:
                    if str(subs[1]).upper() == char:
                        if str(subs[1]).upper() != "S" and subs[2].isalpha():
                            raise ValueError
                        break
                    elif len_counter == len(short_cat) - 1:
                        raise ValueError
                    else:
                        len_counter += 1
        if args.user:
            for user in args.user:
                if user[1].isalpha():
                    raise ValueError
        if args.comments:
            for post in args.comments:
                if post[1].isalpha():
                    raise ValueError
    except ValueError:
        e_title()
        parser.exit()

### Check if the Subreddits exist and list invalid Subreddits if applicable
def confirm_subs(reddit,sub_list,parser):
    print("\nChecking if Subreddit(s) exist...")
    found,not_found = existence(reddit,sub_list,parser,s_t,s_t[0])
    if not_found:
        print("\nThe following Subreddits were not found and will be skipped:")
        print("-"*60)
        print(*not_found, sep = "\n")

    subs = [sub for sub in found]
    return subs

### Get CLI scraping settings for Subreddits, Redditors, and post comments
def get_cli_settings(reddit,args,master,s_t,s_type):
    if s_type == s_t[0]:
        for sub_n,values in master.items():
            for sub in args.sub:
                settings = [sub[1],sub[2]]
                if sub_n == sub[0]:
                    master[sub_n].append(settings)
    elif s_type == s_t[1]:
        for user_n,values in master.items():
            for user in args.user:
                master[user[0]] = user[1]
    elif s_type == s_t[2]:
        for com_n,values in master.items():
            for comments in args.comments:
                master[comments[0]] = comments[1]

#===============================================================================
#                      Basic Subreddit Scraper Functions
#===============================================================================
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

### Select post category and the number of results returned from each Subreddit to be scraped
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

#===============================================================================
#                       Subreddit Scraping Functions
#===============================================================================
### Make s_master dictionary from Subreddit list
def c_s_dict(subs):
    s_master = dict((sub,[]) for sub in subs)
    return s_master

### Print scraping details for each Subreddit
def print_settings(s_master,args):
    print("\n------------------Current settings for each Subreddit-------------------")
    print("\n{:<25}{:<17}{:<30}".format("Subreddit","Category","Number of results / Keyword(s)"))
    print("-"*72)
    for sub,settings in s_master.items():
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
            if confirm == options[0]:
                return confirm
            elif confirm == options[1]:
                break
            elif confirm not in options:
                raise ValueError
        except ValueError:
            print("Not an option! Try again.")

### Get Subreddit posts
def get_posts(reddit,sub,cat_i,search_for):
    subreddit = reddit.subreddit(sub)
    if cat_i == short_cat[5] or cat_i == 5:
        print(("\nSearching posts in r/%s for '%s'...") % (sub,search_for))
        collected = subreddit.search("%s" % search_for)
    else:
        print(("\nProcessing %s results from r/%s...") % (search_for,sub))
        if cat_i == short_cat[0] or cat_i == 0:
            collected = subreddit.hot(limit = int(search_for))
        elif cat_i == short_cat[1] or cat_i == 1:
            collected = subreddit.new(limit = int(search_for))
        elif cat_i == short_cat[2] or cat_i == 2:
            collected = subreddit.controversial(limit = int(search_for))
        elif cat_i == short_cat[3] or cat_i == 3:
            collected = subreddit.top(limit = int(search_for))
        elif cat_i == short_cat[4] or cat_i == 4:
            collected = subreddit.rising(limit = int(search_for))

    return collected

### Sort collected dictionary. Reformat dictionary if exporting to JSON
def sort_posts(args,collected):
    print("Sorting posts...")
    titles = ["Title","Flair","Author","Created","Upvotes","Upvote Ratio","ID",\
                "Edited?","Is Locked?","NSFW?","Is Spoiler?","Stickied?",\
                "URL","Comment Count","Text"]

    if args.csv:
        overview = dict((title,[]) for title in titles)
        for post in collected:
            overview["Title"].append(post.title)
            overview["Flair"].append(post.link_flair_text)
            overview["Author"].append(post.author.name)
            overview["Created"].append(dt.datetime.fromtimestamp(post.created).strftime("%m-%d-%Y %H:%M:%S"))    # Convert UNIX time to readable format
            overview["Upvotes"].append(post.score)
            overview["Upvote Ratio"].append(post.upvote_ratio)
            overview["ID"].append(post.id)
            overview["Edited?"].append(post.edited)
            overview["Is Locked?"].append(post.locked)
            overview["NSFW?"].append(post.over_18)
            overview["Is Spoiler?"].append(post.spoiler)
            overview["Stickied?"].append(post.stickied)
            overview["URL"].append(post.url)
            overview["Comment Count"].append(post.num_comments)
            overview["Text"].append(post.selftext)
    elif args.json:
        overview = dict()
        counter = 1
        for post in collected:
            e_p = [post.title,post.link_flair_text,post.author.name,\
                    dt.datetime.fromtimestamp(post.created).strftime("%m-%d-%Y %H:%M:%S"),\
                    post.score,post.upvote_ratio,post.id,post.edited,post.locked,\
                    post.over_18,post.spoiler,post.stickied,post.url,post.num_comments,post.selftext]
            overview["Post %s" % counter] = {title:value for title,value in zip(titles,e_p)}
            counter += 1

    return overview

### Get, sort, then write scraped Subreddit posts to CSV or JSON
def gsw_sub(reddit,args,s_master):
    for sub,settings in s_master.items():
        for each in settings:
            if args.basic == False:
                cat_i = each[0].upper()
            else:
                cat_i = each[0]
            search_for = each[1]

            collected = get_posts(reddit,sub,cat_i,search_for)
            overview = sort_posts(args,collected)
            fname = sub_fname(args,cat_i,search_for,sub)
            if args.csv:
                export(fname,overview,eo[0])
                csv = "\nCSV file for r/%s created." % sub
                print(csv)
                print("-"*(len(csv) - 1))
            elif args.json:
                export(fname,overview,eo[1])
                json = "\nJSON file for r/%s created." % sub
                print(json)
                print("-"*(len(json) - 1))

#===============================================================================
#                               Export Functions
#===============================================================================
### Determine file name format for Subreddit scraping
def sub_fname(args,cat_i,search_for,sub):
    fname = ""
    if args.sub:
        if cat_i == short_cat[5]:
            fname = str(("r-%s-%s-'%s' %s") % (sub,categories[5],search_for,date))
        else:
            fname = str(("r-%s-%s %s") % (sub,categories[short_cat.index(cat_i)],date))
    elif args.basic:
        if cat_i == 5:
            fname = str(("r-%s-%s-'%s' %s") % (sub,categories[cat_i],search_for,date))
        else:
            fname = str(("r-%s-%s %s") % (sub,categories[cat_i],date))

    return fname

### Determine file name format for Redditor or comments scraping
def fname(args,string):
    fname = ""
    if args.user:
        fname = str(("u-%s %s") % (string,date))
    elif args.comments:
        fname = str(("c-%s %s") % (string,date))

    return fname

### Write overview dictionary to CSV or JSON
def export(fname,overview,f_type):
    if f_type == eo[0]:
        with open("%s.csv" % fname, "w", encoding = "utf-8") as results:
            writer = csv.writer(results, delimiter = ",")
            writer.writerow(overview.keys())
            writer.writerows(zip(*overview.values()))
    elif f_type == eo[1]:
        with open("%s.json" % fname, "w", encoding = "utf-8") as results:
            json.dump(overview,results,indent = 4)

#===============================================================================
#                           User Scraping Functions
#===============================================================================
### Check if Redditor(s) exist and list Redditor(s) who are not found
def list_users(reddit,user_list,parser):
    print("\nChecking if Redditor(s) exist...")
    users,not_users = existence(reddit,user_list,parser,s_t,s_t[1])
    if not_users:
        print("\nThe following Redditors were not found and will be skipped:")
        print("-"*55)
        print(*not_users,sep = "\n")

    return users

### Make u_master dictionary from Redditor list
def c_u_dict(users):
    u_master = dict((user,None) for user in users)
    return u_master

### This class made my code so much cleaner man. It was created to reuse code where I had
### to pass different objects into numerous blocks of code. I never really messed
### around with classes too much before this, but I am so glad I did :')
class Listables():
    ### Initialize objects that will be used in class methods
    def __init__(self,user,overview,limit):
        self.user = user
        self.overview = overview
        self.limit = limit

        self.submissions = user.submissions.new(limit = limit)
        self.comments = user.comments.new(limit = limit)
        self.hot = user.hot(limit = limit)
        self.new = user.new(limit = limit)
        self.controversial = user.controversial(time_filter = "all", limit = limit)
        self.top = user.top(time_filter = "all", limit = limit)
        self.gilded = user.gilded(limit = limit)
        self.upvoted = user.upvoted(limit = limit)
        self.downvoted = user.downvoted(limit = limit)
        self.gildings = user.gildings(limit = limit)
        self.hidden = user.hidden(limit = limit)
        self.saved = user.saved(limit = limit)

        self.mutt_names = ["Hot","New","Controversial","Top","Gilded"]
        self.mutts = [self.hot,self.new,self.controversial,self.top,self.gilded]

        self.access_names = ["Upvoted","Downvoted","Gildings","Hidden","Saved"]
        self.access = [self.upvoted,self.downvoted,self.gildings,self.hidden,self.saved]

    ### Sort Redditor submissions
    def sort_submissions(self):
        for submission in self.submissions:
            post = ["Title: %s" % submission.title, "Body: %s" % submission.selftext]
            self.overview["Submissions"].append(post)

    ### Sort Redditor comments
    def sort_comments(self):
        for comment in self.comments:
            self.overview["Comments"].append(comment.body)

    ### Sort hot, new, controversial, top, and gilded Redditor posts. The ListGenerator
    ### returns a mix of submissions and comments, so handling each differently is
    ### necessary
    def sort_mutts(self):
        for cat,obj in zip(self.mutt_names,self.mutts):
            for post in obj:
                if isinstance(post,praw.models.Submission):
                    l = ["Title: %s" % post.title, "Body: %s" % post.selftext]
                    self.overview["%s" % cat.capitalize()].append(l)
                elif isinstance(post,praw.models.Comment):
                    l = "Comment: %s" % post.body
                    self.overview["%s" % cat.capitalize()].append(l)

    ### Sort upvoted, downvoted, gildings, hidden, and saved Redditor posts. These
    ### lists tend to raise a 403 HTTP Forbidden exception, so naturally exception
    ### handling is necessary
    def sort_access(self):
        for cat,obj in zip(self.access_names,self.access):
            try:
                for post in obj:
                    if isinstance(post,praw.models.Submission):
                        l = ["Title: %s" % post.title, "Body: %s" % post.selftext]
                        self.overview["%s (may be forbidden)" % cat.capitalize()].append(l)
                    elif isinstance(post,praw.models.Comment):
                        l = "Comment: %s" % post.body
                        self.overview["%s (may be forbidden)" % cat.capitalize()].append(l)
            except PrawcoreException as error:
                print(("\nACCESS TO %s OBJECTS FORBIDDEN: %s. SKIPPING.") % (cat.upper(),error))
                self.overview["%s (may be forbidden)" % cat.capitalize()].append("FORBIDDEN")

### Get and sort Redditor information
def gs_user(reddit,user,limit):
    print("\nGetting information for u/%s..." % user)
    user = reddit.redditor(user)

    print(("\nProcessing %s results from u/%s's profile...") % (limit,user))
    titles = ["Name","Fullname","ID","Date Created","Comment Karma","Link Karma", \
                "Is Employee?","Is Friend?","Is Mod?","Is Gold?","Submissions","Comments", \
                "Hot","New","Controversial","Top","Upvoted (may be forbidden)","Downvoted (may be forbidden)", \
                "Gilded","Gildings (may be forbidden)","Hidden (may be forbidden)","Saved (may be forbidden)"]

    overview = dict((title,[]) for title in titles)
    overview["Name"].append(user.name)
    overview["Fullname"].append(user.fullname)
    overview["ID"].append(user.id)
    overview["Date Created"].append(dt.datetime.fromtimestamp(user.created_utc).strftime("%m-%d-%Y %H:%M:%S"))
    overview["Comment Karma"].append(user.comment_karma)
    overview["Link Karma"].append(user.link_karma)
    overview["Is Employee?"].append(user.is_employee)
    overview["Is Friend?"].append(user.is_friend)
    overview["Is Mod?"].append(user.is_mod)
    overview["Is Gold?"].append(user.is_gold)
    listable = Listables(user,overview,limit = int(limit))
    listable.sort_submissions()
    listable.sort_comments()
    listable.sort_mutts()
    listable.sort_access()

    return overview

### Get, sort, then write scraped Redditor information to CSV or JSON
def w_user(reddit,users,u_master,args):
    for user,limit in u_master.items():
         overview = gs_user(reddit,user,limit)
         f_name = fname(args,user)
         if args.csv:
             export(f_name,overview,eo[0])
             csv = "\nCSV file for u/%s created." % user
             print(csv)
             print("-"*(len(csv) - 1))
         elif args.json:
             export(f_name,overview,eo[1])
             json = "\nJSON file for u/%s created." % user
             print(json)
             print("-"*(len(json) - 1))

#===============================================================================
#                        Post Comments Scraping Functions
#===============================================================================
### Check if posts exist and list posts that are not found
def list_posts(reddit,post_list,parser):
    print("\nChecking if post(s) exist...")
    posts,not_posts = existence(reddit,post_list,parser,s_t,s_t[2])
    if not_posts:
        print("\nThe following posts were not found and will be skipped:")
        print("-"*55)
        print(*not_posts,sep = "\n")

    return posts

### Make c_master dictionary from posts list
def c_c_dict(posts):
    c_master = dict((post,None) for post in posts)
    return c_master

### Add list of dictionary of comments attributes to use when sorting comments
def add_comment(titles,comment):
    c_set = dict((title,None) for title in titles)
    c_set[titles[0]] = comment.author.name
    c_set[titles[1]] = dt.datetime.fromtimestamp(comment.created_utc).strftime("%m-%d-%Y %H:%M:%S")
    c_set[titles[2]] = comment.score
    c_set[titles[3]] = comment.body
    c_set[titles[4]] = comment.edited
    c_set[titles[5]] = comment.is_submitter
    c_set[titles[6]] = comment.stickied

    return [c_set]

### Sort comments. Exit loop if replace_more() has timed out
def s_comments(all,titles,submission):
    for comment in submission.comments.list():
        cpid = comment.parent_id.split("_",1)[1]
        if cpid == submission.id:
            add = add_comment(titles,comment)
            all[comment.id] = [add]
        elif cpid in all.keys():
            append = add_comment(titles,comment)
            all[cpid].append({comment.id:append})
        else:
            for parent_id,more_c in all.items():
                for d in more_c:
                    if isinstance(d,dict):
                        try:
                            sub_set = add_comment(titles,comment)
                            if cpid in d.keys():
                                d[cpid].append({comment.id:sub_set})
                            else:
                                d[comment.id] = [sub_set]
                        except AttributeError:
                            print("\nLoad more comments timed out.")
                            return

### Get and sort comments from posts
def gs_comments(reddit,post,limit):
    submission = reddit.submission(url=post)
    print(("\nProcessing %s comments from Reddit post '%s'...") % (limit,submission.title))
    titles = ["Author","Created","Upvotes","Text","Edited?","Is Submitter?","Stickied?"]
    submission.comments.replace_more(limit=None)

    all = dict()
    s_comments(all,titles,submission)
    cut = {key: all[key] for key in list(all)[:int(limit)]}
    return cut

### Get, sort, then write scraped comments to CSV or JSON
def w_comments(reddit,post_list,c_master,args):
    for post,limit in c_master.items():
        title = reddit.submission(url=post).title
        overview = gs_comments(reddit,post,limit)
        f_name = fname(args,title)
        if args.csv:
            export(f_name,overview,eo[0])
            csv = "\nCSV file for '%s' comments created." % title
            print(csv)
            print("-"*(len(csv) - 1))
        elif args.json:
            export(f_name,overview,eo[1])
            json = "\nJSON file for '%s' comments created." % title
            print(json)
            print("-"*(len(json) - 1))

#===============================================================================
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
                         password = passwd)    # Connect to reddit

    ### Parse and check args, and initialize Subreddit, Redditor, post comments,
    ### and/or basic Subreddit scraper
    parser,args = parse_args()
    check_args(parser,args)
    title()
    if args.sub:
        ### CLI scraper
        r_title()
        sub_list = create_list(args,s_t,s_t[0])
        subs = confirm_subs(reddit,sub_list,parser)

        s_master = c_s_dict(subs)
        get_cli_settings(reddit,args,s_master,s_t,s_t[0])
        if args.y:
            gsw_sub(reddit,args,s_master)
        else:
            confirm = print_settings(s_master,args)
            if confirm == options[0]:
                gsw_sub(reddit,args,s_master)
            else:
                print("\nCancelling.")
    if args.user:
        ### Redditor scraper
        u_title()
        user_list = create_list(args,s_t,s_t[1])
        users = list_users(reddit,user_list,parser)
        u_master = c_u_dict(users)
        get_cli_settings(reddit,args,u_master,s_t,s_t[1])
        w_user(reddit,users,u_master,args)
    if args.comments:
        ### Post comments scraper
        c_title()
        post_list = create_list(args,s_t,s_t[2])
        posts = list_posts(reddit,post_list,parser)
        c_master = c_c_dict(posts)
        get_cli_settings(reddit,args,c_master,s_t,s_t[2])
        w_comments(reddit,post_list,c_master,args)
    elif args.basic:
        ### Basic Subreddit scraper
        b_title()
        while True:
            while True:
                subs = get_subreddits(reddit,parser)
                s_master = c_s_dict(subs)
                get_settings(subs,s_master)
                confirm = print_settings(s_master,args)
                if confirm == options[0]:
                    break
                else:
                    print("\nExiting.")
                    parser.exit()
            gsw_sub(reddit,args,s_master)
            repeat = another()
            if repeat == options[1]:
                print("\nExiting.")
                break

if __name__ == "__main__":
    main()
