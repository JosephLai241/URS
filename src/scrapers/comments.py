#===============================================================================
#                               Comments Scraper
#===============================================================================
from .. import cli, titles

def run_comments(args,comments_functions,parser,reddit,s_t):
    titles.c_title()
    post_list = cli.create_list(args,s_t,s_t[2])
    posts = comments_functions.list_posts(reddit,post_list,parser)
    c_master = comments_functions.c_c_dict(posts)
    cli.get_cli_settings(reddit,args,c_master,s_t,s_t[2])
    comments_functions.w_comments(reddit,post_list,c_master,args)
