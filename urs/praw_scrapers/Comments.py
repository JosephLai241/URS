"""
Submission comments scraper
===========================
Defining methods for the submission comments scraper.
"""


import logging

from colorama import (
    init, 
    Fore, 
    Style
)
from halo import Halo

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
    s_t
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

class CheckSubmissions():
    """
    Method for printing found and invalid Reddit posts.
    """

    @staticmethod
    @LogError.log_none_left("submissions")
    def list_submissions(parser, post_list, reddit):
        """
        Check if submissions exist and list posts that are not found.

        Calls a method from an external module:

            Validation.existence()

        Parameters
        ----------
        parser: ArgumentParser
            argparse ArgumentParser object
        post_list: list
            List of submission URLs
        reddit: Reddit object
            Reddit instance created by PRAW API credentials

        Returns
        -------
        posts: list
            List of valid submission URLs
        """

        check_submissions_spinner = Halo(color = "white", text = "Validating submission(s).")
        
        check_submissions_spinner.start()
        logging.info("Validating submissions...")
        logging.info("")
        posts, not_posts = Validation.existence(s_t[2], post_list, parser, reddit, s_t)
        check_submissions_spinner.succeed("Finished submission validation.")
        print()

        if not_posts:
            print(Fore.YELLOW + Style.BRIGHT + "\nThe following submissions were not found and will be skipped:")
            print(Fore.YELLOW + Style.BRIGHT + "-" * 55)
            print(*not_posts, sep = "\n")

            logging.warning("Failed to validate the following submissions:")
            logging.warning("%s" % (not_posts))
            logging.warning("Skipping.")
            logging.info("")

        if not posts:
            logging.critical("ALL SUBMISSIONS FAILED VALIDATION.")
            raise ValueError
        
        return not_posts, posts

class GetComments():
    """
    Methods for getting comments from a post.
    """

    def __init__(self):
        """
        Initialize variables used in later methods:

            self._titles: list of comment attributes

        Returns
        -------
        None
        """

        self._titles = [
            "parent_id", 
            "comment_id", 
            "author", 
            "date_created", 
            "upvotes", 
            "text", 
            "edited", 
            "is_submitter", 
            "stickied"
        ]

    def _fix_attributes(self, comment):
        """
        If applicable, handle deleted Redditors or edited time.

        Calls a method from an external module:

            Global.convert_time()

        Parameters
        ----------
        comment: PRAW object

        Returns
        -------
        author_name: str
        edit_date: str
        """

        try:
            author_name = comment.author.name
        except AttributeError:
            author_name = "[deleted]"

        edit_date = comment.edited \
            if str(comment.edited).isalpha() \
            else convert_time(comment.edited)

        return author_name, edit_date

    def create_comment(self, comment):
        """
        Create a comment object containing comment metadata used when sorting.

        Calls methods from an external module:

            Global.make_none_dict()
            Global.convert_time()

        Parameters
        ----------
        comment: PRAW object

        Returns
        -------
        comment_object: dict
            Dictionary containing comment metadata
        """

        comment_object = make_none_dict(self._titles)

        author_name, edit_date = self._fix_attributes(comment)
        comment_attributes = [
            comment.parent_id, 
            comment.id, 
            author_name, 
            convert_time(comment.created_utc), 
            comment.score, 
            comment.body, 
            edit_date, 
            comment.is_submitter, 
            comment.stickied
        ]

        for title, attribute in zip(self._titles, comment_attributes):
            comment_object[title] = attribute
        
        return comment_object

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
    
    def _dfs_insert(self, existing_comment, new_comment):
        """
        An iterative implementation of depth-first search to insert a new comment 
        into a comment tree.

        Parameters
        ----------
        existing_comment: CommentNode
        new_comment: CommentNode

        Returns
        -------
        None
        """

        stack = []
        stack.append(existing_comment)
        
        visited = set()
        visited.add(existing_comment)

        found = False
        while not found:
            current_comment = stack.pop(0)
            
            for reply in current_comment.replies:
                if new_comment.parent_id.split("_", 1)[1] == reply.comment_id:
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
            else self._dfs_insert(self.root, new_comment)

