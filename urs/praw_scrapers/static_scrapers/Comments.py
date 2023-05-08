"""
Submission comments scraper
===========================
Defining methods for the submission comments scraper.
"""


import json
import logging
from argparse import Namespace
from typing import Any, Dict, List

from colorama import Fore, Style
from halo import Halo
from praw import Reddit
from praw.models import Submission
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    RenderableColumn,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from taisun.comments_utils import CommentNode, Forest

from urs.praw_scrapers.utils.Objectify import Objectify
from urs.praw_scrapers.utils.Validation import Validation
from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import Export, NameFile
from urs.utils.Global import Status, convert_time, make_none_dict
from urs.utils.Logger import LogExport, LogPRAWScraper
from urs.utils.Titles import PRAWTitles


class SortComments:
    """
    Methods for sorting comments depending on which style of comments was
    specified (raw or structured).
    """

    @staticmethod
    def sort_raw(all_comments: List[Dict[str, Any]], submission: Submission) -> None:
        """
        Sort all comments in raw format.

        :param list[dict[str, Any]] all_comments: A `list[dict[str, Any]]` containing
            all comments within a submission.
        :param Submission submission: PRAW `Submission` object.
        """

        for comment in submission.comments.list():
            all_comments.append(Objectify().make_comment(comment, False))

    @staticmethod
    def sort_structured(submission: Submission, url: str) -> List[Dict[str, Any]]:
        """
        Sort all comments in structured format.

        :param Submission submission: PRAW `Submission` object.
        :param str url: The submission's URL.

        :returns: A `list[dict[str, Any]]` containing `CommentNode`s in `dict`
            form.
        :rtype: `list[dict[str, Any]]`
        """

        renderable_column = RenderableColumn(renderable="|")
        spinner_column = SpinnerColumn(spinner_name="noise")
        text_column = TextColumn("Seeding Forest")

        progress_bar = Progress(
            spinner_column,
            text_column,
            BarColumn(),
            MofNCompleteColumn(),
            renderable_column,
            TimeRemainingColumn(),
        )

        forest = Forest(submission.id_from_url(url))

        with progress_bar:
            for comment in progress_bar.track(submission.comments.list()):
                comment_node = CommentNode(
                    json.dumps((Objectify().make_comment(comment, False)))
                )

                forest.seed_comment(comment_node)

        return forest.root.replies


class GetSort:
    """
    Methods for getting comments from a Reddit submission.
    """

    def __init__(self, args: Namespace, submission: Submission, url: str) -> None:
        """
        Initialize variables used in later methods:

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param Submission submission: PRAW `Submission` object.
        :param str url: The submission's URL.
        """

        self._args = args
        self._url = url

        more_comments_status = Status(
            "Finished resolving instances of MoreComments.",
            Fore.CYAN
            + Style.BRIGHT
            + "Resolving instances of MoreComments. This may take a while. Please wait.",
            "cyan",
        )

        more_comments_status.start()
        self._submission = submission
        self._submission.comments.replace_more(limit=None)
        more_comments_status.succeed()

    def get_sort(self, args: Namespace, limit: str) -> List[Dict[str, Any]]:
        """
        Get comments from posts.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param str limit: A `str` indicating the number of results to return.

        :returns: A `list[dict[str, Any]]` containing all comments within a submission.
        :rtype: `list[dict[str, Any]]`
        """

        if args.raw:
            all_comments = []
            SortComments().sort_raw(all_comments, self._submission)
        else:
            all_comments = SortComments().sort_structured(self._submission, self._url)

        return all_comments[: int(limit)] if int(limit) != 0 else all_comments


