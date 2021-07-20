"""
Redditor scraper
================
Defining methods for the Redditor scraper.
"""


import logging
import praw

from colorama import (
    Fore, 
    Style
)
from halo import Halo
from prawcore import PrawcoreException

from urs.praw_scrapers.utils.Objectify import Objectify
from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import (
    Export,
    NameFile
)
from urs.utils.Global import (
    convert_time,
    make_none_dict
)
from urs.utils.Logger import (
    LogError,
    LogExport, 
    LogPRAWScraper
)
from urs.utils.Titles import PRAWTitles

class ProcessInteractions():
    """
    Methods for sorting and labeling comment or submission objects correctly.
     
    Some Redditor attributes will return a ListingGenerator which includes both 
    comments and submissions. These attributes will need to be sorted accordingly:
    - Downvoted (may be forbidden)
    - Gilded
    - Gildings (may be forbidden)
    - Hidden (may be forbidden)
    - Hot
    - New
    - Saved (may be forbidden)
    - Upvoted (may be forbidden)
    """

    def __init__(self, limit, redditor, skeleton):
        """
        Initialize variables used in later methods:

            self._skeleton: dictionary that contains all Redditor metadata and interactions

            self._comments: Redditor's comment objects
            self._controversial: Redditor's controversial objects
            self._downvoted: Redditor's downvoted objects
            self._gilded: Redditor's gilded objects
            self._gildings: Redditor's gildings objects
            self._hidden: Redditor's hidden objects
            self._hot: Redditor's hot objects
            self._moderated: Redditor's moderated objects
            self._multireddits: Redditor's multireddits
            self._new: Redditor's new objects
            self._saved: Redditor's saved objects
            self._submissions: Redditor's submission objects
            self._top: Redditor's top objects
            self._upvoted: Redditor's upvoted objects
            
        Parameters
        ----------
        limit: int
            Integer denoting n_results to return
        redditor: PRAW object
        skeleton: dict
            Dictionary containing all Redditor data

        Returns
        -------
        None
        """

        self._skeleton = skeleton

        self._comments = redditor.comments.new(limit = limit)
        self._controversial = redditor.controversial(limit = limit)
        self._downvoted = redditor.downvoted(limit = limit)
        self._gilded = redditor.gilded(limit = limit)
        self._gildings = redditor.gildings(limit = limit)
        self._hidden = redditor.hidden(limit = limit)
        self._hot = redditor.hot(limit = limit)
        self._moderated = redditor.moderated()
        self._multireddits = redditor.multireddits()
        self._new = redditor.new(limit = limit)
        self._saved = redditor.saved(limit = limit)
        self._submissions = redditor.submissions.new(limit = limit)
        self._top = redditor.top(limit = limit)
        self._upvoted = redditor.upvoted(limit = limit)

    def _extract(self, obj, scrape_type):
        """
        Extracting submission or comment attributes and appending to the skeleton.

        Calls public methods from an external module:

            Objectify().make_submission()
            Objectify().make_comment()

        Parameters
        ----------
        obj: PRAW object
            PRAW Redditor object that may contain Redditor submissions or comments 
        scrape_type: str
            String denoting the field within the skeleton

        Returns
        -------
        None
        """

        for item in obj:
            redditor_item = Objectify().make_submission(True, item) \
                if isinstance(item, praw.models.Submission) \
                else Objectify().make_comment(item, True)

            self._skeleton["data"]["interactions"][scrape_type].append(redditor_item)

    @Halo(color = "white", text = "Extracting submissions.")
    def get_submissions(self):
        """
        Get Redditor submissions. 
        
        Calls previously defined private method:

            self._extract()
        """

        self._extract(self._submissions, "submissions")

    @Halo(color = "white", text = "Extracting comments.")
    def get_comments(self):
        """
        Get Redditor comments. 
        
        Calls previously defined private method:

            self._extract()
        """

        self._extract(self._comments, "comments")

    @Halo(color = "white", text = "Extracting Controversial, Gilded, Hot, New, and Top interactions.")
    def get_mutts(self):
        """
        Get Controversial, Gilded, Hot, New, and Top Redditor posts. The ListingGenerator
        returns a mix of submissions and comments, so handling each differently is
        necessary. 
        
        Calls previously defined private method:

            self._extract()
        """

        mutt_interactions = [
            self._controversial, 
            self._gilded, 
            self._hot, 
            self._new, 
            self._top
        ]
        mutt_names = [
            "controversial", 
            "gilded", 
            "hot", 
            "new", 
            "top"
        ]

        for category, interaction in zip(mutt_names, mutt_interactions):
            self._extract(interaction, category)
            
    def get_access(self):
        """
        Get Upvoted, Downvoted, Gildings, Hidden, and Saved Redditor posts. These
        lists tend to raise a 403 HTTP Forbidden exception, so naturally exception
        handling is necessary. 
        
        Calls previously defined private method:

            self._extract()
        """

        access_interactions = [
            self._downvoted, 
            self._gildings, 
            self._hidden, 
            self._saved, 
            self._upvoted
        ]
        access_names = [
            "downvoted", 
            "gildings", 
            "hidden", 
            "saved", 
            "upvoted"
        ]

        access_halo = Halo(color = "white", text = "Extracting Upvoted, Downvoted, Gildings, Hidden, and Saved interactions.")

        access_halo.start()
        for category, interaction in zip(access_names, access_interactions):
            try:
                self._extract(interaction, category)
            except PrawcoreException as error:
                access_halo.warn(Fore.YELLOW + f"Access to {category.capitalize()} interactions forbidden: {error}. SKIPPING.")
                self._skeleton["data"]["interactions"][f"{category}"].append("FORBIDDEN")

    @Halo(color = "white", text = "Extracting moderated Subreddits.")
    def get_moderated(self):
        """
        Get Redditor's moderated Subreddits.

        Calls a public method from an external module:

            Objectify().make_subreddit()
        """

        if self._moderated:
            for subreddit in self._moderated:
                subreddit = Objectify().make_subreddit(subreddit)
                self._skeleton["data"]["interactions"]["moderated"].append(subreddit)

    @Halo(color = "white", text = "Extracting multireddits.")
    def get_multireddits(self):
        """
        Get Redditor's multireddits.
        
        Calls a public method from an external module:

            Objectify().make_multireddit()
        """

        if self._multireddits:
            for multireddit in self._multireddits:
                multireddit = Objectify().make_multireddit(multireddit)
                self._skeleton["data"]["interactions"]["multireddits"].append(multireddit)
        
