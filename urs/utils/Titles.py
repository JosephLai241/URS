#===============================================================================
#                                   Titles
#===============================================================================
from colorama import init, Style

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class Titles():
    """
    Functions for printing all titles used in this program.
    """

    ### Print Reddit scraper title
    def title(self):
        print(Style.BRIGHT + r"""
            __  ______  _____    _____  ____   ___
           / / / / __ \/ ___/   |__  / / __ \ <  /
          / / / / /_/ /\__ \     /_ < / / / / / / 
         / /_/ / _, _/___/ /   ___/ // /_/ / / /  
         \____/_/ |_|/____/   /____(_)____(_)_/   
         =========================================
      Scrape Subreddits, Redditors, and post comments
""")

    ### Print Subreddit scraper title
    def r_title(self):
        print(Style.BRIGHT + r"""
     _____       __                  __    ___ __
    / ___/__  __/ /_  ________  ____/ /___/ (_) /______
    \__ \/ / / / __ \/ ___/ _ \/ __  / __  / / __/ ___/
    ___/ / /_/ / /_/ / /  /  __/ /_/ / /_/ / / /_(__  )
   /____/\__,_/_.___/_/   \___/\__,_/\__,_/_/\__/____/
""")

    ### Print Redditor scraper title
    def u_title(self):
        print(Style.BRIGHT + r"""
       ____           __    ___ __
      / __ \___  ____/ /___/ (_) /_____  __________
     / /_/ / _ \/ __  / __  / / __/ __ \/ ___/ ___/
    / _, _/  __/ /_/ / /_/ / / /_/ /_/ / /  (__  )
   /_/ |_|\___/\__,_/\__,_/_/\__/\____/_/  /____/
""")

    ### Print comments scraper title
    def c_title(self):
        print(Style.BRIGHT + r"""
      ______                                     __
     / ____/___  ____ ___  ____ ___  ___  ____  / /______
    / /   / __ \/ __ `__ \/ __ `__ \/ _ \/ __ \/ __/ ___/
   / /___/ /_/ / / / / / / / / / / /  __/ / / / /_(__  )
   \____/\____/_/ /_/ /_/_/ /_/ /_/\___/_/ /_/\__/____/
""")

    ### Print basic scraper title
    def b_title(self):
        print(Style.BRIGHT + r"""
       __               _
      / /_  ____ ______(_)____
     / __ \/ __ `/ ___/ / ___/
    / /_/ / /_/ (__  ) / /__
   /_.___/\__,_/____/_/\___/
   ---------------------------
    *Only scrapes Subreddits*
""")

    ### Print error title
    def e_title(self):
        print(Style.BRIGHT + r"""
                  __________  ____  ____  ____
                 / ____/ __ \/ __ \/ __ \/ __ \
                / __/ / /_/ / /_/ / / / / /_/ /
               / /___/ _, _/ _, _/ /_/ / _, _/
              /_____/_/ |_/_/ |_|\____/_/ |_|
              =================================
   Please recheck args or refer to help for usage examples.
""")