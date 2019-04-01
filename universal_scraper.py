#! usr/bin/env python3
"""
Created on Fri Mar  1 17:44:53 2019

Reddit scraper using the Reddit API (PRAW)

@author: Joseph Lai
"""
import praw
from prawcore import NotFound
import csv
import datetime as dt

### Reddit API Credentials
c_id = "14_CHAR_HERE"               # Personal Use Script (14 char)
c_secret = "27_CHAR_HERE"           # Secret key (27 char)
u_a = "APP_NAME_HERE"               # App name
usrnm = "REDDIT_USERNAME_HERE"      # Reddit username
passwd = "REDDIT_PASSWORD_HERE"     # Reddit login password

### Subreddit categories
categories = ["Hot","New","Controversial","Top","Rising","Search"]

### Check if subreddit exists
def existence(reddit,sub_list):
    found = []
    not_found = []
    
    for sub in sub_list:
        try:
            reddit.subreddits.search_by_name(sub, exact = True)
            found.append(sub)
        except NotFound:
            not_found.append(sub)
        
    return found,not_found

### Select subreddit(s) to scrape
def get_subreddits(reddit):
    while True:
        try:        
            search_for = str(input("""
  ========================================================================
           Reddit Scraper - Scrape Any Subreddit Of Your Choosing
  ========================================================================                       
         **Scraper captures posts from all time on the subreddit**

Enter subreddit or a list of subreddits (separated by a space) to scrape:

"""))
            
            print("\nChecking existence of subreddits...")        
            
            search_for = " ".join(search_for.split())                
            sub_list = [subreddit for subreddit in search_for.split(" ")]
            found,not_found = existence(reddit,sub_list)
            
            if found:
                print("\nThe following subreddits were found and will be searched in:")
                print("-"*60)
                print(*found, sep = "\n")
            
            if not_found:
                print("\nThe following subreddits were not found and will be skipped:")
                print("-"*60)
                print(*not_found, sep = "\n")
                 
            while True:                
                try:
                    confirm = input("\nConfirm selection? [Y/N] ")
                    if confirm.lower().strip() == "y":
                        subs = [sub for sub in found]
                        return subs
                    
                    elif confirm.lower().strip() == "n":
                        break                 
                    
                    elif confirm.isdigit() or len(confirm) > 1:
                        raise ValueError

                except ValueError:
                    print("\nNot an option!")
    
        except:
            pass   

### Make dictionary from master list
def create_dict(subs):
    master = dict((sub,[]) for sub in subs)

    return master

### Select post category and the number of results returned from each subreddit to be scraped
def get_settings(subs,master):
    for sub,values in master.items():    
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

                    search_for = str(input("\nWhat would you like to search for in r/%s? " % sub))
                    
                    master[sub].append(cat_i)
                    master[sub].append(search_for)

                else:
                    print("\nSelected post category: %s" % categories[cat_i])
                    
                    while True:                        
                        try:                            
                            submissions = input(("\nHow many results do you want to capture from r/%s? ") % sub)
                            if submissions.isalpha():
                                raise ValueError
                            else:                            
                                master[sub].append(cat_i)
                                master[sub].append(int(submissions))
                                break

                        except ValueError:
                            print("\nNot an option! Try again.")    

                break
            
            except IndexError:
                print("\nNot an option! Try again.")
            
            except ValueError:
                print("\nNot an option! Try again.")

### Print scraping details for each sub
def print_settings(master):
    print("\n------------------Current settings for each subreddit-------------------")    
    print("\n{:<25}{:<17}{:<30}".format("Subreddit","Category","Number of results / Keyword(s)"))
    print("-"*72)    
    for sub,settings in master.items():
        cat_i = settings[0]
        specific = settings[1]
        
        print("\n{:<25}{:<17}{:<30}".format(sub,categories[cat_i],specific))

    confirm = str(input("\nConfirm options? [Y/N] "))
    option = confirm.lower().strip()

    return option

### Get posts of subreddit. Return the dictionary "overview" when donezo
def get_posts(reddit,sub,cat_i,search_for):
    print("\nGetting posts for r/%s..." % sub)
    subreddit = reddit.subreddit(sub)
    
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

### Sort overview dictionary
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
def write_csv(sub,cat_i,search_for,overview):
    fname = ""
    if cat_i == 5:
        fname = str(("%s-%s-'%s' %s.csv") % (sub,categories[cat_i],search_for,dt.datetime.now().strftime("%m-%d-%Y")))
    else:
        fname = str(("%s-%s %s.csv") % (sub,categories[cat_i],dt.datetime.now().strftime("%m-%d-%Y")))
        
    with open(fname, "w") as results:
        writer = csv.writer(results, delimiter = ",")
        writer.writerow(overview.keys())
        writer.writerows(zip(*overview.values()))

    print("CSV file for r/%s created." % sub)

def main():
    ### Login loop    
    while True:
    	try:
            reddit = praw.Reddit(client_id = c_id, \
                             	client_secret = c_secret, \
                             	user_agent = u_a, \
                             	username = usrnm, \
                             	password = passwd)    # Connect to reddit
            break

    	except praw.exceptions.APIException:    # Catch Reddit API error. REVIEW PARAMS
    		print("Unable to connect to server. Try again.")
    	
    	except praw.exceptions.ClientException:    # Catch client login error
    		print("Unable to log in. Try again.")

    ### Scraping loop
    while True:
        while True:
            subs = get_subreddits(reddit)
            master = create_dict(subs)
            get_settings(subs,master)       
            confirm = print_settings(master)
            
            if confirm == "y":
                break

        for sub,settings in master.items():        
            cat_i = settings[0]
            search_for = settings[1]

            collected = get_posts(reddit,sub,cat_i,search_for)
            overview = sort_posts(collected)
            write_csv(sub,cat_i,search_for,overview)     

        def another():
            while True:
                try:
                    repeat = input("\nScrape again? [Y/N] ")
                    if repeat.isdigit() or len(repeat) > 1:
                        raise ValueError

                    else:
                        return str(repeat)
            
                except ValueError:
                    print("Not an option! Try again.")
                        
                except len(repeat) > 1:
                    print("Not an option! Try again.")

        redo = another()
        if redo == "n":
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
