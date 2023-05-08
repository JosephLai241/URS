# Scrape Speeds

Your internet connection speed is the primary bottleneck that will establish the scrape duration; however, there are additional bottlenecks such as:

- The number of results returned for Subreddit or Redditor scraping.
- The submission's popularity (total number of comments) for submission comments scraping.

# Rate Limits

Yes, PRAW has rate limits. These limits are proportional to how much karma you have accumulated -- the higher the karma, the higher the rate limit. This has been implemented to mitigate spammers and bots that utilize PRAW.

Rate limit information for your account is displayed in a small table underneath the successful login message each time you run any of the PRAW scrapers. I have also added a [`--check` flag](../utilities/rate-limit-checking.md) if you want to quickly view this information.

`URS` will display an error message as well as the rate limit reset date if you have used all your available requests.

There are a couple ways to circumvent rate limits:

- Scrape intermittently
- Use an account with high karma to get your PRAW credentials
- Scrape less results per run

Available requests are refilled if you use the PRAW scrapers intermittently, which might be the best solution. This can be especially helpful if you have automated `URS` and are not looking at the output on each run.