class GetInteractions():
    """
    Methods for getting Redditor information and interactions.
    """

    @staticmethod
    def _make_json_skeleton(limit, reddit, redditor):
        """
        Create a skeleton for JSON export. Include scrape details at the top.

        Parameters
        ----------
        limit: str
            String denoting n_results returned
        reddit: PRAW Reddit object
        redditor: str
            String denoting the Redditor name

        Returns
        -------
        skeleton: dict
            Dictionary containing all Redditor data
        redditor: PRAW Redditor object
        """

        plurality = "results" \
            if int(limit) > 1 \
            else "result"

        Halo().info(f"Processing {limit} {plurality} from u/{redditor}'s profile.")
        
        skeleton = {
            "scrape_settings": {
                "redditor": redditor,
                "n_results": limit
            },
            "data": {
                "information": None,
                "interactions": {}
            }
        }
        redditor = reddit.redditor(redditor)

        return redditor, skeleton

    @staticmethod
    def _get_trophies(redditor):
        """
        Get Redditor's trophies.

        Parameters
        ----------
        redditor: PRAW Redditor object

        Returns
        -------
        trophies: list
            List containing Redditor trophies
        """

        if redditor.trophies():
            return [
                {
                    "award_id": trophy.award_id,
                    "description": trophy.description,
                    "icon_40": trophy.icon_40,
                    "icon_70": trophy.icon_70,
                    "name": trophy.name,
                    "url": trophy.url
                }
                for trophy in redditor.trophies()
            ]

    @staticmethod
    def _get_user_subreddit(redditor):
        """
        Get Redditor's Subreddit.

        Parameters
        ----------
        redditor: PRAW Redditor object

        Returns
        -------
        redditor_subreddit: dict
            Dictionary containing Redditor Subreddit data
        """

        subreddit = redditor.subreddit

        return {
            "can_assign_link_flair": subreddit.can_assign_link_flair,
            "can_assign_user_flair": subreddit.can_assign_user_flair,
            "created_utc": subreddit.created_utc,
            "description": subreddit.description,
            "description_html": subreddit.description_html,
            "display_name": subreddit.display_name,
            "id": subreddit.id,
            "name": subreddit.name,
            "nsfw": subreddit.over18,
            "public_description": subreddit.public_description,
            "spoilers_enabled": subreddit.spoilers_enabled,
            "subscribers": subreddit.subscribers,
            "user_is_banned": subreddit.user_is_banned,
            "user_is_moderator": subreddit.user_is_moderator,
            "user_is_subscriber": subreddit.user_is_subscriber
        }

    @staticmethod
    @Halo(color = "white", text = "Extracting Redditor information.")
    def _get_user_info(redditor, skeleton):
        """
        Get Redditor account information.

        Calls a previously defined public method:

            GetInteractions._get_trophies()

        Calls a public method from an external module:

            Global.convert_time()

        Parameters
        ----------
        redditor: PRAW Redditor object
        skeleton: dict
            Dictionary containing all Redditor data

        Returns
        -------
        None
        """

        try:
            skeleton["data"]["information"] = {
                "is_suspended": redditor.is_suspended,
                "name": redditor.name
            }
        except AttributeError:
            skeleton["data"]["information"] = {
                "comment_karma": redditor.comment_karma,
                "created_utc": convert_time(redditor.created_utc),
                "fullname": redditor.fullname,
                "has_verified_email": redditor.has_verified_email,
                "icon_img": redditor.icon_img,
                "id": redditor.id,
                "is_employee": redditor.is_employee,
                "is_friend": redditor.is_friend,
                "is_mod": redditor.is_mod,
                "is_gold": redditor.is_gold,
                "link_karma": redditor.link_karma,
                "name": redditor.name,
                "subreddit": GetInteractions._get_user_subreddit(redditor),
                "trophies": GetInteractions._get_trophies(redditor)
            }

    @staticmethod
    def _make_interactions_lists(skeleton):
        """
        Make empty lists for each Redditor interaction field.

        Parameters
        ----------
        skeleton: dict
            Dictionary containing all Redditor data

        Returns
        -------
        None
        """

        interaction_titles = [ 
            "comments", 
            "controversial", 
            "downvoted", 
            "gilded", 
            "gildings", 
            "hidden", 
            "hot", 
            "moderated",
            "multireddits",
            "new", 
            "saved",
            "submissions", 
            "top", 
            "upvoted", 
        ]

        for interaction_title in interaction_titles:
            skeleton["data"]["interactions"][interaction_title] = []

    @staticmethod
    def _get_user_interactions(limit, redditor, skeleton):
        """
        Get Redditor interactions on Reddit.

        Calls previously defined private and public methods:

            GetInteractions._make_interactions_lists()

            ProcessInteractions()
            ProcessInteractions().get_submissions()
            ProcessInteractions().get_comments()
            ProcessInteractions().get_mutts()
            ProcessInteractions().get_moderated()
            ProcessInteractions().get_multireddits()
            ProcessInteractions().get_access()


        Parameters
        ----------
        limit: str
            String denoting n_results returned
        redditor: PRAW Redditor object
        skeleton: dict
            Dictionary containing all Redditor data

        Returns
        -------
        None
        """

        GetInteractions._make_interactions_lists(skeleton)

        interactions = ProcessInteractions(int(limit), redditor, skeleton)
        interactions.get_submissions()
        interactions.get_comments()
        interactions.get_mutts()
        interactions.get_moderated()
        interactions.get_multireddits()
        interactions.get_access()

    @staticmethod
    def get(limit, reddit, redditor):
        """
        Get Redditor information and interactions.

        Calls previously defined private methods:

            GetInteractions._make_json_skeleton()
            GetInteractions._get_user_info()
            GetInteractions._get_user_interactions()

        Parameters
        ----------
        limit: str
            String denoting n_results returned
        reddit: PRAW Reddit object
        redditor: PRAW Redditor object

        Returns
        -------
        skeleton: dict
            Dictionary containing all Redditor data
        """

        redditor, skeleton = GetInteractions._make_json_skeleton(limit, reddit, redditor)
        GetInteractions._get_user_info(redditor, skeleton)
        GetInteractions._get_user_interactions(limit, redditor, skeleton)

        return skeleton

