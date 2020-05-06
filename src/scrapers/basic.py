#===============================================================================
#                           Basic Subreddit Scraper
#===============================================================================
from .. import titles

def run_basic(args,basic_functions,options,parser,reddit,subreddit):
    titles.b_title()
    while True:
        while True:
            subs = basic_functions.get_subreddits(reddit,parser)
            s_master = subreddit.c_s_dict(subs)
            basic_functions.get_settings(subs,s_master)
            confirm = subreddit.print_settings(s_master,args)
            if confirm == options[0]:
                break
            else:
                print("\nExiting.")
                parser.exit()
        subreddit.gsw_sub(reddit,args,s_master)
        repeat = basic_functions.another()
        if repeat == options[1]:
            print("\nExiting.")
            break