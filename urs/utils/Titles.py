"""
Titles
======
Display ASCII art that is used throughout this program.
"""


from colorama import (
    Fore, 
    Style
)

class MainTitle():
    """
    Method for printing the main URS title.
    """

    @staticmethod
    def title():
        """
        Print URS title.
        """

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

    @staticmethod
    def r_title():
        """
        Print Subreddit scraper title.
        """

        print(Fore.WHITE + Style.BRIGHT + r"""
 _ __  
/\`'__\
\ \ \/ 
 \ \_\ 
  \/_/ 
""")

    @staticmethod
    def u_title():
        """
        Print Redditor scraper title.
        """

        print(Fore.WHITE + Style.BRIGHT + r"""
 __  __  
/\ \/\ \ 
\ \ \_\ \
 \ \____/
  \/___/ 
""")

    @staticmethod
    def c_title():
        """
        Print comments scraper title.
        """

        print(Fore.WHITE + Style.BRIGHT + r"""
  ___   
 /'___\ 
/\ \__/ 
\ \____\
 \/____/
""")

    @staticmethod
    def b_title():
        """
        Print basic scraper title.
        """

        print(Fore.WHITE + Style.BRIGHT + r"""
 __        
/\ \       
\ \ \____  
 \ \ '__`\ 
  \ \ \L\ \
   \ \_,__/
    \/___/... Only scrapes Subreddits. 
""")

    @staticmethod
    def lr_title():
        """
        Print Subreddit livestream title.
        """

        print(Fore.WHITE + Style.BRIGHT + r"""
 ___            
/\_ \           
\//\ \    _ __ ⏺️  
  \ \ \  /\`'__\
   \_\ \_\ \ \/ 
   /\____\\ \_\ 
   \/____/ \/_/
""")

    @staticmethod
    def lu_title():
        """
        Print Redditor livestream title.
        """

        print(Fore.WHITE + Style.BRIGHT + r"""
 ___              
/\_ \             
\//\ \    __  __⏺️  
  \ \ \  /\ \/\ \ 
   \_\ \_\ \ \_\ \
   /\____\\ \____/
   \/____/ \/___/ 
""")

class AnalyticsTitles():
    """
    Methods for printing analytical tool titles.
    """

    @staticmethod
    def f_title():
        """
        Print frequencies title.
        """

        print(Fore.WHITE + Style.BRIGHT + r"""
  ___  
 /'___\ 📈
/\ \__/ 
\ \ ,__\ 
 \ \ \_/
  \ \_\ 
   \/_/
""")

    @staticmethod
    def wc_title():
        """
        Print wordcloud title.
        """

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

    @staticmethod
    def e_title(invalid_message):
        """
        Print error title.

        Parameters
        ----------
        invalid_message: str
            String denoting the specific error in arguments

        Returns
        -------
        None
        """

        print(Fore.RED + Style.BRIGHT + fr"""
   __   
 /'__`\ 
/\  __/ 
\ \____\
 \/____/... {invalid_message}
 
Please recheck args or refer to help or usage examples.
""")

    @staticmethod
    def n_title(reddit_object):
        """
        Print exiting title when there are no Reddit objects left to scrape.

        Parameters
        ----------
        reddit_object: str
            String denoting the Reddit object type

        Returns
        -------
        None
        """

        print(Fore.RED + Style.BRIGHT + fr"""
  ___    
 /' _`\  
/\ \/\ \ 
\ \_\ \_\
 \/_/\/_/... No {reddit_object} to scrape! Aborting URS.     
""")

    @staticmethod
    def i_title(error):
        """
        Print invalid file title.

        Parameters
        ----------
        error: str
            String denoting the specific error associated with invalid files
        """

        print(Fore.RED + Style.BRIGHT + fr"""
 __    
/\_\   
\/\ \  
 \ \ \ 
  \ \_\
   \/_/... {error}     
""")

    @staticmethod
    def p_title(error):
        """
        Print PRAW error title.

        Parameters
        ----------
        error: PrawException
            PrawException raised when API validation fails

        Returns
        -------
        None
        """

        print(Fore.RED + Style.BRIGHT + fr"""
 _____   
/\ '__`\ 
\ \ \L\ \
 \ \ ,__/... Please recheck API credentials or your internet connection.
  \ \ \/ 
   \ \_\ 
    \/_/

Prawcore exception: {error}
""")

    @staticmethod
    def l_title(reset_timestamp):
        """
        Print rate limit error title.

        Parameters
        ----------
        reset_timestamp: str
            Reset timestamp provided by PRAW

        Returns
        -------
        None
        """

        print(Fore.RED + Style.BRIGHT + fr"""
 __        
/\ \       
\ \ \      
 \ \ \  __ 
  \ \ \L\ \
   \ \____/
    \/___/... You have reached your rate limit.

Please try again when your rate limit is reset: {reset_timestamp}
""")

    @staticmethod
    def ex_title(error):
        """
        Print export error title.

        Parameters
        ----------
        error: str
            Exception raised while exporting scrape data

        Returns
        -------
        None
        """

        print(Fore.RED + Style.BRIGHT + fr"""
 __     
/\ \    
\ \ \   
 \ \ \  
  \ \_\ 
   \/\_\
    \/_/... An error has occurred while exporting scraped data.
    
{error}
""" )
