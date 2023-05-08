"""
Redditor scraper
================
Defining methods for the Redditor scraper.
"""


from argparse import Namespace
from typing import Any, Dict, List, Tuple, Union

from colorama import Fore, Style
from halo import Halo
from praw import Reddit
from praw.models import Comment, Redditor, Submission
from prawcore import PrawcoreException

from urs.praw_scrapers.utils.Objectify import Objectify
from urs.praw_scrapers.utils.Validation import Validation
from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import Export, NameFile
from urs.utils.Global import convert_time, make_none_dict
from urs.utils.Logger import LogExport, LogPRAWScraper
from urs.utils.Titles import PRAWTitles


class ProcessInteractions:
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

    def __init__(
        self, limit: int, redditor: Redditor, skeleton: Dict[str, Any]
    ) -> None:
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

        :param int limit: The number of results to return.
        :param Redditor redditor: A PRAW Redditor object.
        :param dict[str, Any] skeleton: A `dict[str, Any]` containing all Redditor
            data.
        """

        self._skeleton = skeleton

        self._comments = redditor.comments.new(limit=limit)
        self._controversial = redditor.controversial(limit=limit)
        self._downvoted = redditor.downvoted(limit=limit)
        self._gilded = redditor.gilded(limit=limit)
        self._gildings = redditor.gildings(limit=limit)
        self._hidden = redditor.hidden(limit=limit)
        self._hot = redditor.hot(limit=limit)
        self._moderated = redditor.moderated()
        self._multireddits = redditor.multireddits()
        self._new = redditor.new(limit=limit)
        self._saved = redditor.saved(limit=limit)
        self._submissions = redditor.submissions.new(limit=limit)
        self._top = redditor.top(limit=limit)
        self._upvoted = redditor.upvoted(limit=limit)

    def _extract(self, obj: List[Union[Comment, Submission]], scrape_type: str) -> None:
        """
        Extracting submission or comment attributes and appending to the skeleton.

        :param list[Comment | Submission] obj: A list of PRAW Redditor objects
            that may contain submissions or comments.
        :param str scrape_type: The scrape type field within the skeleton.
        """

        for item in obj:
            redditor_item = (
                Objectify().make_submission(True, item)
                if isinstance(item, Submission)
                else Objectify().make_comment(item, True)
            )

            self._skeleton["data"]["interactions"][scrape_type].append(redditor_item)

    @Halo(color="white", text="Extracting submissions.")
    def get_submissions(self) -> None:
        """
        Get Redditor submissions.
        """

        self._extract(self._submissions, "submissions")

    @Halo(color="white", text="Extracting comments.")
    def get_comments(self) -> None:
        """
        Get Redditor comments.
        """

        self._extract(self._comments, "comments")

    @Halo(
        color="white",
        text="Extracting Controversial, Gilded, Hot, New, and Top interactions.",
    )
    def get_mutts(self) -> None:
        """
        Get Controversial, Gilded, Hot, New, and Top Redditor posts. The ListingGenerator
        returns a mix of submissions and comments, so handling each differently is
        necessary.
        """

        mutt_interactions = [
            self._controversial,
            self._gilded,
            self._hot,
            self._new,
            self._top,
        ]
        mutt_names = ["controversial", "gilded", "hot", "new", "top"]

        for category, interaction in zip(mutt_names, mutt_interactions):
            self._extract(interaction, category)

    def get_access(self) -> None:
        """
        Get Upvoted, Downvoted, Gildings, Hidden, and Saved Redditor posts. These
        lists tend to raise a 403 HTTP Forbidden exception, so naturally exception
        handling is necessary.
        """

        access_interactions = [
            self._downvoted,
            self._gildings,
            self._hidden,
            self._saved,
            self._upvoted,
        ]
        access_names = ["downvoted", "gildings", "hidden", "saved", "upvoted"]

        access_halo = Halo(
            color="white",
            text="Extracting Upvoted, Downvoted, Gildings, Hidden, and Saved interactions.",
        )

        access_halo.start()
        for category, interaction in zip(access_names, access_interactions):
            try:
                self._extract(interaction, category)
            except PrawcoreException as error:
                access_halo.warn(
                    Fore.YELLOW
                    + f"Access to {category.capitalize()} interactions forbidden: {error}. SKIPPING."
                )
                self._skeleton["data"]["interactions"][f"{category}"].append(
                    "FORBIDDEN"
                )

    @Halo(color="white", text="Extracting moderated Subreddits.")
    def get_moderated(self) -> None:
        """
        Get Redditor's moderated Subreddits.
        """

        if self._moderated:
            for subreddit in self._moderated:
                subreddit = Objectify().make_subreddit(subreddit)
                self._skeleton["data"]["interactions"]["moderated"].append(subreddit)

    @Halo(color="white", text="Extracting multireddits.")
    def get_multireddits(self) -> None:
        """
        Get Redditor's multireddits.
        """

        if self._multireddits:
            for multireddit in self._multireddits:
                multireddit = Objectify().make_multireddit(multireddit)
                self._skeleton["data"]["interactions"]["multireddits"].append(
                    multireddit
                )


class GetInteractions:
    """
    Methods for getting Redditor information and interactions.
    """

    @staticmethod
    def _make_json_skeleton(
        limit: str, reddit: Reddit, redditor_name: str
    ) -> Tuple[Redditor, Dict[str, Any]]:
        """
        Create a skeleton for JSON export. Include scrape details at the top.

        :param str limit: The number of results to return.
        :param Reddit reddit: PRAW Reddit object.
        :param str redditor: The Redditor's name.

        :returns: The Redditor instance and a `dict[str, Any]` containing all
            Redditor data.
        :rtype: `(Redditor, dict[str, Any])`
        """

        plurality = "results" if int(limit) > 1 else "result"

        Halo().info(f"Processing {limit} {plurality} from u/{redditor_name}'s profile.")

        skeleton = {
            "scrape_settings": {"redditor": redditor_name, "n_results": limit},
            "data": {"information": None, "interactions": {}},
        }
        redditor = reddit.redditor(redditor_name)

        return redditor, skeleton

    @staticmethod
    def _get_trophies(redditor: Redditor) -> Union[List[Dict[str, Any]], None]:
        """
        Get Redditor's trophies.

        :param Redditor redditor: The Redditor instance.

        :returns: A `list[str, Any]` containing Redditor trophies, or `None` if
            the Redditor does not have any trophies.
        :rtype: `list[dict[str, Any]] | None`
        """

        if redditor.trophies():
            return [
                {
                    "award_id": trophy.award_id,
                    "description": trophy.description,
                    "icon_40": trophy.icon_40,
                    "icon_70": trophy.icon_70,
                    "name": trophy.name,
                    "url": trophy.url,
                }
                for trophy in redditor.trophies()
            ]

    @staticmethod
    def _get_user_subreddit(redditor: Redditor) -> Dict[str, Any]:
        """
        Get Redditor's Subreddit.

        :param Redditor redditor: The Redditor instance.

        :returns: A `dict[str, Any]` containing Redditor Subreddit data.
        :rtype: `dict[str, Any]`
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
            "user_is_subscriber": subreddit.user_is_subscriber,
        }

    @staticmethod
    @Halo(color="white", text="Extracting Redditor information.")
    def _get_user_info(redditor: Redditor, skeleton: Dict[str, Any]) -> None:
        """
        Get Redditor account information.

        :param Redditor redditor: The Redditor instance.
        :param dict[str, Any] skeleton: A `dict[str, Any]` containing all Redditor
            data.
        """

        try:
            skeleton["data"]["information"] = {
                "is_suspended": redditor.is_suspended,
                "name": redditor.name,
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
                "trophies": GetInteractions._get_trophies(redditor),
            }

    @staticmethod
    def _make_interactions_lists(skeleton: Dict[str, Any]) -> None:
        """
        Make empty lists for each Redditor interaction field.

        :param dict[str, Any] skeleton: A `dict[str, Any]` containing all Redditor
            data.
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
    def _get_user_interactions(
        limit: str, redditor: Redditor, skeleton: Dict[str, Any]
    ) -> None:
        """
        Get Redditor interactions on Reddit.

        :param str limit: The number of results to return.
        :param Redditor redditor: A PRAW Redditor object.
        :param dict[str, Any] skeleton: A `dict[str, Any]` containing all Redditor
            data.
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
    def get(limit: str, reddit: Reddit, redditor_name: str) -> Dict[str, Any]:
        """
        Get Redditor information and interactions.

        :param str limit: The number of results to return.
        :param Reddit reddit: PRAW Reddit object.
        :param str redditor_name: The name of the Redditor.

        :returns: A `dict[str, Any]` containing all Redditor data.
        :rtype: `dict[str, Any]`
        """

        redditor, skeleton = GetInteractions._make_json_skeleton(
            limit, reddit, redditor_name
        )
        GetInteractions._get_user_info(redditor, skeleton)
        GetInteractions._get_user_interactions(limit, redditor, skeleton)

        return skeleton