class Write():
    """
    Methods for writing scraped Redditor information to CSV or JSON.
    """

    @staticmethod
    def write(reddit, u_master):
        """
        Get, sort, then write scraped Redditor information to CSV or JSON.

        Calls a previously defined public method:

            GetInteractions.get()

        Calls a public method from an external module:

            NameFile().u_fname()

        Parameters
        ----------
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        u_master: dict
            Dictionary containing all scrape settings

        Returns
        -------
        None
        """

        for redditor, limit in u_master.items():
            data = GetInteractions.get(limit, reddit, redditor)
            f_name = NameFile().u_fname(limit, redditor)

            Export.export(data, f_name, "json", "redditors")
            
            print()
            Halo().succeed(Style.BRIGHT + Fore.GREEN + f"JSON file for u/{redditor} created.")
            print()

class RunRedditor():
    """
    Run the Redditor scraper.
    """

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer("redditor")
    def run(args, parser, reddit):
        """
        Get, sort, then write scraped Redditor information to CSV or JSON.

        Calls a previously defined public method:

            Write.write()

        Calls public methods from external modules: 

            GetPRAWScrapeSettings().create_list()
            Validation.validate()
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
        u_master: dict
            Dictionary containing all Redditor scrape settings
        """

        PRAWTitles.u_title()

        user_list = GetPRAWScrapeSettings().create_list(args, "redditor")
        not_users, users = Validation.validate(user_list, reddit, "redditor")
        u_master = make_none_dict(users)
        GetPRAWScrapeSettings().get_settings(args, not_users, u_master, "redditor")

        Write.write(reddit, u_master)

        return u_master
