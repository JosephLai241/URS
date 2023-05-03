# Error Messages

This document will briefly go over all the potential error messages you might run into while using URS.

# Table of Contents

- [Global Errors](#global-errors)
  - [Invalid Arguments](#invalid-arguments)
  - [Export Error](#export-error)
- [PRAW Errors](#praw-errors)
  - [Invalid API Credentials or No Internet Connection](#invalid-api-credentials-or-no-internet-connection)
  - [No Reddit Objects Left to Scrape](#no-reddit-objects-left-to-scrape)
  - [Rate Limit Reached](#rate-limit-reached)
- [Analytical Tool Errors](#analytical-tool-errors)
  - [Invalid File](#invalid-file)

# Global Errors

## Invalid Arguments

       __
     /'__`\
    /\  __/
    \ \____\
     \/____/... [ERROR MESSAGE]

     Please recheck args or refer to help for usage examples.

This message is displayed if you have entered invalid arguments. The specific error will follow `...`.

You can use the `-h` flag to see the help message or the `-e` flag to display example usage.

## Export Error

     __
    /\ \
    \ \ \
     \ \ \
      \ \_\
       \/\_\
        \/_/... An error has occurred while exporting scraped data.

    [ERROR MESSAGE]

This message is displayed if an error occured while exporting the data. This applies to the scraper tools or word frequencies tool. The specific error will be printed under the art.

# PRAW Errors

## Invalid API Credentials or No Internet Connection

     _____
    /\ '__`\
    \ \ \L\ \
     \ \ ,__/... Please recheck API credentials or your internet connection.
      \ \ \/
       \ \_\
        \/_/

    Prawcore exception: [EXCEPTION]

This message is displayed if you enter invalid API credentials or if you are not connected to the internet. The exception is printed under the art.

Recheck the environment variables in `.env` to make sure your API credentials are correct.

## No Reddit Objects Left to Scrape

      ___
    /' _ `\
    /\ \/\ \
    \ \_\ \_\
     \/_/\/_/... No [OBJECTS] to scrape! Exiting.

This message is displayed if the Reddit objects you have passed in have failed validation (does not exist), are skipped, and there are no longer any objects left for URS to process for that specific scraper.

## Rate Limit Reached

     __
    /\ \
    \ \ \
     \ \ \  __
      \ \ \L\ \
       \ \____/
        \/___/... You have reached your rate limit.

    Please try again when your rate limit is reset: [DATE]

PRAW has rate limits. This message is displayed if you have reached the rate limit set for your account. The reset date will vary depending on when you ran URS. The date I received during testing is usually 24 hours later.

# Analytical Tool Errors

## Invalid File

     __
    /\_\
    \/\ \
     \ \ \
      \ \_\
       \/_/... [ERROR MESSAGE]

This message is displayed when you have passed in an invalid file to generate word frequencies or a wordcloud for. The specific error will follow `...`.