class Write:
    """
    Methods for writing scraped comments to CSV or JSON.
    """

    @staticmethod
    def _make_json_skeleton(
        args: Namespace, limit: str, submission: Submission, url: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create a skeleton for JSON export. Include scrape details at the top.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param str limit: A `str` indicating the number of results to return.
        :param Submission submission: PRAW `Submission` object.
        :param str url: The submission's URL.

        :returns: A `dict[str, dict[str, Any]]` containing scrape settings and
            all scrape data.
        :rtype: `dict[str, dict[str, Any]]`
        """

        metadata_status = Status(
            "Extracted submission metadata.", "Extracting submission metadata.", "white"
        )

        metadata_status.start()
        skeleton = {
            "scrape_settings": {
                "n_results": int(limit) if int(limit) > 0 else "all",
                "style": "structured" if not args.raw else "raw",
                "url": url,
            },
            "data": {
                "submission_metadata": {
                    "author": "u/" + submission.author.name
                    if hasattr(submission.author, "name")
                    else "[deleted]",
                    "created_utc": convert_time(submission.created_utc),
                    "distinguished": submission.distinguished,
                    "edited": submission.edited
                    if submission.edited == False
                    else convert_time(submission.edited),
                    "is_original_content": submission.is_original_content,
                    "is_self": submission.is_self,
                    "link_flair_text": submission.link_flair_text,
                    "locked": submission.locked,
                    "nsfw": submission.over_18,
                    "num_comments": submission.num_comments,
                    "permalink": submission.permalink,
                    "score": submission.score,
                    "selftext": submission.selftext,
                    "spoiler": submission.spoiler,
                    "stickied": submission.stickied,
                    "subreddit": submission.subreddit.display_name,
                    "title": submission.title,
                    "upvote_ratio": submission.upvote_ratio,
                },
                "comments": None,
            },
        }

        try:
            skeleton["data"]["submission_metadata"][
                "gallery_data"
            ] = submission.gallery_data
            skeleton["data"]["submission_metadata"][
                "media_metadata"
            ] = submission.media_metadata

            skeleton["data"]["submission_metadata"] = dict(
                sorted(skeleton["data"]["submission_metadata"].items())
            )
        except AttributeError:
            pass

        metadata_status.succeed()

        return skeleton

    @staticmethod
    def _determine_export(args: Namespace, data: Dict[str, Any], f_name: str) -> None:
        """
        Export either structured or raw comments.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param dict[str, Any] data: A `dict[str, Any]` containing all scraped data.
        :param str f_name: The filename.
        """

        if args.raw:
            export_status = f"Exporting {data['scrape_settings']['n_results']} comments in raw format."
            Halo().info(export_status)
            logging.info(export_status)
            Export.export(data, f_name, "json", "comments")
        else:
            export_status = f"Exporting {data['scrape_settings']['n_results']} comments in structured format."
            Halo().info(export_status)
            logging.info(export_status)
            Export.write_structured_comments(data, f_name)

    @staticmethod
    def write(args: Namespace, c_master: Dict[str, Any], reddit: Reddit):
        """
        Get, sort, then write scraped comments to CSV or JSON.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param dict[str, Any] data: A `dict[str, Any]` containing all scraped data.
        :param Reddit reddit: PRAW Reddit instance.
        """

        for url, limit in c_master.items():
            submission = reddit.submission(url=url)
            data = Write._make_json_skeleton(args, limit, submission, url)
            data["data"]["comments"] = GetSort(args, submission, url).get_sort(
                args, limit
            )

            f_name = NameFile().c_fname(args, limit, submission.title)
            Write._determine_export(args, data, f_name)

            print()
            Halo(
                color="green",
                text=Style.BRIGHT
                + Fore.GREEN
                + f"JSON file for '{submission.title}' comments created.",
            ).succeed()
            print()


class RunComments:
    """
    Run the comments scraper.
    """

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer("comments")
    def run(args: Namespace, reddit: Reddit) -> Dict[str, Any]:
        """
        Run comments scraper.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param Reddit reddit: PRAW Reddit instance.

        :returns: A `dict[str, Any]` containing all submission comments scrape
            settings.
        :rtype: `dict[str, Any]`
        """

        PRAWTitles.c_title()

        post_list = GetPRAWScrapeSettings().create_list(args, "comments")
        not_posts, posts = Validation.validate(post_list, reddit, "comments")
        c_master = make_none_dict(posts)
        GetPRAWScrapeSettings().get_settings(args, not_posts, c_master, "comments")

        Write.write(args, c_master, reddit)

        return c_master
