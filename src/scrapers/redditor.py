#===============================================================================
#                               Redditor Scraper
#===============================================================================
from .. import cli, titles

def run_redditor(args,s_t,parser,reddit,redditor_functions):
    titles.u_title()
    user_list = cli.create_list(args,s_t,s_t[1])
    users = redditor_functions.list_users(reddit,user_list,parser)
    u_master = redditor_functions.c_u_dict(users)
    cli.get_cli_settings(reddit,args,u_master,s_t,s_t[1])
    redditor_functions.w_user(reddit,users,u_master,args)