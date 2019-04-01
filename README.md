# Universal Reddit Scraper
Universal Reddit scraper using the Reddit API (PRAW).

Written in Python. Intended for use in a Linux terminal.

You will need to install the PRAW module in order for this program to work. `pip install praw` or `pip3 install praw` depending on your system. You will also need your own Reddit account and API credentials.

**NOTE:** PRAW currently only supports Python 2.7, 3.3, 3.4, 3.5, and 3.6.

This is a universal Reddit scraper where you can manually specify subreddits to scrape, specify which category of posts to scrape for each subreddit, and how many results are returned. I have also added a search option where you can also search for keyword(s) within a subreddit and the scraper will get all posts that are returned from the search.


Options for which category of posts to scrape for are as follows:
- Hot
- New
- Controversial
- Top
- Rising
- Search

*NOTE:* If you choose to search for something within a subreddit, all the results are returned and you will not be able to specify how many results are returned.

Once you configure the settings for the scrape, the program will write a .csv file to the same directory in which this scraper program is saved on your computer. The .csv file will include the Title, Score, ID, URL, Comment Count, Date Created, and the Text body of each post. 

The file names are formatted as such: "SUBREDDIT-POST_CATEGORY DATE.csv". If you have searched for a specific keyword in a subreddit, file names are formatted like so: "SUBREDDIT-Search-'KEYWORD' DATE.csv".

# How to get Reddit API Credentials

First, create your own Reddit account and then head over to https://old.reddit.com/prefs/apps.

Click "create app". Name your app and choose "script" for the type of app. In the redirect URL, type in "http://localhost:8080" since this is a personal use app. You can also add a description and an about URL. 

Once you create the app, you should see a string of 14 characters on the top left corner underneath "personal use script." That is your API ID. Further down you will see "secret" and a string of 27 characters; that is your API password. Save this information as it will be used in the program in order to use the Reddit API. You will also have to provide your app name, Reddit account username and password as well. 

This block of credentials is found on lines 14-18.

# ***Enjoy!***

# List of things I still have to add or change in this program
- As of now, users would have to start over if they decide they are not satisfied with their scrape settings. I might look into adding an option to either go back and redo the subreddit scrape settings or to completely start over. This way users will have options.

- I intended for this to be used in the terminal, specifically for Linux-based distros. Will look into a better way to print out the scraped results into the terminal instead of creating CSV files for each scrape. Or maybe I will add a "Display scrape results in terminal / Create CSV file / Both? [T/C/B] " option.

- I am still not exactly sure how to do PRAW exception handling, will have to look into that a bit more to catch invalid Reddit credentials, forbidden HTTP responses, etc.


