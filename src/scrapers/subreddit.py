#===============================================================================
#                               Subreddit Scraper
#===============================================================================
from .. import cli, titles

def run_subreddit(args,options,parser,reddit,s_t,subreddit_functions):
    titles.r_title()
    sub_list = cli.create_list(args,s_t,s_t[0])
    subs = cli.confirm_subs(reddit,sub_list,parser)
    s_master = subreddit_functions.c_s_dict(subs)
    cli.get_cli_settings(reddit,args,s_master,s_t,s_t[0])
    if args.y:
        subreddit_functions.gsw_sub(reddit,args,s_master)
    else:
        confirm = subreddit_functions.print_settings(s_master,args)
        if confirm == options[0]:
            subreddit_functions.gsw_sub(reddit,args,s_master)
        else:
            print("\nCancelling.")