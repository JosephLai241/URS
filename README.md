# Reddit Scraper for Penetration Testing posts

You will need to install the PRAW module in order for this program to work. `pip install praw` or `pip3 install praw` depending on your system.

*NOTE:* PRAW currently only supports Python 2.7, 3.3, 3.4, 3.5, and 3.6.

This is a Reddit scraper I created using the Reddit API. It is designed specifically to scrape for information within the following subreddits:
 - Pentesting
 - AskNetSec
 - HowToHack
 - netsec
 - hacking
 - netsecstudents
 - raspberry_pi
 - homelab
 - Kalilinux
 - Hacking_Tutorials
 - pentest

You can choose which category of posts to scrape each subreddit as well as how many results are returned. These options include:
 - Hot
 - New
 - Controversial
 - Top
 - Rising
 - Search - Users also have the option to search each subreddit for keywords; however, all search results are returned and the number of results the user specifically wants is disregarded.

# You need your own Reddit account and app credentials in order to use this



# How to modify this program to scrape other subreddits

This program can be easily modified to scrape any subreddit(s). All you have to do is change the list of subreddits to scrape on line 21 to the subreddits you want.

Enjoy!