class SortComments():
    """
    Methods for sorting comments depending on which style of comments was 
    specified (raw or structured).
    """

    @staticmethod
    def sort_raw(all_comments, submission):
        """
        Sort all comments in raw format. 
        
        Calls previously defined public method:

            GetComments().create_comment()

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
            all_comments.append(GetComments().create_comment(comment))

    @staticmethod
    def sort_structured(submission, url):
        """
        Sort all comments in structured format. 
        
        Calls previously defined public methods:

            CommentNode()
            Forest()
            Forest().seed()
            GetComments().create_comment()

        Calls a public method from an external module:

            EncodeNode().encode()

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

        forest_spinner = Halo(color = "cyan", text = Fore.CYAN + Style.BRIGHT + "Seeding Forest.")
        forest_spinner.start()
        for comment in submission.comments.list():
            comment_node = CommentNode(GetComments().create_comment(comment))
            EncodeNode().encode(comment_node)

            forest.seed(comment_node)

        forest_spinner.succeed("Forest has fully matured.")
        return forest.root.replies

class GetSort():
    """
    Methods for getting comments from a Reddit submission.
    """

    def __init__(self, args, reddit, url):
        """
        Initialize variables used in later methods:

            self._submission: PRAW submission object

        Calls replace_more() method on submission object to get nested comments.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        reddit: Reddit object
            Reddit instance created by PRAW API credentials
        url: str
            String denoting the submission's url

        Returns
        -------
        None
        """

        self._args = args
        self._submission = reddit.submission(url = url)
        self._url = url

        more_comments_spinner = Halo(color = "cyan", text = Fore.CYAN + Style.BRIGHT + "Resolving instances of MoreComments. This may take a while. Please wait.")

        more_comments_spinner.start()
        self._submission.comments.replace_more(limit = None)
        more_comments_spinner.succeed("Finished resolving instances of MoreComments.")

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
            
        if int(limit) != 0:
            return all_comments[:int(limit)]

        return all_comments

class Write():
    """
    Methods for writing scraped comments to CSV or JSON.
    """

    @staticmethod
    def _make_json_skeleton(args, limit, title, url):
        """
        Create a skeleton for JSON export. Include scrape details at the top.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        limit: str
            Integer of string type denoting n_results or RAW format
        title: str
            String denoting submission title
        url: str
            String denoting submission URL

        Returns
        -------
        skeleton: dict
            Dictionary containing scrape settings and all scrape data
        """

        skeleton = {
            "scrape_settings": {
                "submission_title": title,
                "n_results": int(limit) \
                    if int(limit) > 0 \
                    else "all",
                "style": "structured" \
                    if not args.raw \
                    else "raw",
                "submission_url": url
            },
            "data": None
        }

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
        
        Export.export(data, f_name, "json", "comments") \
            if args.raw \
            else Export.write_structured_comments(data, f_name)

    @staticmethod
    def _print_confirm(args, title):
        """
        Print confirmation message and set print length depending on string length.

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments that were defined in the CLI
        title: str
            String denoting the submission title

        Returns
        -------
        None
        """

        confirmation_spinner = Halo(color = "green", text = Style.BRIGHT + Fore.GREEN + "JSON file for '%s' comments created." % title)
        print()
        confirmation_spinner.succeed()
        print()

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
            title = reddit.submission(url = url).title
            data = Write._make_json_skeleton(args, limit, title, url)
            data["data"] = GetSort(args, reddit, url).get_sort(args, limit)
            
            f_name = NameFile().c_fname(args, limit, title)
            Write._determine_export(args, data, f_name)
            Write._print_confirm(args, title)

class RunComments():
    """
    Run the comments scraper.
    """

    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer(s_t[2])
    def run(args, parser, reddit):
        """
        Run comments scraper.

        Calls previously defined public methods:

            CheckSubmissions.list_submissions()
            Write.write()

        Calls public methods from external modules:

            GetPRAWScrapeSettings().create_list()
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

        post_list = GetPRAWScrapeSettings().create_list(args, s_t[2])
        not_posts, posts = CheckSubmissions.list_submissions(parser, post_list, reddit)
        c_master = make_none_dict(posts)
        GetPRAWScrapeSettings().get_settings(args, not_posts, c_master, s_t[2])

        Write.write(args, c_master, reddit)

        return c_master