class Write:
    """
    Methods for writing scraped Redditor information to CSV or JSON.
    """

    @staticmethod
    def write(reddit: Reddit, u_master: Dict[str, Any]) -> None:
        """
        Get, sort, then write scraped Redditor information to CSV or JSON.

        :param Reddit reddit: PRAW Reddit object.
        :param dict[str, Any] u_master: A `dict[str, Any]` containing all scrape
            settings.
        """

        for redditor, limit in u_master.items():
            data = GetInteractions.get(limit, reddit, redditor)
            f_name = NameFile().u_fname(limit, redditor)

            Export.export(data, f_name, "json", "redditors")

            print()
            Halo().succeed(
                Style.BRIGHT + Fore.GREEN + f"JSON file for u/{redditor} created."
            )
            print()


class RunRedditor:
    """
    Run the Redditor scraper.
    """

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer("redditor")
    def run(args: Namespace, reddit: Reddit) -> Dict[str, Any]:
        """
        Get, sort, then write scraped Redditor information to CSV or JSON.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param Reddit reddit: PRAW Reddit object.

        :returns: A `dict[str, Any]` containing all Redditor scrape settings.
        :rtype: `dict[str, Any]`
        """

        PRAWTitles.u_title()

        user_list = GetPRAWScrapeSettings().create_list(args, "redditor")
        not_users, users = Validation.validate(user_list, reddit, "redditor")
        u_master = make_none_dict(users)
        GetPRAWScrapeSettings().get_settings(args, not_users, u_master, "redditor")

        Write.write(reddit, u_master)

        return u_master
