"""
Titles
======
Display ASCII art that is used throughout this program.
"""


from colorama import (
    init, 
    Fore, 
    Style
)

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class MainTitle():
    """
    Method for printing the main URS title.
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

class PRAWTitles():
    """
    Methods for printing PRAW scraper titles.
    """

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

class AnalyticsTitles():
    """
    Methods for printing for analytical tool titles.
    """

    ### Print frequencies title.
    @staticmethod
    def f_title():
        print(Fore.WHITE + Style.BRIGHT + r"""
   ___  
 /'___\ 📋
/\ \__/ 
\ \ ,__\ 
 \ \ \_/
  \ \_\ 
   \/_/
""")

    ### Print wordcloud title.
    @staticmethod
    def wc_title():
        print(Fore.WHITE + Style.BRIGHT + r"""
 __  __  __    ___ 🖌️ 
/\ \/\ \/\ \  /'___\ 
\ \ \_/ \_/ \/\ \__/ 
 \ \___x___/'\ \____\
  \/__//__/   \/____/
""")

class Errors():
    """
    Methods for printing error titles.
    """

    ### Print error title.
    @staticmethod
    def e_title():
        print(Fore.RED + Style.BRIGHT + r"""
   __   
 /'__`\ 
/\  __/ 
\ \____\
 \/____/... Please recheck args or refer to help or usage examples.
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
