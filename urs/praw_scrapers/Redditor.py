"""
Redditor scraper
================
Defining methods for the Redditor scraper.
"""


import praw

from colorama import (
    init, 
    Fore, 
    Style
)
from prawcore import PrawcoreException

from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import (
    Export,
    NameFile
)
from urs.utils.Global import (
    convert_time,
    eo,
    make_none_dict,
    s_t
)
from urs.utils.Logger import (
    LogExport, 
    LogPRAWScraper
)
from urs.utils.Titles import PRAWTitles

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class CheckRedditors():
    """
    Method for printing found and invalid Redditors.
    """

    @staticmethod
    def list_redditors(parser, reddit, user_list):
        """
        Check if Redditors exist and list Redditors who are not found.

        Calls a public method from an external module:

            Validation.existence()

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser object
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        user_list: list
            List of Redditors

        Returns
        -------
        users: list
            List of valid Redditors URLs
        """

        print("\nChecking if Redditor(s) exist...")
        users, not_users = Validation.existence(s_t[1], user_list, parser, reddit, s_t)
        
        if not_users:
            print(Fore.YELLOW + Style.BRIGHT + "\nThe following Redditors were not found and will be skipped:")
            print(Fore.YELLOW + Style.BRIGHT + "-" * 59)
            print(*not_users, sep = "\n")

        if not users:
            print(Fore.RED + Style.BRIGHT + "\nNo Redditors to scrape!")
            print(Fore.RED + Style.BRIGHT + "\nExiting.\n")
            quit()

        return users

