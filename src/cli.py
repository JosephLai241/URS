#===============================================================================
#                       Command-line Interface Functions
#===============================================================================
import argparse
import sys
from . import global_vars, titles, validation

### Global variables
short_cat = global_vars.short_cat
s_t = global_vars.s_t

### Get args
def parse_args():
    parser = argparse.ArgumentParser(usage = "scraper.py [-h] [-r SUBREDDIT [H|N|C|T|R|S] RESULTS_OR_KEYWORDS] [-u USER RESULTS] [-c URL RESULTS] [-b] [-y] [--csv|--json]", \
                                    formatter_class = argparse.RawDescriptionHelpFormatter, \
                                    description = "Universal Reddit Scraper 3.0 - Scrape Subreddits, Redditors, or comments from posts", \
                                    epilog = r"""
Subreddit categories:
   H,h     selecting Hot category
   N,n     selecting New category
   C,c     selecting Controversial category
   T,t     selecting Top category
   R,r     selecting Rising category
   S,s     selecting Search category

EXAMPLES

    Get the first 10 posts in r/all in the Hot category and export to JSON:

        $ ./scraper.py -r all h 10 --json

    Search for "United States of America" in r/worldnews and export to CSV:

        $ ./scraper.py -r worldnews s "United States of America" --csv

    Scraping 50 results from u/spez's Reddit account:

        $ ./scraper.py -u spez 50 --json

    Scraping 25 comments from this r/TIFU post:

        $ ./scraper.py -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 25 --csv

    You can scrape multiple items at once:

        $ ./scraper.py -r askreddit h 15 -u spez 25 -c https://www.reddit.com/r/tifu/comments/a99fw9/tifu_by_buying_everyone_an_ancestrydna_kit_and/ 50 --json

    You can also still use URS 1.0 (SUBREDDIT SCRAPING ONLY), but you cannot include this flag with any items besides export options:

        $ ./scraper.py -b --csv

""")

    ### Parser Subreddit, basic, Redditor, comments scraper, and skip confirmation flags
    scraper = parser.add_argument_group("Scraping options")
    scraper.add_argument("-r","--sub",action="append",nargs=3,metavar="",help="specify Subreddit to scrape")
    scraper.add_argument("-b","--basic",action="store_true",help="initialize non-CLI Subreddit scraper")
    scraper.add_argument("-u","--user",action="append",nargs=2,metavar="",help="specify Redditor profile to scrape")
    scraper.add_argument("-c","--comments",action="append",nargs=2,metavar="",help="specify the URL of the post to scrape comments")
    scraper.add_argument("-y",action="store_true",help="skip Subreddit options confirmation and scrape immediately")

    ### Export to CSV or JSON flags
    expt = parser.add_mutually_exclusive_group(required=True)
    expt.add_argument("--csv",action="store_true",help="export to CSV")
    expt.add_argument("--json",action="store_true",help="export to JSON")

    ### Print help message if no arguments are present
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()
    return parser,args

### Create either Subreddit, Redditor, or posts list
def create_list(args,s_t,l_type):
    if l_type == s_t[0]:
        list = [sub[0] for sub in args.sub]
    elif l_type == s_t[1]:
        list = [user[0] for user in args.user]
    elif l_type == s_t[2]:
        list = [post[0] for post in args.comments]

    return list

### Check args and catching errors
def check_args(parser,args):
    try:
        if args.sub:
            for subs in args.sub:
                len_counter = 0
                if subs[1].upper() not in short_cat:
                    raise ValueError
                for char in short_cat:
                    if str(subs[1]).upper() == char:
                        if str(subs[1]).upper() != "S" and subs[2].isalpha():
                            raise ValueError
                        break
                    elif len_counter == len(short_cat) - 1:
                        raise ValueError
                    else:
                        len_counter += 1
        if args.user:
            for user in args.user:
                if user[1].isalpha():
                    raise ValueError
        if args.comments:
            for post in args.comments:
                if post[1].isalpha():
                    raise ValueError
    except ValueError:
        titles.e_title()
        parser.exit()

### Check if Subreddits exist and list invalid Subreddits if applicable
def confirm_subs(reddit,sub_list,parser):
    print("\nChecking if Subreddit(s) exist...")
    found,not_found = validation.existence(reddit,sub_list,parser,s_t,s_t[0])
    if not_found:
        print("\nThe following Subreddits were not found and will be skipped:")
        print("-"*60)
        print(*not_found, sep = "\n")

    subs = [sub for sub in found]
    return subs

### Get CLI scraping settings for Subreddits, Redditors, and post comments
def get_cli_settings(reddit,args,master,s_t,s_type):
    if s_type == s_t[0]:
        for sub_n in master:
            for sub in args.sub:
                settings = [sub[1],sub[2]]
                if sub_n == sub[0]:
                    master[sub_n].append(settings)
    elif s_type == s_t[1]:
        for user in args.user:
            master[user[0]] = user[1]
    elif s_type == s_t[2]:
        for comments in args.comments:
            master[comments[0]] = comments[1]
