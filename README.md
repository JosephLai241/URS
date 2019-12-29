# Universal Reddit Scraper 3.0

## **12/28/19: Comments scraping functionality currently has some issues. Redditor scraping and exporting to JSON are ready to go.**

This is a universal Reddit scraper that can scrape Subreddits, Redditors, and comments on posts. 

Written in Python and utilizes the Reddit API ([`PRAW`](https://pypi.org/project/praw/)).

I provided a requirements.txt for a quick install of both `PRAW` and [`argparse`](https://pypi.org/project/argparse/). 

`pip install -r requirements.txt` 

You will also need your own Reddit account and API credentials. I have included a tutorial on how to do this below.

**NOTE:** `PRAW` is currently supported on Python 3.5+. This project was tested with Python 3.6.

## Table of Contents
 - [Scraping Reddit](#scraping-reddit)
 
    - [Subreddits](#subreddits)
    
    - [Redditors](#redditors)
    
    - [Post Comments](#post-comments)
    
 - [How to get Reddit API Credentials](#how-to-get-reddit-api-credentials)
 
 - [Some Linux Tips](#some-linux-tips)
 
 - [Walkthrough](#walkthrough)
 
     - [CLI Scrapers](#cli-scrapers)
     
       - [Subreddit Scraper](#subreddit-scraper)
       
       - [Redditor Scraper](#redditor-scraper)
       
       - [Comments Scraper](#comments-scraper)
     
     - [Basic Scraper](#basic-scraper)
    
 - [Releases](#releases)
 
# Scraping Reddit

## Subreddits

`$ ./scraper.py -r SUBREDDIT [H|N|C|T|R|S] N_RESULTS_OR_KEYWORDS --FILE_FORMAT`

You can specify Subreddits, which category of posts, and how many results are returned from each scrape. I have also added a search option where you can search for keyword(s) within a Subreddit and the scraper will get all posts that are returned from the search.

These are the post category options:
- Hot
- New
- Controversial
- Top
- Rising
- Search

***NOTE:*** All results are returned if you search for something within a Subreddit, so you will not be able to specify how many results to keep.

Once you configure the settings for the scrape, the program will save the results to either a .csv or .json file.

The Subreddit scrape will include the following submission attributes:

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

If you have searched for keywords in a Subreddit, file names are formatted as such: `"r-SUBREDDIT-Search-'KEYWORDS' DATE.[FILE_FORMAT]"`

## Redditors

`$ ./scraper.py -u USER N_RESULTS --FILE_FORMAT`

You can also scrape Redditor profiles and specify how many results are returned.

Redditor scrapes will include the following Redditor attributes:

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

## Post Comments

`$ ./scraper.py -c URL N_RESULTS --FILE_FORMAT`

**These scrapes were designed to be used with JSON only. Exporting to CSV is not recommended.

*Comment scraping functionality currently has some issues and may be different once I figure out a better solution. Section coming soon!*

# How to get Reddit API Credentials

First, create your own Reddit account and then head over to [Reddit's apps page](https://old.reddit.com/prefs/apps).

Click "create app". Name your app and choose "script" for the type of app. In the redirect URL, type in "http://localhost:8080" since this is a personal use app. You can also add a description and an about URL. 

Once you create the app, you should see a string of 14 characters on the top left corner underneath "personal use script." That is your API ID. Further down you will see "secret" and a string of 27 characters; that is your API password. Save this information as it will be used in the program in order to use the Reddit API. You will also have to provide your app name, Reddit account username and password as well. 

This block of credentials is found on lines 23-27.

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

First, you will have to provide your own Reddit credentials in this block of code.

![Reddit credentials](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/credentialblock.png)

**You have to provide valid credentials, otherwise the scraper will not work.**

All exported files will be saved to the current working directory.

## CLI scrapers

If you do not want to read the rest of this walkthrough, or forget the args, you can always consult the built-in help message by using `-h` or `--help`.

![Help Message 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/Help_1.png)

----------------------------------------------------------------------------------------------------------------------------

### Subreddit scraper

Scraping Subreddits using flags is much faster than the [basic scraper](#basic-scraper).

Use the `-r` flag to indicate a Subreddit, the post category, and finally, depending on the category selected, either the number of results returned or keyword(s) to search for during the scrape.

Category options are as follows:

 - H,h - Hot
 - N,n - New
 - C,c - Controversial
 - T,t - Top
 - R,r - Rising  
 - S,s - Search
 
Scraping 10 r/AskReddit posts in the Hot category and export to JSON:
 
![Subreddit Scraping 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/r_1.png)
 
The program will then display the type of scrape, check if the Subreddit(s) exist, and display the settings for each Subreddit. It will display a list of invalid Subreddits, if applicable. You can also include `-y` in your args if you want to skip this confirmation screen and immediately scrape.
 
![Subreddit Scraping 2](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/r_2.png)

**JSON Sample:**

![JSON Sample](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/r_json.png)

**CSV Sample:**

![CSV Sample](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/r_csv.png)
 
---------------------------------------------------------------------------------------------------------------------------- 

### Redditor Scraper
 
Use the `-u` flag to indicate a Redditor and the number of results returned. The program will then display the type of scrape and check if the Redditor(s) exist. It will display a list of invalid Redditors, if applicable.

I recommend exporting Redditor scrapes to JSON because the format is much nicer to read, but the current CSV format may change once URS 3.0 is finalized. I chose to export to CSV for demonstration purposes.
 
Scraping 5 results for each of u/spez's user attributes and export to CSV:
 
![Redditor Scraping 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/u_1.png)
 
There are a couple user lists that are typically restricted and will raise an 403 HTTP Forbidden exception. If you are forbidden from accessing a list, the program will display its name and append "FORBIDDEN" to that section in the export file.
 
![Redditor Scraping 2](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/u_2.png)
 
**JSON Sample:**
 
![Redditor JSON](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/u_json.png)
 
**CSV Sample:**
 
![Redditor CSV](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/u_csv.png)
 
----------------------------------------------------------------------------------------------------------------------------
 
### Comments Scraper
 
*Functionality is under construction. Coming soon!*
 
## Basic Scraper

If you do not want to use the command line flags, you can still use Universal Reddit Scraper 1.0 by providing the `-b` flag.

![B Flag](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/b_flag.png)

You can choose to just scrape a single Subreddit, or enter a list of Subreddits separated by a space.

![Enter subs](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/enter.png)

After entering the Subreddit(s) you want to scrape, the program will check if the Subreddit exists. It will separate the results from the check into a list of valid and invalid Subreddits.

![Check subs](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/checksubs.png)

You will then have the option to choose the post category within the Subreddit (Hot, New, Controversial, Top, Rising, Search). After choosing the category, you will also have the option to choose how many results you would like to be returned. Again, this only applies if you do not choose the Search option.

![Settings 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/settings1.png)

If you choose to search for keyword(s) within the Subreddit, you will be greeted with these settings instead.

![Settings 2](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/settings2.png)

After you have configured all settings for each Subreddit, you will be greeted with the following screen which displays the settings you have configured.

![Settings overview](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/overview.png)

When you confirm the settings, the program will write CSV files to the directory in which you saved the program and display the title of the post, the score (number of upvotes) of each post, post ID, post URL, comment count, date created, and additional text (body) of the post if there is any.

![Finish](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/finish.png)

![CSVs created](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/csvcreated.png)

# Releases
- **May 25, 2019** Universal Reddit Scraper 1.0. Does not include CLI support.
- **July 29, 2019:** Universal Reddit Scraper 2.0. Now includes CLI support!
- **December 28, 2019:** Universal Reddit Scraper 3.0 (beta). 
  - New features include:
    - Exporting to JSON
    - Scraping Redditors
  - Comments scraping functionality is still under construction.