class ProcessInteractions():
    """
    Methods for sorting and labeling comment or submission objects correctly.
     
    Some user attributes will return a ListingGenerator which includes both comments 
    and submissions. These attributes will need to be sorted accordingly:
    - Downvoted (may be forbidden)
    - Gilded
    - Gildings (may be forbidden)
    - Hidden (may be forbidden)
    - Hot
    - New
    - Saved (may be forbidden)
    - Upvoted (may be forbidden)
    """

    def __init__(self, limit, skeleton, user):
        """
        Initialize variables used in later methods:

            self._skeleton: dictionary that contains all Redditor metadata and interactions

            self._comments: user's comment objects
            self._controversial: user's controversial objects
            self._downvoted: user's downvoted objects
            self._gilded: user's gilded objects
            self._gildings: user's gildings objects
            self._hidden: user's hidden objects
            self._hot: user's hot objects
            self._new: user's new objects
            self._saved: user's saved objects
            self._submissions: user's submission objects
            self._top: user's top objects
            self._upvoted: user's upvoted objects
            
            self._comment_titles: list of comment attribute fields
            self._submission_titles: list of submission attribute fields

            self._scrape_types: list of sorted scrape types for Redditor data

            self._mutts: list of user objects that may return either submission or comment objects
            self._mutt_names: list of titles for each user object in self._mutts

            self._access: list of user objects that may return a 403 HTTP Forbidden exception
            self._access_names: list of titles for each user object in self._access

        Parameters
        ----------
        limit: int
            Integer denoting n_results to return
        skeleton: dict
            Dictionary containing all Redditor data
        user: PRAW object

        Returns
        -------
        None
        """

        self._skeleton = skeleton

        self._comments = user.comments.new(limit = limit)
        self._controversial = user.controversial(limit = limit)
        self._downvoted = user.downvoted(limit = limit)
        self._gilded = user.gilded(limit = limit)
        self._gildings = user.gildings(limit = limit)
        self._hidden = user.hidden(limit = limit)
        self._hot = user.hot(limit = limit)
        self._new = user.new(limit = limit)
        self._saved = user.saved(limit = limit)
        self._submissions = user.submissions.new(limit = limit)
        self._top = user.top(limit = limit)
        self._upvoted = user.upvoted(limit = limit)

        self._comment_titles = [
            "type",
            "date_created", 
            "score", 
            "text", 
            "parent_id", 
            "link_id", 
            "edited", 
            "stickied", 
            "replying_to", 
            "in_subreddit"
        ]
        self._submission_titles = [
            "type",
            "title", 
            "date_created", 
            "upvotes", 
            "upvote_ratio",
            "id", 
            "nsfw", 
            "in_subreddit", 
            "body"
        ]

        self._scrape_types = [
            "submissions", 
            "comments", 
            "mutts", 
            "access"
        ]

        self._mutts = [
            self._controversial, 
            self._gilded, 
            self._hot, 
            self._new, 
            self._top
        ]
        self._mutt_names = [
            "controversial", 
            "gilded", 
            "hot", 
            "new", 
            "top"
        ]

        self._access = [
            self._downvoted, 
            self._gildings, 
            self._hidden, 
            self._saved, 
            self._upvoted
        ]
        self._access_names = [
            "downvoted", 
            "gildings", 
            "hidden", 
            "saved", 
            "upvoted"
        ]

    def _make_zip_dict(self, items, titles):
        """
        Make a dictionary from zipped lists. This private method is used to create
        individual submission or comment objects to store in lists.

        Parameters
        ----------
        items: list
            List of strings to set the dictionary keys
        titles: list
            List of PRAW objects to set the dictionary values

        Returns
        -------
        redditor_data: dict
            Dictionary for a Redditor object (submission or comment)
        """

        return dict((title, item) for title, item in zip(titles, items))

    def _make_submission_item(self, item):
        """
        Make submission item. 
        
        Calls previously defined private method:

            self._make_zip_dict()

        Parameters
        ----------
        item: PRAW object
            PRAW submission item

        Returns
        -------
        redditor_item: dict
            Dictionary for a Redditor's submission
        """

        items = [
            "submission",
            item.title, 
            convert_time(item.created), 
            item.score, 
            item.upvote_ratio, 
            item.id, 
            item.over_18, 
            item.subreddit.display_name, 
            item.selftext
        ]

        return self._make_zip_dict(items, self._submission_titles)

    def _make_comment_item(self, item):
        """
        Make comment item. 
        
        Calls previously defined private method:

            self._make_zip_dict()

        Parameters
        ----------
        item: PRAW object
            PRAW comment item

        Returns
        -------
        redditor_item: dict
            Dictionary for a Redditor's comment
        """

        edit_date = item.edited \
            if str(item.edited).isalpha() \
            else convert_time(item.edited)
        items = [
            "comment",
            convert_time(item.created_utc), 
            item.score, 
            item.body, 
            item.parent_id, 
            item.link_id, 
            edit_date, 
            item.stickied, 
            item.submission.selftext, 
            item.submission.subreddit.display_name
        ]

        return self._make_zip_dict(items, self._comment_titles)

    def _determine_append(self, cat, redditor_item, scrape_type):
        """
        Determine how to append the list to the JSON skeleton. 
        
        Calls previously defined private method:

            self._scrape_types()

        Parameters
        ----------
        cat: str
            String denoting Redditor category
        redditor_item: dict
            Dictionary for a Redditor's submission or comment
        scrape_type: str
            String denoting the scrape type within self._scrape_types

        Returns
        -------
        None
        """

        switch = {
            0: "submissions",
            1: "comments",
            2: "%s" % cat \
                if cat != None \
                else None,
        }

        index = self._scrape_types.index(scrape_type)
        self._skeleton["data"]["interactions"][switch.get(index)].append(redditor_item)

    def _extract(self, cat, obj, scrape_type):
        """
        Extracting submission or comment attributes and appending to the skeleton.
        
        Calls previously defined private methods:

            self._make_submission_item()
            self._make_comment_item()
            self._determine_append()

        Parameters
        ----------
        cat: str
            String denoting Redditor category
        obj: PRAW object
            PRAW Redditor object that may contain Redditor submissions or comments 
        scrape_type: str
            String denoting the scrape type within self._scrape_types

        Returns
        -------
        None
        """

        for item in obj:
            redditor_item = self._make_submission_item(item) \
                if isinstance(item, praw.models.Submission) \
                else self._make_comment_item(item)

            self._determine_append(cat, redditor_item, scrape_type) 

    def sort_submissions(self):
        """
        Sort Redditor submissions. 
        
        Calls previously defined private method:

            self._extract()
        """

        self._extract(None, self._submissions, self._scrape_types[0])

    def sort_comments(self):
        """
        Sort Redditor comments. 
        
        Calls previously defined private method:

            self._extract()
        """

        self._extract(None, self._comments, self._scrape_types[1])

    def sort_mutts(self):
        """
        Sort Controversial, Gilded, Hot, New and Top Redditor posts. The ListingGenerator
        returns a mix of submissions and comments, so handling each differently is
        necessary. 
        
        Calls previously defined private method:

            self._extract()
        """

        for cat, obj in zip(self._mutt_names, self._mutts):
            self._extract(cat, obj, self._scrape_types[2])

    def sort_access(self):
        """
        Sort upvoted, downvoted, gildings, hidden, and saved Redditor posts. These
        lists tend to raise a 403 HTTP Forbidden exception, so naturally exception
        handling is necessary. 
        
        Calls previously defined private method:

            self._extract()
        """

        for cat, obj in zip(self._access_names, self._access):
            try:
                self._extract(cat, obj, self._scrape_types[3])
            except PrawcoreException as error:
                print(Style.BRIGHT + Fore.YELLOW + "\nACCESS TO %s OBJECTS FORBIDDEN: %s. SKIPPING." % (cat.upper(), error))
                self._skeleton["data"]["interactions"]["%s" % cat].append("FORBIDDEN")

