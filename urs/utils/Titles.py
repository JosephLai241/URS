"""
Titles
======
Display ASCII art that is used throughout this program.
"""


from colorama import Fore, Style
from prawcore import PrawcoreException


class MainTitle:
    """
    Method for printing the main URS title.
    """

    @staticmethod
    def title() -> None:
        """
        Print URS title.
        """

        print(
            Fore.WHITE
            + Style.BRIGHT
            + r"""
 __  __  _ __   ____
/\ \/\ \/\`'__\/',__\
\ \ \_\ \ \ \//\__, `\
 \ \____/\ \_\\/\____/
  \/___/  \/_/ \/___/
"""
        )


class PRAWTitles:
    """
    Methods for printing PRAW scraper titles.
    """

    @staticmethod
    def r_title() -> None:
        """
        Print Subreddit scraper title.
        """

        print(
            Fore.WHITE
            + Style.BRIGHT
            + r"""
 _ __
/\`'__\
\ \ \/
 \ \_\
  \/_/
"""
        )

    @staticmethod
    def u_title() -> None:
        """
        Print Redditor scraper title.
        """

        print(
            Fore.WHITE
            + Style.BRIGHT
            + r"""
 __  __
/\ \/\ \
\ \ \_\ \
 \ \____/
  \/___/
"""
        )

    @staticmethod
    def c_title() -> None:
        """
        Print comments scraper title.
        """

        print(
            Fore.WHITE
            + Style.BRIGHT
            + r"""
  ___
 /'___\
/\ \__/
\ \____\
 \/____/
"""
        )

    @staticmethod
    def b_title() -> None:
        """
        Print basic scraper title.
        """

        print(
            Fore.WHITE
            + Style.BRIGHT
            + r"""
 __
/\ \
\ \ \____
 \ \ '__`\
  \ \ \L\ \
   \ \_,__/
    \/___/... Only scrapes Subreddits.
"""
        )

    @staticmethod
    def lr_title() -> None:
        """
        Print Subreddit livestream title.
        """

        print(
            Fore.WHITE
            + Style.BRIGHT
            + r"""
 ___
/\_ \
\//\ \    _ __ ⏺️
  \ \ \  /\`'__\
   \_\ \_\ \ \/
   /\____\\ \_\
   \/____/ \/_/
"""
        )

    @staticmethod
    def lu_title() -> None:
        """
        Print Redditor livestream title.
        """

        print(
            Fore.WHITE
            + Style.BRIGHT
            + r"""
 ___
/\_ \
\//\ \    __  __⏺️
  \ \ \  /\ \/\ \
   \_\ \_\ \ \_\ \
   /\____\\ \____/
   \/____/ \/___/
"""
        )


class AnalyticsTitles:
    """
    Methods for printing analytical tool titles.
    """

    @staticmethod
    def f_title() -> None:
        """
        Print frequencies title.
        """

        print(
            Fore.WHITE
            + Style.BRIGHT
            + r"""
  ___
 /'___\ 📈
/\ \__/
\ \ ,__\
 \ \ \_/
  \ \_\
   \/_/
"""
        )

    @staticmethod
    def wc_title() -> None:
        """
        Print wordcloud title.
        """

        print(
            Fore.WHITE
            + Style.BRIGHT
            + r"""
 __  __  __    ___ 🖌️
/\ \/\ \/\ \  /'___\
\ \ \_/ \_/ \/\ \__/
 \ \___x___/'\ \____\
  \/__//__/   \/____/
"""
        )


class Errors:
    """
    Methods for printing error titles.
    """

    @staticmethod
    def e_title(invalid_message: str) -> None:
        """
        Print error title.

        :param str invalid_message: The specific error message in arguments.
        """

        print(
            Fore.RED
            + Style.BRIGHT
            + rf"""
   __
 /'__`\
/\  __/
\ \____\
 \/____/... {invalid_message}

Please recheck args or refer to help or usage examples.
"""
        )

    @staticmethod
    def n_title(reddit_object: str) -> None:
        """
        Print exiting title when there are no Reddit objects left to scrape.

        :param str reddit_object: The Reddit object type.
        """

        print(
            Fore.RED
            + Style.BRIGHT
            + rf"""
  ___
 /' _`\
/\ \/\ \
\ \_\ \_\
 \/_/\/_/... No {reddit_object} to scrape! Aborting URS.
"""
        )

    @staticmethod
    def i_title(error: str) -> None:
        """
        Print invalid file title.

        :param str error: The specific error associated with invalid files.
        """

        print(
            Fore.RED
            + Style.BRIGHT
            + rf"""
 __
/\_\
\/\ \
 \ \ \
  \ \_\
   \/_/... {error}
"""
        )

    @staticmethod
    def p_title(error: PrawcoreException) -> None:
        """
        Print PRAW error title.

        :param PrawcoreException error: The `PrawcoreException` raised when API
            validation fails.
        """

        print(
            Fore.RED
            + Style.BRIGHT
            + rf"""
 _____
/\ '__`\
\ \ \L\ \
 \ \ ,__/... Please recheck API credentials or your internet connection.
  \ \ \/
   \ \_\
    \/_/

Prawcore exception: {error}
"""
        )

    @staticmethod
    def l_title(reset_timestamp: str) -> None:
        """
        Print rate limit error title.

        :param str reset_timestamp: The reset timestamp provided by PRAW.
        """

        print(
            Fore.RED
            + Style.BRIGHT
            + rf"""
 __
/\ \
\ \ \
 \ \ \  __
  \ \ \L\ \
   \ \____/
    \/___/... You have reached your rate limit.

Please try again when your rate limit is reset: {reset_timestamp}
"""
        )

    @staticmethod
    def ex_title(error: Exception) -> None:
        """
        Print export error title.

        :param Exception error: The `Exception` raised while exporting scrape data.
        """

        print(
            Fore.RED
            + Style.BRIGHT
            + rf"""
 __
/\ \
\ \ \
 \ \ \
  \ \_\
   \/\_\
    \/_/... An error has occurred while exporting scraped data.

{error}
"""
        )
