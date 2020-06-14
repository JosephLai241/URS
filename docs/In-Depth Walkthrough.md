# In-Depth Walkthrough

**First, you will have to provide your own Reddit credentials in the block of credentials found in `Credentials.py`.**

URS will raise an error if you entered invalid credentials.

# Table of Contents

- [CLI Scrapers](#cli-scrapers)
    - [Subreddit Scraper](#subreddit-scraper)
    - [Redditor Scraper](#redditor-scraper)
    - [Comments Scraper](#comments-scraper)
- [Basic Scraper](#basic-scraper)

## CLI scrapers

If you do not want to read the rest of this walkthrough, or forget the args, you can always consult the built-in help message by using `-h` or `--help` . 

![Help Message](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/help.png)

----------------------------------------------------------------------------------------------------------------------------

### Subreddit scraper

Scraping Subreddits using flags is much faster than the [basic scraper](#basic-scraper). 

Use the `-r` flag to indicate a Subreddit, the submission category, and finally, depending on the category selected, either the number of results returned or keyword(s) to search for during the scrape. 

Category options are as follows:

 - H, h - Hot
 - N, n - New
 - C, c - Controversial
 - T, t - Top
 - R, r - Rising  
 - S, s - Search
 
Scraping 10 r/AskReddit posts in the Hot category and export to JSON:

![Subreddit Scraping 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/r_1.png)

The program will then display the type of scrape, check if the Subreddit(s) exist, and display the settings for each Subreddit. It will display a list of invalid Subreddits if applicable. You can also include `-y` in your args if you want to skip this confirmation screen and immediately scrape. 

![Subreddit Scraping 2](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/r_2.png)

**JSON Sample:**

![JSON Sample](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/r_json.png)

**CSV Sample:**

![CSV Sample](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/r_csv.png)

---------------------------------------------------------------------------------------------------------------------------- 

### Redditor Scraper

Use the `-u` flag to indicate a Redditor and the number of results returned. The program will then display the type of scrape and check if the Redditor(s) exist. It will display a list of invalid Redditors, if applicable. 

**These scrapes were designed to be used with JSON only. Exporting to CSV is not recommended, but it will still work.** 

Scraping 5 results for each of u/spez's user attributes and export to JSON:

![Redditor Scraping 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/u_1.png)

There are a couple user lists that are typically restricted and will raise an 403 HTTP Forbidden exception. If you are forbidden from accessing a list, the program will display its name and append "FORBIDDEN" to that section in the export file. 

![Redditor Scraping 2](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/u_2.png)

**JSON Sample:**

![Redditor JSON](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/u_json.png)

----------------------------------------------------------------------------------------------------------------------------

### Comments Scraper

Use the `-c` flag to indicate a submission and the number of comments returned. The program will then display the type of scrape and check if the submission(s) exist. It will display a list of invalid posts, if applicable. 

**These scrapes were designed to be used with JSON only. Exporting to CSV is not recommended, but it will still work.** 

There are two ways you can scrape comments with this program. You can indicate a number to return a structured JSON file that includes down to third-level replies. Or you can specify `0` comments to be returned and the program will return an unstructured JSON file of all comments. 

**Structured Scrape**

Scraping 10 comments from [this Reddit submission](https://www.reddit.com/r/ProgrammerHumor/comments/9ozauu/a_more_accurate_representation_of_what_happened/) and export to JSON:
 

![Comments Scraping 1](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/c_1.png)

![Comments Scraping 2](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/c_2.png)

**Structured JSON Sample:**

![Structured JSON](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/c_json.png)

**Unstructured Scrape**

When exporting raw comments, all top-level comments are listed first, followed by second-level, third-level, etc. 

![Comments Scraping 3](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/c_3.png)

![Comments Scraping 4](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/c_4.png)

**Unstructured JSON Sample:**

![Unstructured JSON](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/c_json_raw.png)

## Basic Scraper

I kept URS 1.0's functionality after I added CLI support, in case anyone prefers to use it over CLI arguments. **It only scrapes Subreddits**; Redditor and submission comments scraping would require you to use CLI arguments. 

You can access the basic scraper by using the `-b` flag and an export option. 

You can just scrape a single Subreddit, or enter a list of Subreddits separated by a space. 

![B Flag](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/b_1.png)

After entering the Subreddit(s) you want to scrape, the program will check if the Subreddit exists. It will separate the results into a list of valid and invalid Subreddits. 

![Check Subs](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/b_2.png)

You will then choose the submission category within the Subreddit (Hot, New, Controversial, Top, Rising, or Search). After choosing the category, you will also choose how many results you would like to be returned. 

![Submission Category Options](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/b_3.png)

If you choose to search for keyword(s) within the Subreddit, you will be greeted with these settings instead. 

![Search](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/b_4.png)

After you have configured all settings for each Subreddit, you will be greeted with the following screen which displays all of your settings. After confirming, the program will scrape the Subreddits based on your parameters. 

![Settings Overview](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/b_5.png)

![Settings Overview](https://github.com/JosephLai241/Universal-Reddit-Scraper/blob/master/.github/Screenshots/b_6.png)