class GetInteractions():
    """
    Methods for getting Redditor information and interactions.
    """

    def __init__(self):
        """
        Initialize variables used in later methods:

            self._info_titles: list of titles for Redditor information
            self._interaction_titles: list of titles for each type of Redditor interaction

        Returns
        -------
        None
        """

        self._info_titles = [
            "name", 
            "fullname", 
            "id", 
            "date_created", 
            "comment_karma", 
            "link_karma", 
            "is_employee", 
            "is_friend", 
            "is_mod", 
            "is_gold"
        ]
        self._interaction_titles = [ 
            "submissions", 
            "comments", 
            "hot", 
            "new", 
            "controversial", 
            "top", 
            "upvoted", 
            "downvoted", 
            "gilded", 
            "gildings", 
            "hidden", 
            "saved"
        ]

    def _make_json_skeleton(self, limit, reddit, user):
        """
        Create a skeleton for JSON export. Include scrape details at the top.

        Parameters
        ----------
        limit: str
            String denoting n_results returned
        reddit: PRAW Reddit object
        user: PRAW Redditor object

        Returns
        -------
        skeleton: dict
            Dictionary containing all Redditor data
        user: PRAW Redditor object
        """

        plurality = "results" \
            if int(limit) > 1 \
            else "result"
        print(Style.BRIGHT + "\nProcessing %s %s from u/%s's profile..." % (limit, plurality, user))
        print("\nThis may take a while. Please wait.")

        skeleton = {
            "scrape_settings": {
                "redditor": user,
                "n_results": limit
            },
            "data": {
                "information": {},
                "interactions": {}
            }
        }
        user = reddit.redditor(user)

        return skeleton, user

    def _get_user_info(self, skeleton, user):
        """
        Get Redditor account information.

        Calls a previously defined private method:

            self._info_titles()

        Calls a public method from an external module:

            Global.convert_time()

        Parameters
        ----------
        skeleton: dict
            Dictionary containing all Redditor data
        user: PRAW Redditor object

        Returns
        -------
        None
        """

        user_info_titles = self._info_titles
        user_info = [
            user.name, 
            user.fullname, 
            user.id, 
            convert_time(user.created_utc),
            user.comment_karma, 
            user.link_karma, 
            user.is_employee, 
            user.is_friend,
            user.is_mod, 
            user.is_gold
        ]

        for info_title, user_item in zip(user_info_titles, user_info):
            skeleton["data"]["information"][info_title] = user_item

    def _make_interactions_lists(self, skeleton):
        """
        Make empty lists for each user interaction field.

        Parameters
        ----------
        skeleton: dict
            Dictionary containing all Redditor data

        Returns
        -------
        None
        """

        for interaction_title in self._interaction_titles:
            skeleton["data"]["interactions"][interaction_title] = []

    def _get_user_interactions(self, limit, skeleton, user):
        """
        Get Redditor interactions on Reddit.

        Calls previously defined private and public methods:

            self._make_interactions_lists()

            ProcessInteractions()
            ProcessInteractions().sort_submissions()
            ProcessInteractions().sort_comments()
            ProcessInteractions().sort_mutts()
            ProcessInteractions().sort_access()


        Parameters
        ----------
        limit: str
            String denoting n_results returned
        skeleton: dict
            Dictionary containing all Redditor data
        user: PRAW Redditor object

        Returns
        -------
        None
        """

        self._make_interactions_lists(skeleton)

        interactions = ProcessInteractions(int(limit), skeleton, user)
        interactions.sort_submissions()
        interactions.sort_comments()
        interactions.sort_mutts()
        interactions.sort_access()

    def get(self, limit, reddit, user):
        """
        Get Redditor information and interactions.

        Calls previously defined private methods:

            self._make_json_skeleton()
            self._get_user_info()
            self._get_user_interactions()

        Parameters
        ----------
        limit: str
            String denoting n_results returned
        reddit: PRAW Reddit object
        user: PRAW Redditor object

        Returns
        -------
        skeleton: dict
            Dictionary containing all Redditor data
        """

        skeleton, user = self._make_json_skeleton(limit, reddit, user)
        self._get_user_info(skeleton, user)
        self._get_user_interactions(limit, skeleton, user)

        return skeleton

