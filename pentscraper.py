#! usr/bin/env python3
"""
Created on Fri Mar  1 17:44:53 2019

Reddit scraper for pentesting information using the Reddit API

@author: Joseph Lai
"""
import praw
import csv
import datetime as dt

### Reddit API Credentials
c_id = "14_CHAR_HERE"               # Personal Use Script (14 char)
c_secret = "27_CHAR_HERE"           # Secret key (27 char)
u_a = "APP_NAME_HERE"               # App name
usrnm = "REDDIT_USERNAME_HERE"      # Reddit username
passwd = "REDDIT_PASSWORD_HERE"     # Reddit login password

### Subreddits to search
search = ["Pentesting","AskNetsec","HowToHack","netsec","hacking","netsecstudents","raspberry_pi",
          "homelab","Kalilinux","Hacking_Tutorials","pentest"]

### Subreddit categories
categories = ["Hot","New","Controversial","Top","Rising","Search"]

### Subreddit search selection 
def get_subreddit():
    ### Subreddit selection loop
    while True:
        try:
            index = int(input("""
  =======================================
  Scrape Pentesting Materials from Reddit
  =======================================                       
  
  Select a subreddit to search:
  -------------------------------------------------------------------
  0:  Pentesting -
      Penetration Testing and Security Discussion
  
  1:  AskNetsec -
      Ask NetSec Redditors anything
  
  2:  HowToHack - 
      Learn resources to expand your knowledge
  
  3:  netsec - 
      Community for technical news and discussion of 
      information security and closely related topics
  
  4:  hacking - 
      Constructive collaboration and learning 
      about exploits, industry standards, grey and white hat hacking,
      new hardware and software hacking technology, 
      sharing ideas and suggestions for small business and 
      personal security
  
  5:  netsecstudents - 
      Subreddit for students or anyone studying Network Security
  
  6:  raspberry_pi - 
      Subreddit for discussing the Raspberry Pi ARM computer 
      and all things related to it
  
  7:  homelab - 
      Subreddit where techies and sysadmin from everywhere 
      are welcome to share their labs, projects, builds, etc
  
  8:  Kalilinux - 
      Dedicated to Kali Linux, a complete rebuild of BackTrack Linux, 
      adhering completely to Debian development standards with an 
      all-new infrastructure that has been put in place
  
  9:  Hacking_Tutorials - 
      Subreddit where redditors can post various
      resources that discuss and teach the art of hacking
  
  10: pentest - 
      Like netsec, only specifically geared towards 
      news in Penetration Testing
  -------------------------------------------------------------------
                          """))
                
            print("\nSelected subreddit: r/%s" % search[index])
            break
        
        except IndexError:
            print("Not an option! Try again.")
            
        except ValueError:
            print("Not an option! Try again.")
    
    ### Post category loop        
    while True:
        try:
            cat_i = int(input("""
  Select a category to display
  ----------------------------
  0: Hot
  1: New
  2: Controversial
  3: Top
  4: Rising
  5: Search
  ----------------------------
            """))
            
            if cat_i == 5:
                print("\nSelected search option")
                search_for = str(input("What would you like to search for in r/%s? " % search[index]))
                print("---NOTE: Search will return all results of the search. Specifying the number of results will be disregarded.")
            else:
                print("\nSelected post category: %s" % categories[cat_i])
                search_for = None
            
            print("**Scraper captures posts from all time posts on the subreddit**")
            
            break
        
        except IndexError:
            print("Not an option! Try again.")
        
        except ValueError:
            print("Not an option! Try again.")
    
    ### Specify number of submissions to write to CSV loop        
    while True:
        try:
            submissions = int(input("How many results do you want to capture? "))
            break
            
        except ValueError:
            print("Not an option! Try again.")
     
    ### Handles printing correct statement if search category was selected
    if search_for != None:
        print(("\nScraping %s search results relating to '%s' in r/%s...") % (submissions,search_for,search[index]))
    else:
        print(("\nScraping %s submissions for %s posts in r/%s...") % (submissions,categories[cat_i],search[index]))
            
    return index,cat_i,search_for,submissions

### Get posts of subreddit
def get_posts(reddit,index,cat_i,search_for,submissions):
    print("Getting posts...")
    subreddit = reddit.subreddit(search[index])
    
    if cat_i == 0:
        collected = subreddit.hot(limit = submissions)
    elif cat_i == 1:
        collected = subreddit.new(limit = submissions)
    elif cat_i == 2:
        collected = subreddit.controversial(limit = submissions)
    elif cat_i == 3:
        collected = subreddit.top(limit = submissions)
    elif cat_i == 4:
        collected = subreddit.rising(limit = submissions)
    elif cat_i == 5:
        collected = subreddit.search("%s" % search_for)
            
    return collected
    
### Sort posts that were collected in the scrape and make a dictionary for CSV creation
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
def write_csv(index,cat_i,search_for,overview):
    print("Creating CSV...")
    
    fname = ""
    if cat_i == 5:
        fname = str(("r-%s-%s-'%s' %s.csv") % (search[index],categories[cat_i],search_for,dt.datetime.now().strftime("%m-%d-%Y")))
    else:
        fname = str(("r-%s-%s %s.csv") % (search[index],categories[cat_i],dt.datetime.now().strftime("%m-%d-%Y")))
        
    with open(fname, "w") as results:
        writer = csv.writer(results, delimiter = ",")
        writer.writerow(overview.keys())
        writer.writerows(zip(*overview.values()))

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
        index,cat_i,search_for,submissions = get_subreddit()                # Get subreddit name
        
        collected = get_posts(reddit,index,cat_i,search_for,submissions)    # Get posts in subreddit
        overview = sort_posts(collected)                                    # Sort posts from scrape, return dictionary
                             
        write_csv(index,cat_i,search_for,overview)                          # Create CSV
        
        print("\nCSV created.")
        
        try:
            repeat = str(input("\nScrape another subreddit? [Y/N] "))
        
            if repeat.lower().strip() == "n":
                print("\n----------Exiting----------")
                break
            
        except ValueError:
            print("Not an option! Try again.")
                
        except len(repeat) > 1:
            print("Not an option! Try again.")
            
if __name__ == "__main__":
    main()
