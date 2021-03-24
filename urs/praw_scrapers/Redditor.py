"""
Redditor scraper
================
Defining methods for the Redditor scraper.
"""


import logging
import praw

from colorama import (
    init, 
    Fore, 
    Style
)
from halo import Halo
from prawcore import PrawcoreException

from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import (
    Export,
    NameFile
)
from urs.utils.Global import (
    convert_time,
    make_none_dict,
    Status
)
from urs.utils.Logger import (
    LogError,
    LogExport, 
    LogPRAWScraper
)
from urs.utils.Titles import PRAWTitles

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class Objectify():
    """
    Methods for creating Reddit objects based on metadata.
    """

    def make_subreddit(self, subreddit):
        """
        Make a Subreddit object.

        Calls a public method from an external module:

            Global.convert_time()

        Parameters
        ----------
        subreddit: PRAW Subreddit object

        Returns
        -------
        subreddit_object: dict
            Dictionary containing Subreddit metadata
        """

        return {
            "can_assign_link_flair": subreddit.can_assign_link_flair,
            "can_assign_user_flair": subreddit.can_assign_user_flair,
            "created_utc": convert_time(subreddit.created_utc),
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

    def make_submission(self, submission):
        """
        Make a submission object.

        Calls a previously defined public method:

            self.make_subreddit()

        Calls a public method from an external module:

            Global.convert_time()

        Parameters
        ----------
        submission: PRAW submission object

        Returns
        -------
        submission_object: dict
            Dictionary containing submission metadata
        """

        return {
            "type": "submission",
            "author": "u/" + submission.author.name \
                if hasattr(submission.author, "name") \
                else "[deleted]",
            "created_utc": convert_time(submission.created_utc),
            "distinguished": submission.distinguished,
            "edited": submission.edited \
                if submission.edited != False \
                else convert_time(submission.edited),
            "id": submission.id,
            "is_original_content": submission.is_original_content,
            "is_self": submission.is_self,
            "link_flair_text": submission.link_flair_text,
            "locked": submission.locked,
            "name": submission.name,
            "num_comments": submission.num_comments,
            "nsfw": submission.over_18,
            "permalink": submission.permalink,
            "score": submission.score,
            "selftext": submission.selftext,
            "spoiler": submission.spoiler,
            "stickied": submission.stickied,
            "subreddit": self.make_subreddit(submission.subreddit),
            "title": submission.title,
            "upvote_ratio": submission.upvote_ratio,
            "url": submission.url
        }

    def make_comment(self, comment):
        """
        Make a comment item. 
        
        Calls previously defined public method:

            self.make_submission()

        Calls a public method from an external module:

            Global.convert_time()

        Parameters
        ----------
        comment: PRAW comment object

        Returns
        -------
        redditor_item: dict
            Dictionary containing comment metadata
        """

        return {
            "type": "comment",
            "body": comment.body,
            "body_html": comment.body_html,
            "created_utc": convert_time(comment.created_utc),
            "distinguished": comment.distinguished,
            "edited": comment.edited \
                if comment.edited != False \
                else convert_time(comment.edited),
            "id": comment.id,
            "is_submitter": comment.is_submitter,
            "link_id": comment.link_id,
            "parent_id": comment.parent_id,
            "score": comment.score,
            "stickied": comment.stickied,
            "submission": self.make_submission(comment.submission),
            "subreddit_id": comment.subreddit_id
        }

    def make_multireddit(self, multireddit):
        """
        Make a multireddit item.

        Calls a previously defined public method:

            self.make_subreddit()

        Calls a public method from an external module:

            Global.convert_time()

        Parameters
        ----------
        multireddit: PRAW multireddit object

        Returns
        -------
        multireddit_object: dict
            Dictionary containing multireddit metadata
        """

        multireddit_object = {
            "can_edit": multireddit.can_edit,
            "copied_from": multireddit.copied_from,
            "created_utc": convert_time(multireddit.created_utc),
            "description_html": multireddit.description_html,
            "description_md": multireddit.description_md,
            "display_name": multireddit.display_name,
            "name": multireddit.name,
            "nsfw": multireddit.over_18,
            "subreddits": [],
            "visibility": multireddit.visibility
        }

        if multireddit.subreddits:
            for subreddit in multireddit.subreddits:
                subreddit = self.make_subreddit(subreddit)
                multireddit_object["subreddits"].append(subreddit) 

        return multireddit_object

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

        Calls previously defined public methodss:

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
            redditor_item = Objectify().make_submission(item) \
                if isinstance(item, praw.models.Submission) \
                else Objectify().make_comment(item)

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
                access_halo.warn(Fore.YELLOW + "Access to %s interactions forbidden: %s. SKIPPING." % (category.capitalize(), error))
                self._skeleton["data"]["interactions"]["%s" % category].append("FORBIDDEN")

    @Halo(color = "white", text = "Extracting moderated Subreddits.")
    def get_moderated(self):
        """
        Get Redditor's moderated Subreddits.

        Calls previously defined public methodss:

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
        
        Calls previously defined public methodss:

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
        redditor: PRAW Redditor object

        Returns
        -------
        skeleton: dict
            Dictionary containing all Redditor data
        redditor: PRAW Redditor object
        """

        plurality = "results" \
            if int(limit) > 1 \
            else "result"

        Halo().info("Processing %s %s from u/%s's profile." % (limit, plurality, redditor))
        
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
    @Halo(color = "white", text = "Extracting Redditor trophies.")
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
    @Halo(color = "white", text = "Extracting Redditor information.")
    def _get_user_info(redditor, skeleton):
        """
        Get Redditor account information.

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
                "subreddit": redditor.subreddit,
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
    def write(args, reddit, u_master):
        """
        Get, sort, then write scraped Redditor information to CSV or JSON.

        Calls a previously defined public method:

            GetInteractions.get()

        Calls a public method from an external module:

            NameFile().u_fname()

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

        for redditor, limit in u_master.items():
            data = GetInteractions.get(limit, reddit, redditor)
            f_name = NameFile().u_fname(limit, redditor)

            Export.export(data, f_name, "json", "redditors")
            
            print()
            Halo().succeed(Style.BRIGHT + Fore.GREEN + "JSON file for u/%s created." % redditor)
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
        not_users, users = Validation.validate(user_list, parser, reddit, "redditor")
        u_master = make_none_dict(users)
        GetPRAWScrapeSettings().get_settings(args, not_users, u_master, "redditor")

        Write.write(args, reddit, u_master)

        return u_master