class Write():
    """
    Methods for writing scraped Redditor information to CSV or JSON.
    """

    @staticmethod
    def _determine_export(args, data, f_name):
        """
        Export to either CSV or JSON.

        Calls a public method from an external module:

            Export.export()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        data: dict
            Dictionary containing Redditor information to write to file
        f_name: str
            String denoting the filename

        Returns
        -------
        None
        """

        export_option = eo[1] \
            if not args.csv \
            else eo[0]

        Export.export(data, f_name, export_option, "redditors")

    @staticmethod
    def _print_confirm(args, user):
        """
        Print confirmation message and set print length depending on string length.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        usr: str
            String denoting the Redditor's username

        Returns
        -------
        None
        """

        export_option = "JSON" \
            if not args.csv \
            else "CSV"

        confirmation = "\n%s file for u/%s created." % (export_option, user)

        print(Style.BRIGHT + Fore.GREEN + confirmation)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(confirmation) - 1))

    @staticmethod
    def write(args, reddit, u_master):
        """
        Get, sort, then write scraped Redditor information to CSV or JSON.

        Calls previously defined public methods:

            GetInteractions().get()
            Write._determine_export()
            Write._print_confirm()

        Calls a public method from an external module:

            NameFile().u_fname(limit, user)

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        u_master: dict
            Dictionary containing all scrape settings

        Returns
        -------
        None
        """

        for user, limit in u_master.items():
            data = GetInteractions().get(limit, reddit, user)
            f_name = NameFile().u_fname(limit, user)

            Write._determine_export(args, data, f_name)
            Write._print_confirm(args, user)

class RunRedditor():
    """
    Run the Redditor scraper.
    """

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer(s_t[1])
    def run(args, parser, reddit):
        """
        Get, sort, then write scraped Redditor information to CSV or JSON.

        Calls previously defined public methods:

            CheckRedditors().list_redditors()
            Write.write()

        Calls public methods from external modules: 

            GetPRAWScrapeSettings().create_list()
            Global.make_none_dict()
            GetPRAWScrapeSettings().get_settings()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI 
        parser: ArgumentParser
            argparse ArgumentParser object
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        None
        """

        PRAWTitles.u_title()

        user_list = GetPRAWScrapeSettings().create_list(args, s_t[1])
        users = CheckRedditors().list_redditors(parser, reddit, user_list)
        u_master = make_none_dict(users)
        GetPRAWScrapeSettings().get_settings(args, u_master, s_t[1])

        Write.write(args, reddit, u_master)
