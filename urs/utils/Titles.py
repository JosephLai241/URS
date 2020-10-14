#===============================================================================
#                                   Titles
#===============================================================================
from colorama import (
    init, 
    Fore, 
    Style)

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class Titles():
    """
    Methods for printing all titles used in this program.
    """

    ### Print URS title.
    @staticmethod
    def title():
        print(Fore.WHITE + Style.BRIGHT + r"""
 __  __  _ __   ____  
/\ \/\ \/\`'__\/',__\ 
\ \ \_\ \ \ \//\__, `\
 \ \____/\ \_\\/\____/
  \/___/  \/_/ \/___/ 
""")

    ### Print Subreddit scraper title.
    @staticmethod
    def r_title():
        print(Fore.WHITE + Style.BRIGHT + r"""
 _ __  
/\`'__\
\ \ \/ 
 \ \_\ 
  \/_/ 
""")

    ### Print Redditor scraper title.
    @staticmethod
    def u_title():
        print(Fore.WHITE + Style.BRIGHT + r"""
 __  __  
/\ \/\ \ 
\ \ \_\ \
 \ \____/
  \/___/ 
""")

    ### Print comments scraper title.
    @staticmethod
    def c_title():
        print(Fore.WHITE + Style.BRIGHT + r"""
  ___   
 /'___\ 
/\ \__/ 
\ \____\
 \/____/
""")

    ### Print basic scraper title.
    @staticmethod
    def b_title():
        print(Fore.WHITE + Style.BRIGHT + r"""
 __        
/\ \       
\ \ \____  
 \ \ '__`\ 
  \ \ \L\ \
   \ \_,__/
    \/___/... Only scrapes Subreddits. 
""")

    ### Print error title.
    @staticmethod
    def e_title():
        print(Fore.RED + Style.BRIGHT + r"""
   __   
 /'__`\ 
/\  __/ 
\ \____\
 \/____/... Please recheck args or refer to help for usage examples.
""")

    ### Print PRAW error title.
    @staticmethod
    def p_title(error):
        print(Fore.RED + Style.BRIGHT + r"""
 _____   
/\ '__`\ 
\ \ \L\ \
 \ \ ,__/... Please recheck API credentials or your internet connection.
  \ \ \/ 
   \ \_\ 
    \/_/

Prawcore exception: %s
""" % error)

    ### Print rate limit error title.
    @staticmethod
    def l_title(reset_timestamp):
        print(Fore.RED + Style.BRIGHT + r"""
 __        
/\ \       
\ \ \      
 \ \ \  __ 
  \ \ \L\ \
   \ \____/
    \/___/... You have reached your rate limit.

Please try again when your rate limit is reset: %s
""" % reset_timestamp)
