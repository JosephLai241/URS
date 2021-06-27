"""
Submission comments scraper
===========================
Defining methods for the submission comments scraper.
"""


import logging

from colorama import (
    Fore, 
    Style
)
from halo import Halo

from urs.praw_scrapers.utils.Objectify import Objectify
from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import (
    EncodeNode,
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

class CommentNode():
    """
    Defining a node object that stores comment metadata for the comments tree.
    """

    def __init__(self, metadata):
        """
        Set the node's comment data.

            self.__setattr__(key, value): set node attributes based on the `metadata`
                dictionary
            self.replies: list containing CommentNodes

        Parameters
        ----------
        metadata: dict
            Dictionary containing comment metadata

        Returns
        -------
        None
        """

        for key, value in metadata.items():
            self.__setattr__(key, value)

        self.replies = []

class Forest():
    """
    Methods to nurture the comment forest.
    """

    def __init__(self, submission, url):
        """
        Initialize the collective root.

            self.root: list containing CommentNodes

        Parameters
        ----------
        submission: PRAW submission object
        url: str
            String denoting the submission's url

        Returns
        -------
        None
        """

        self.root = CommentNode({ "id": submission.id_from_url(url) })
    
    def _dfs_insert(self, new_comment):
        """
        An iterative implementation of depth-first search to insert a new comment 
        into a comment tree.

        Parameters
        ----------
        new_comment: CommentNode

        Returns
        -------
        None
        """

        stack = []
        stack.append(self.root)
        
        visited = set()
        visited.add(self.root)

        found = False
        while not found:
            current_comment = stack.pop(0)
            
            for reply in current_comment.replies:
                if new_comment.parent_id.split("_", 1)[1] == reply.id:
                    reply.replies.append(new_comment)
                    found = True
                else:
                    if reply not in visited:
                        stack.insert(0, reply)
                        visited.add(reply)

    def seed(self, new_comment):
        """
        Insert a new CommentNode into a comment tree within the Forest.

        Calls previously defined private method:

            self._dfs_insert()

        Parameters
        ----------
        new_comment: CommentNode

        Returns
        -------
        None
        """

        parent_id = new_comment.parent_id.split("_", 1)[1]

        self.root.replies.append(new_comment) \
            if parent_id == getattr(self.root, "id") \
            else self._dfs_insert(new_comment)

class SortComments():
    """
    Methods for sorting comments depending on which style of comments was 
    specified (raw or structured).
    """

    @staticmethod
    def sort_raw(all_comments, submission):
        """
        Sort all comments in raw format. 

        Calls a public method from an external module:

            Objectify().make_comment()
        
        Parameters
        ----------
        all_comments: list
            List containing all comments within a submission
        submission: PRAW submission object
            Reddit submission object

        Returns
        -------
        None
        """

        for comment in submission.comments.list():
            all_comments.append(Objectify().make_comment(comment, False))

    @staticmethod
    def sort_structured(submission, url):
        """
        Sort all comments in structured format. 
        
        Calls previously defined public methods:

            CommentNode()
            Forest()
            Forest().seed()

        Calls public methods from external modules:

            EncodeNode().encode()
            Objectify().make_comment()

        Parameters
        ----------
        submission: PRAW submission object
        url: str
            String denoting the submission's url

        Returns
        -------
        replies: list
            List containing `CommentNode`s
        """
        
        forest = Forest(submission, url)

        seed_status = Status(
            "Forest has fully matured.",
            Fore.CYAN + Style.BRIGHT + "Seeding Forest.",
            "cyan"
        )

        seed_status.start()
        for comment in submission.comments.list():
            comment_node = CommentNode(Objectify().make_comment(comment, False))
            EncodeNode().encode(comment_node)

            forest.seed(comment_node)

        seed_status.succeed()
        return forest.root.replies

class GetSort():
    """
    Methods for getting comments from a Reddit submission.
    """

    def __init__(self, args, submission, url):
        """
        Initialize variables used in later methods:

            self._submission: PRAW submission object

        Calls replace_more() method on submission object to get nested comments.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        submission: PRAW submission object
        url: str
            String denoting the submission's url

        Returns
        -------
        None
        """

        self._args = args
        self._url = url

        more_comments_status = Status(
            "Finished resolving instances of MoreComments.",
            Fore.CYAN + Style.BRIGHT + "Resolving instances of MoreComments. This may take a while. Please wait.",
            "cyan"
        )

        more_comments_status.start()
        self._submission = submission
        self._submission.comments.replace_more(limit = None)
        more_comments_status.succeed()

    def get_sort(self, args, limit):
        """
        Get comments from posts. 
        
        Calls previously defined private methods:

            self._get_raw()
            self._get_structured()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        limit: str
            String denoting the number of results to return

        Returns
        -------
        all_comments: list
            List containing all comments within a submission
        """

        if args.raw:
            all_comments = []
            SortComments().sort_raw(all_comments, self._submission)
        else:
            all_comments = SortComments().sort_structured(self._submission, self._url)

        return all_comments[:int(limit)] \
            if int(limit) != 0 \
            else all_comments

class Write():
    """
    Methods for writing scraped comments to CSV or JSON.
    """

    @staticmethod
    def _make_json_skeleton(args, limit, submission, url):
        """
        Create a skeleton for JSON export. Include scrape details at the top.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        limit: str
            Integer of string type denoting n_results or RAW format
        submission: PRAW submission object
        url: str
            String denoting submission URL


        Returns
        -------
        skeleton: dict
            Dictionary containing scrape settings and all scrape data
        """

        metadata_status = Status(
            "Extracted submission metadata.",
            "Extracting submission metadata.",
            "white"
        )

        metadata_status.start()
        skeleton = {
            "scrape_settings": {
                "n_results": int(limit) \
                    if int(limit) > 0 \
                    else "all",
                "style": "structured" \
                    if not args.raw \
                    else "raw",
                "url": url
            },
            "data": {
                "submission_metadata": {
                    "author": "u/" + submission.author.name \
                        if hasattr(submission.author, "name") \
                        else "[deleted]",
                    "created_utc": convert_time(submission.created_utc),
                    "distinguished": submission.distinguished,
                    "edited": submission.edited \
                        if submission.edited == False \
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
                    "upvote_ratio": submission.upvote_ratio
                },
                "comments": None
            }
        }

        try:
            skeleton["data"]["submission_metadata"]["gallery_data"] = submission.gallery_data
            skeleton["data"]["submission_metadata"]["media_metadata"] = submission.media_metadata

            skeleton["data"]["submission_metadata"] = dict(sorted(skeleton["data"]["submission_metadata"].items()))
        except AttributeError:
            pass

        metadata_status.succeed()

        return skeleton

    @staticmethod
    def _determine_export(args, data, f_name):
        """
        Export either structured or raw comments.

        Calls a public method from an external module:

            Export.export()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        data: dict
            Dictionary containing all scraped data
        f_name: str
            String denoting the filename

        Returns
        -------
        None
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
    def write(args, c_master, reddit):
        """
        Get, sort, then write scraped comments to CSV or JSON.

        Calls previously defined public and private methods:

            GetSort().get_sort()

            Write._determine_export()
            Write._make_json_skeleton()
            Write._print_confirm()

        Calls a public method from an external module:

            NameFile().c_fname()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        c_master: dict
            Dictionary containing all scrape settings
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        None
        """

        for url, limit in c_master.items():
            submission = reddit.submission(url = url)
            data = Write._make_json_skeleton(args, limit, submission, url)
            data["data"]["comments"] = GetSort(args, submission, url).get_sort(args, limit)
            
            f_name = NameFile().c_fname(args, limit, submission.title)
            Write._determine_export(args, data, f_name)

            print()
            Halo(color = "green", text = Style.BRIGHT + Fore.GREEN + f"JSON file for '{submission.title}' comments created.").succeed()
            print()

class RunComments():
    """
    Run the comments scraper.
    """

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer("comments")
    def run(args, parser, reddit):
        """
        Run comments scraper.

        Calls a previously defined public method:

            Write.write()

        Calls public methods from external modules:

            GetPRAWScrapeSettings().create_list()
            Validation.validate()
            GetPRAWScrapeSettings().get_settings()
            Global.make_none_dict()

            PRAWTitles.c_title()

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
        c_master: dict
            Dictionary containing all submission comments scrape settings
        """

        PRAWTitles.c_title()

        post_list = GetPRAWScrapeSettings().create_list(args, "comments")
        not_posts, posts = Validation.validate(post_list, reddit, "comments")
        c_master = make_none_dict(posts)
        GetPRAWScrapeSettings().get_settings(args, not_posts, c_master, "comments")

        Write.write(args, c_master, reddit)

        return c_master
