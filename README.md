# Universal Reddit Scraper

## URS 3.0 is done! This Readme will be updated with a new walkthrough for all the new features soon.

This is a universal Reddit scraper that can scrape Subreddits, Redditors, and comments on posts. 

Written in Python and utilizes the Reddit API ([`PRAW`](https://pypi.org/project/praw/)).

I provided a requirements.txt for a quick install of both `PRAW` and [`argparse`](https://pypi.org/project/argparse/). 

`pip install -r requirements.txt` 

You will also need your own Reddit account and API credentials. I have included a tutorial on how to do this below.

**NOTE:** `PRAW` is currently supported on Python 3.5+. This project was tested with Python 3.6.

## Table of Contents
 - [Scraping Reddit](#scraping-reddit)
 
    - [Scraping Subreddits](#scraping-subreddits)
    
    - [Scraping Redditors](#scraping-redditors)
    
    - [Scraping Post Comments](#scraping-post-comments)
    
 - [How to get Reddit API Credentials](#how-to-get-reddit-api-credentials)
 
 - [Some Linux Tips](#some-linux-tips)
 
 - [Walkthrough](#walkthrough)
 
     - [CLI scraper](#cli-scraper)
     
     - [Basic scraper](#basic-scraper)
    
 - [Releases](#releases)
 
# Scraping Reddit

## Scraping Subreddits

`./scraper.py -r SUBREDDIT [H|N|C|T|R|S] N_RESULTS_OR_KEYWORDS --FILE_FORMAT`

You can manually specify subreddits to scrape, specify which category of posts to scrape for each subreddit, and how many results are returned. I have also added a search option where you can search for keyword(s) within a subreddit and the scraper will get all posts that are returned from the search.

Options for which category of posts you want to scrape are as follows:
- Hot
- New
- Controversial
- Top
- Rising
- Search

***NOTE:*** If you choose to search for something within a subreddit, all the results are returned and you will not be able to specify how many results are returned.

Once you configure the settings for the scrape, the program will save the results to either a .csv or .json file.

The Subreddit scrape will include the following attributes of each post:

 - Title
 - Flair
 - Author
 - Created
 - Upvotes
 - Upvote Ratio
 - ID
 - Is Locked?
 - NSFW?
 - Is Spoiler?
 - Stickied?
 - URL
 - Comment Count
 - Text


The file names will follow this format: `"r-SUBREDDIT-POST_CATEGORY DATE.[FILE_FORMAT]"`

If you have searched for a specific keyword in a subreddit, file names are formatted as such: `"r-SUBREDDIT-Search-'KEYWORD' DATE.[FILE_FORMAT]"`.

## Scraping Redditors

`./scraper.py -u USER N_RESULTS --FILE_FORMAT`

You can also scrape Redditor profiles and specify how many results are returned.

Redditor scrapes will include the following attributes of each user:

- Name
- Fullname
- ID
- Date Created
- Comment Karma
- Link Karma
- Is Employee?
- Is Friend?
- Is Mod?
- Is Gold?
- Submissions
- Comments
- Hot
- New
- Controversial
- Top
- Upvoted (may be forbidden)
- Downvoted (may be forbidden)
- Gilded
- Gildings (may be forbidden)
- Hidden (may be forbidden)
- Saved (may be forbidden)

***NOTE:*** If you are not allowed to access a Redditor's lists, PRAW will raise a 403 HTTP Forbidden exception and the program will just append a "FORBIDDEN" underneath that section in the exported file.

***NOTE:*** The number of results returned will be applied to all attributes. I have not implemented code to allow users to specify different number of results returned for individual attributes.

The file names will follow this format: `"u-USERNAME DATE.[FILE_FORMAT]"`

## Scraping Post Comments

`./scraper.py -c URL N_RESULTS --FILE_FORMAT`

You can scrape post comments and specify how many top-level comments are returned. Each top-level comment will be followed by any second and third-level comments.

Comments scrapes will include the following attributes of each comment:

 - Author
 - Created
 - Upvotes
 - Text
 - Edited?
 - Is Submitter?
 - Stickied?

***NOTE:* These scrapes were designed to be used with JSON only. Exporting to CSV is not recommended.**

The file names will follow this format: `"c-POST_TITLE DATE.[FILE_FORMAT]"`

# How to get Reddit API Credentials

First, create your own Reddit account and then head over to [Reddit's apps page](https://old.reddit.com/prefs/apps).

Click "create app". Name your app and choose "script" for the type of app. In the redirect URL, type in "http://localhost:8080" since this is a personal use app. You can also add a description and an about URL. 

Once you create the app, you should see a string of 14 characters on the top left corner underneath "personal use script." That is your API ID. Further down you will see "secret" and a string of 27 characters; that is your API password. Save this information as it will be used in the program in order to use the Reddit API. You will also have to provide your app name, Reddit account username and password as well. 

This block of credentials is found on lines 15-19.

# Some Linux Tips

- You can further simplify running the program by making the program executable.
- `sudo chmod +x scraper.py`
- Make sure the shebang at the top of scraper.py matches the location in which your Python3.6 is installed. You can use `which python3.6` to check. The default shebang is `#!/usr/bin/python3.6`.
- Now you will only have to prepend `./` to run the scraper.
  - `./scraper.py ...`
- Troubleshooting
  - If you run the scraper with `./` and are greeted with a bad interpreter error, you will have to set the fileformat to UNIX. I did this using Vim.
    - ```
      vim scraper.py
      :set fileformat=unix
      :wq!
      ```

# Walkthrough

## NOTE: This walkthrough is for URS 2.0. URS 3.0 (beta) is now available. A full walkthrough for all new URS 3.0 features is coming soon!

First, you will have to provide your own Reddit credentials in this block of code.

![Reddit credentials](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/credentialblock.png)

**You have to provide valid credentials, otherwise the scraper will not work.**

## CLI scraper

Scraping using flags is much faster than the basic scraper.

Provide the scraper with the `-s` flag to indicate a new subreddit, the post category, and finally, depending on the category selected, either the number of results you would like returned or keyword(s) to search for during the scrape.

`-s SUBREDDIT CATEGORY RESULTS_OR_KEYWORDS`

Category options are as follows:

 - H,h - Hot
 - N,n - New
 - C,c - Controversial
 - T,t - Top
 - R,r - Rising  
 - S,s - Search
 
 You can scrape for multiple subreddits very quickly.
 
 ![Multiple flags](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/multiple_flags.png)
 
 The program will then print the title, check if the subreddit exists, then print out the scraping settings. If you enter subreddit(s) that do not exist, a list of the invalid subreddit(s) will be printed.
 
 ![Settings](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/subs_settings.png)
 
 After confirming the settings, the program will write CSV files to the directory in which you saved the program.
 
 ![Get, Sort, Write](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/get_sort_write.png)
 
 Refer to the help message for more usage examples. You can do this by using the `-h` flag.
 
## Basic scraper

If you do not want to use the command line flags, you can still use Universal Reddit Scraper 1.0 by providing the `-b` flag.

![B Flag](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/b_flag.png)

You can choose to just scrape a single subreddit, or enter a list of subreddits separated by a space.

![Enter subs](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/enter.png)

After entering the subreddit(s) you want to scrape, the program will check if the subreddit exists. It will separate the results from the check into a list of valid and invalid subreddits.

![Check subs](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/checksubs.png)

You will then have the option to choose the post category within the subreddit (Hot, New, Controversial, Top, Rising, Search). After choosing the category, you will also have the option to choose how many results you would like to be returned. Again, this only applies if you do not choose the Search option.

![Settings 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/settings1.png)

If you choose to search for keyword(s) within the subreddit, you will be greeted with these settings instead.

![Settings 2](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/settings2.png)

After you have configured all settings for each subreddit, you will be greeted with the following screen which displays the settings you have configured.

![Settings overview](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/overview.png)

When you confirm the settings, the program will write CSV files to the directory in which you saved the program and display the title of the post, the score (number of upvotes) of each post, post ID, post URL, comment count, date created, and additional text (body) of the post if there is any.

![Finish](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/finish.png)

![CSVs created](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/csvcreated.png)

# Releases
- **May 25, 2019** Universal Reddit Scraper 1.0. Does not include CLI support.
- **July 29, 2019:** Universal Reddit Scraper 2.0. Now includes CLI support!
- **December 28, 2019:** Universal Reddit Scraper 3.0. Now includes support for exporting to JSON, scraping Redditors as well as comments on posts.
