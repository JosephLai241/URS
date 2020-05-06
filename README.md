# Universal Reddit Scraper

This is a universal Reddit scraper that can scrape Subreddits, Redditors, and comments on posts. 

Written in Python and utilizes the Reddit API ([`PRAW`](https://pypi.org/project/praw/)).

I provided a requirements.txt for a quick install of both `PRAW` and [`argparse`](https://pypi.org/project/argparse/). 

`pip install -r requirements.txt` 

You will also need your own Reddit account and API credentials. I have included a tutorial on how to do this below.

***NOTE:*** `PRAW` is currently supported on Python 3.5+. This project was tested with Python 3.6.

## Table of Contents
 - [Scraping Reddit](#scraping-reddit)
    - [Table of All Subreddit, Redditor, and Post Comments Attributes](#a-table-of-all-subreddit-redditor-and-post-comments-attributes)
    - [Subreddits](#subreddits)
    - [Redditors](#redditors)
    - [Post Comments](#post-comments)
 - [How to get Reddit API Credentials](#how-to-get-reddit-api-credentials)
 - [Walkthrough](#walkthrough)
     - [2-Factor Authentication](#2-factor-authentication)
     - [CLI Scrapers](#cli-scrapers)
       - [Subreddit Scraper](#subreddit-scraper)
       - [Redditor Scraper](#redditor-scraper)
       - [Comments Scraper](#comments-scraper)
     - [Basic Scraper](#basic-scraper)
 - [Some Linux Tips](#some-linux-tips)
 - [Contributing](#contributing)
 - [Contributors](#contributors)
 - [Releases](#releases)
 
# Scraping Reddit

Scrape speeds will be determined by the speed of your internet connection.

All exported files will be saved to the current working directory.

## A Table of All Subreddit, Redditor, and Post Comments Attributes

These attributes will be included in each scrape.

Subreddits | Redditors | Post Comments
---------- | --------- | -------------
Title | Name | Parent ID
Flair | Fullname | Comment ID
Date Created | ID | Author
Upvotes | Date Created | Date Created
Upvote Ratio | Comment Karma | Upvotes
ID | Link Karma | Text
Is Locked? | Is Employee? | Edited? 
NSFW? | Is Friend? | Is Submitter?
Is Spoiler? | Is Mod? | Stickied?
Stickied? | Is Gold? | 
URL | Submissions* | 
Comment Count | Comments*
Text | Hot* | 
&nbsp; | New* | 
&nbsp; | Controversial* | 
&nbsp; | Top* | 
&nbsp; | Upvoted* (may be forbidden) | 
&nbsp; | Downvoted* (may be forbidden) | 
&nbsp; | Gilded* | 
&nbsp; | Gildings* (may be forbidden) | 
&nbsp; | Hidden* (may be forbidden) | 
&nbsp; | Saved* (may be forbidden) | 

\* Includes additional attributes; see [Redditors](#redditors) section for more information

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

The file names will follow this format: `"r-SUBREDDIT-POST_CATEGORY DATE.[FILE_FORMAT]"`

If you have searched for keywords in a Subreddit, file names are formatted as such: `"r-SUBREDDIT-Search-'KEYWORDS' DATE.[FILE_FORMAT]"`

## Redditors

`$ ./scraper.py -u USER N_RESULTS --FILE_FORMAT`

**[Currently for JSON ONLY.](https://github.com/JosephLai241/Universal-Reddit-Scraper/issues/3)**

You can also scrape Redditor profiles and specify how many results are returned.

Of these Redditor attributes, the following will include additional attributes:

Submissions, Hot, New, Controversial, Top, Upvoted, Downvoted, Gilded, Gildings, Hidden, and Saved | Comments
-------------------------------------------------------------------------------------------------- | --------
Title | Date Created
Date Created | Score
Upvotes | Text
Upvote Ratio | Parent ID
ID | Link ID
NSFW? | Edited?
Text | Stickied?
&nbsp; | Replying to (title of post or comment)
&nbsp; | In Subreddit (Subreddit name)
 
***NOTE:*** If you are not allowed to access a Redditor's lists, PRAW will raise a 403 HTTP Forbidden exception and the program will just append a "FORBIDDEN" underneath that section in the exported file.

***NOTE:*** The number of results returned will be applied to all attributes. I have not implemented code to allow users to specify different number of results returned for individual attributes.

The file names will follow this format: `"u-USERNAME DATE.[FILE_FORMAT]"`

## Post Comments

`$ ./scraper.py -c URL N_RESULTS --FILE_FORMAT`

**These scrapes were designed to be used with JSON only. Exporting to CSV is not recommended, but it will still work.**

You can also scrape comments from posts and specify the number of results returned.

Comments scraping can either return structured JSON data down to third-level comment replies, or you can simply return a raw list of all comments with no structure.

To return a raw list of all comments, specify `0` results to be returned from the scrape.

When exporting raw comments, all top-level comments are listed first, followed by second-level, third-level, etc.

***NOTE:*** You cannot specify the number of raw comments returned. The program with scrape all comments from the post, which may take a while depending on the post's popularity.

The file names will follow this format: `"c-POST_TITLE DATE.[FILE_FORMAT]"`

# How to get Reddit API Credentials

First, create your own Reddit account and then head over to [Reddit's apps page](https://old.reddit.com/prefs/apps).

Click "are you a developer? create an app...". 

![Create an app](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/Reddit_API/Creds_1.png)

Name your app, choose "script" for the type of app, and type "http://localhost:8080" in the redirect URI field since this is a personal use app. You can also add a description and an about URL. 

![Enter Stuff In Boxes](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/Reddit_API/Creds_2.png)

Click "create app", then "edit" to reveal more information.

![Click Edit](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/Reddit_API/Creds_3.png)

You should see a string of 14 characters on the top left corner underneath "personal use script." That is your API ID. Further down you will see "secret" and a string of 27 characters; that is your API password. Save this information as it will be used in the program in order to use the Reddit API.

![All Info](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/Reddit_API/Creds_4_edit.png)

You will also have to provide your app name, Reddit account username and password in the block of credentials found on lines 27-31.

# Walkthrough

First, you will have to provide your own Reddit credentials in this block of code.

![Reddit credentials](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/Creds.png)

**You have to provide valid credentials, otherwise the scraper will not work.**

## 2-Factor Authentication

If you choose to use 2FA with your Reddit account, enter your password followed by a colon and then your 2FA token in the `passwd` field on line 22. For example, if your password is "p4ssw0rd" and your 2FA token is "123456", you will enter "p4ssw0rd:123456" in the `passwd` field.

**2FA is NOT recommended for use with this program.** This is because PRAW will raise an OAuthException after one hour, prompting you to refresh your 2FA token and re-enter your credentials. Additionally, this means your 2FA token would be stored alongside your Reddit username and password, which would defeat the purpose of enabling 2FA in the first place. See [here](https://praw.readthedocs.io/en/latest/getting_started/authentication.html#two-factor-authentication) for more information.

## CLI scrapers

If you do not want to read the rest of this walkthrough, or forget the args, you can always consult the built-in help message by using `-h` or `--help`.

![Help Message](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/help.png)

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
 
![Subreddit Scraping 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/r-1.png)
 
The program will then display the type of scrape, check if the Subreddit(s) exist, and display the settings for each Subreddit. It will display a list of invalid Subreddits, if applicable. You can also include `-y` in your args if you want to skip this confirmation screen and immediately scrape.
 
![Subreddit Scraping 2](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/r_2.png)

**JSON Sample:**

![JSON Sample](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/r-json.png)

**CSV Sample:**

![CSV Sample](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/r-csv.png)
 
---------------------------------------------------------------------------------------------------------------------------- 

### Redditor Scraper
 
Use the `-u` flag to indicate a Redditor and the number of results returned. The program will then display the type of scrape and check if the Redditor(s) exist. It will display a list of invalid Redditors, if applicable.

**This is currently for JSON ONLY. There is a [CSV export bug](https://github.com/JosephLai241/Universal-Reddit-Scraper/issues/3) that needs squashing.**
 
Scraping 5 results for each of u/spez's user attributes and export to JSON:
 
![Redditor Scraping 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/u-1.png)
 
There are a couple user lists that are typically restricted and will raise an 403 HTTP Forbidden exception. If you are forbidden from accessing a list, the program will display its name and append "FORBIDDEN" to that section in the export file.
 
![Redditor Scraping 2](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/u-2.png)
 
**JSON Sample:**
 
![Redditor JSON](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/u-json.png)
 
----------------------------------------------------------------------------------------------------------------------------
 
### Comments Scraper

Use the `-c` flag to indicate a post and the number of comments returned. The program will then display the type of scrape and check if the post(s) exist. It will display a list of invalid posts, if applicable.

**I have designed this functionality to work best with JSON and strongly recommend this export option, however you will still be able to get your results if you choose to export to CSV instead.**

There are two ways you can scrape comments with this program. You can indicate a number to return a structured JSON file that includes down to third-level replies. Or you can specify `0` comments to be returned and the program will return an unstructured JSON file of all comments.

**Structured Scrape**

Scraping 10 comments from [this Reddit post](https://www.reddit.com/r/ProgrammerHumor/comments/9ozauu/a_more_accurate_representation_of_what_happened/) and export to JSON:
 
![Comments Scraping 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/c_1.png)

![Comments Scraping 2](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/c_2.png)

**Structured JSON Sample:**

![Structured JSON](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/c_json.png)

**Unstructured Scrape**

When exporting raw comments, all top-level comments are listed first, followed by second-level, third-level, etc.

![Comments Scraping 3](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/c_4.png)

![Comments Scraping 4](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/c_3.png)

**Unstructured JSON Sample:**

![Unstructured JSON](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/c_json_raw.png)
 
## Basic Scraper

I kept URS 1.0's functionality after I added CLI support, in case anyone prefers to use it over CLI arguments. **It only scrapes Subreddits**; Redditor and post comments scraping would require you to use CLI arguments.

You can access the basic scraper by using the `-b` flag and an export option.

You can just scrape a single Subreddit, or enter a list of Subreddits separated by a space.

![B Flag](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/b_1.png)

After entering the Subreddit(s) you want to scrape, the program will check if the Subreddit exists. It will separate the results into a list of valid and invalid Subreddits.

![Check Subs](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/b_2.png)

You will then choose the post category within the Subreddit (Hot, New, Controversial, Top, Rising, Search). After choosing the category, you will also choose how many results you would like to be returned.

![Post Category Options](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/b_3.png)

If you choose to search for keyword(s) within the Subreddit, you will be greeted with these settings instead.

![Search](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/b_4.png)

After you have configured all settings for each Subreddit, you will be greeted with the following screen which displays all of your settings. After confirming, the program will scrape the Subreddits based on your parameters.

![Settings Overview](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/b_5.png)

![Settings Overview](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/assets/Screenshots/b-6.png)

# Some Linux Tips

- You can further simplify running the program by making the program executable.
- `sudo chmod +x scraper.py`
- Make sure the shebang at the top of scraper.py matches the location in which your Python is installed. You can use `which python` to check. The default shebang is `#!/usr/bin/python`.
- Now you will only have to prepend `./` to run the scraper.
  - `./scraper.py ...`
- Troubleshooting
  - If you run the scraper with `./` and are greeted with a bad interpreter error, you will have to set the fileformat to UNIX. I did this using Vim.
    - ```
      vim scraper.py
      :set fileformat=unix
      :wq!
      ```

# Contributing

I have decided URS 3.0 will be the last major iteration of this project that I will release. I believe the current features should satisfy users who need to scrape Reddit. However, you can still suggest new features that I can add. If there are good suggestions, and a good reason, for a new feature, I will consider adding it. You are also more than welcome to create a pull request, adding additional features or simply improving runtime or streamlining existing code yourself. If the pull request is approved, I will merge the pull request into the master branch, tag it as a new release, and credit you for contributing to this project.

Make sure you follow the contributing guidelines when creating a pull request. See the [Contributing](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/CONTRIBUTING.md) document for more information. 

# Contributors

- **March 11, 2020:** User [ThereGoesMySanity](https://github.com/ThereGoesMySanity) created a [pull request](https://github.com/JosephLai241/Universal-Reddit-Scraper/pull/9) adding 2FA information to Readme.


# Releases

- **May 25, 2019:** Universal Reddit Scraper 1.0. Does not include CLI support.
- **July 29, 2019:** Universal Reddit Scraper 2.0. Now includes CLI support!
- **December 28, 2019:** Universal Reddit Scraper 3.0 (Beta). 
  - New features include:
    - Exporting to JSON
    - Scraping Redditors
  - Comments scraping functionality is still under construction.
 - **December 31, 2019:** Universal Reddit Scraper 3.0 (Official).
   - Comments scraping functionality is now working!
   - Added additional exception handling for creating filenames
   - Minor code reformatting
   - Simplified verbose output
   - Added an additional Submission attribute when scraping Redditors
   - Happy New Year!
 - **January 15, 2020:** Universal Reddit Scraper 3.0 (Final Release).
   - Numerous changes to Readme
   - Minor code reformatting
   - Fulfilled community standards by adding the following docs:
     - [Contributing guidelines](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/CONTRIBUTING.md)
     - [Pull request template](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/PULL_REQUEST_TEMPLATE.md)
     - Issue templates ([bug report](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/ISSUE_TEMPLATE/BUG_REPORT.md) and [feature request](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/ISSUE_TEMPLATE/FEATURE_REQUEST.md))
     - [Code of Conduct](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/CODE_OF_CONDUCT.md)
     - [License](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/LICENSE)
