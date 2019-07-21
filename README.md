# Universal Reddit Scraper
Universal Reddit scraper using the Reddit API ([PRAW](https://pypi.org/project/praw/)).

Written in Python.

**I previously said that I would make a new repo for the CLI version of this scraper. As I progressed in creating a CLI for the scraper, I realized I would like to integrate the normal scraper so that users can just use a flag to call the non-CLI scraper (the current version), so having two repos would be redundant. That being said, I have deleted the other repo and am going to replace the current scraper.py file with one that supports CLI, add an extra section in the walkthrough for CLI usage, and add a changelog section.**

I provided a requirements.txt for a quick install of both the PRAW and argparse modules. 

`pip install -r requirements.txt` 

You will also need your own Reddit account and API credentials.

**NOTE:** PRAW currently only supports Python 2.7, 3.3, 3.4, 3.5, and 3.6. This project was written in Python 3 and tested with Python 3.6.

This is a universal Reddit scraper where you can manually specify subreddits to scrape, specify which category of posts to scrape for each subreddit, and how many results are returned. I have also added a search option where you can search for keyword(s) within a subreddit and the scraper will get all posts that are returned from the search.

Options for which category of posts to scrape for are as follows:
- Hot
- New
- Controversial
- Top
- Rising
- Search

*NOTE:* If you choose to search for something within a subreddit, all the results are returned and you will not be able to specify how many results are returned.

Once you configure the settings for the scrape, the program will write a .csv file to the same directory in which this scraper program is saved on your computer. 

The .csv file will scrape the Title, Score, ID, URL, Comment Count, Date Created, and the Text body of each post. 

The file names are formatted as such: "SUBREDDIT-POST_CATEGORY DATE.csv". If you have searched for a specific keyword in a subreddit, file names are formatted like so: "SUBREDDIT-Search-'KEYWORD' DATE.csv".

# How to get Reddit API Credentials

First, create your own Reddit account and then head over to [Reddit's apps page](https://old.reddit.com/prefs/apps).

Click "create app". Name your app and choose "script" for the type of app. In the redirect URL, type in "http://localhost:8080" since this is a personal use app. You can also add a description and an about URL. 

Once you create the app, you should see a string of 14 characters on the top left corner underneath "personal use script." That is your API ID. Further down you will see "secret" and a string of 27 characters; that is your API password. Save this information as it will be used in the program in order to use the Reddit API. You will also have to provide your app name, Reddit account username and password as well. 

This block of credentials is found on lines 15-19.

# Some Linux Tips

- **Alias**
  - If you do not want to type out the path to your Python3.6 every time you run the program, you can create an alias by adding a line in your .bashrc.
  - `alias python3.6='/usr/bin/python3.6'`
  - I named the alias "python3.6" and set the path to where my Python3.6 is located. Your Python3.6 may be located elsewhere. Use `which python3.6` to get the path to where it is installed on your machine.
  - Now you will only have to prepend `python3.6` to run the scraper.
    - `python3.6 scraper.py ...`

- **`./`**
  - You can even further simplify running the program by making the program executable.
  - `sudo chmod +x scraper.py`
  - Make sure the shebang at the top of scraper.py matches the location in which your Python3.6 is installed. Again, you can use `which python3.6` to check. The default shebang is `#!/usr/bin/python3.6`.
  - Now you will only have to prepend `./` to run the scraper.
    - `./scraper.py ...`
  - Troubleshooting
    - If you run the scraper with `./` and are greeted with a bad interpreter error, you will have to set the fileformat to UNIX. I did this using Vim.
      - `vim scraper.py`
      - `:set fileformat=unix`
      - `:wq!`

# Screenshots / Walkthrough

First, you will have to provide your own Reddit credentials in this block of code.

![Reddit credentials](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/credentialblock.png)

**You have to provide valid credentials, otherwise the scraper will not work.**

## CLI scraper

Telling the program to scrape by providing flags is much faster than the basic method.

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
 
 The program will then print the title, check if the subreddit exists, then print out the scraping settings. If you enter subreddit(s) that do not exist, a list of the non-existent subreddit(s) will be printed.
 
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

# Changelog
- **April 2, 2019:** Universal Reddit Scraper 1.0 finished. Does not include CLI support.
- **July 20, 2019:** Universal Reddit Scraper 2.0. Includes CLI support!

# List of things I still have to add or change in this program
- As of now, users would have to start over if they decide they are not satisfied with their scrape settings. I might look into adding an option to either go back and redo the subreddit scrape settings or to completely start over. This way users will have options.

- I am still not exactly sure how to do PRAW exception handling, will have to look into that a bit more to catch invalid Reddit credentials, forbidden HTTP responses, etc.

- Considering adding an option where users can specify the data fields they would like in the CSV files instead of the current default fields.
