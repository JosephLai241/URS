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

        print("\nChecking if submission(s) exist...")
        logging.info("Validating submissions...")
        logging.info("")
        posts, not_posts = Validation.existence(s_t[2], post_list, parser, reddit, s_t)
        
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

    def add_comment(self, comment):
        """
        Add list of dictionary of comments attributes to use when sorting.

        Calls methods from an external module:

            Global.make_none_dict()
            Global.convert_time()

        Parameters
        ----------
        comment: PRAW object

        Returns
        -------
        comment_object: dict
            Dictionary for comment attribute
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

class SortComments():
    """
    Methods for sorting comments depending on which style of comments was 
    specified (raw or structured).
    """

    @staticmethod
    def _raw_comments(add, all_dict, comment):
        """
        Append comments in raw export format.

        Parameters
        ----------
        add: dict
            Dictionary object containing comment metadata
        all_dict: dict
            Dictionary containing all comments within a submission
        comment: PRAW object

        Returns
        -------
        None
        """

        all_dict[comment.id] = add

    @staticmethod
    def _top_level_comment(add, all_dict, comment):
        """
        Append top level comments to all_dict.

        Calls previously defined private method:

            SortComments._raw_comments()

        Parameters
        ----------
        add: dict
            Dictionary object containing comment metadata
        all_dict: dict
            Dictionary containing all comments within a submission
        comment: PRAW object

        Returns
        -------
        None
        """

        add["replies"] = []
        SortComments._raw_comments(add, all_dict, comment)

    @staticmethod
    def _second_level_comment(add, all_dict, comment, cpid):
        """
        Append second-level comments to all_dict.

        Parameters
        ----------
        add: dict
            Dictionary object containing comment metadata
        all_dict: dict
            Dictionary containing all comments within a submission
        comment: PRAW object

        Returns
        -------
        None
        """

        add["replies"] = []
        all_dict[cpid]["replies"].append({comment.id: add})

    @staticmethod
    def _third_level_comment(add, all_dict, comment, cpid):
        """
        Append third-level comments to all_dict.

        Parameters
        ----------
        add: dict
            Dictionary object containing comment metadata
        all_dict: dict
            Dictionary containing all comments within a submission
        comment: PRAW object

        Returns
        -------
        None
        """

        for all_comments in all_dict.values():
            for second_level_replies in all_comments["replies"]:
                if cpid in second_level_replies.keys():
                    second_level_replies[cpid]["replies"].append({comment.id: add})
        
    @staticmethod
    def _structured_comments(add, all_dict, comment, cpid, submission):
        """
        Appending structured comments to all_dict. 
        
        Calls previously defined private methods:

            SortComments._top_level_comment()
            SortComments._second_level_comment()
            SortComments._third_level_comment()

        Parameters
        ----------
        add: dict
            Dictionary object containing comment metadata
        all_dict: dict
            Dictionary containing all comments within a submission
        comment: PRAW object
        cpid: str
            String denoting comment parent ID
        submission: PRAW submission object
            Reddit submission object

        Returns
        -------
        None
        """

        if cpid == submission.id:
            SortComments._top_level_comment(add, all_dict, comment)
        elif cpid in all_dict.keys():
            SortComments._second_level_comment(add, all_dict, comment, cpid)
        else:
            SortComments._third_level_comment(add, all_dict, comment, cpid)

    @staticmethod
    def _to_all(all_dict, comment, raw, submission):
        """
        Append comments to all dictionary differently if raw is True or False. 
        
        Calls previously defined public and private methods:

            GetComments().add_comment()
            SortComments._raw_comments()
            SortComments._structured_comments()

        Parameters
        ----------
        all_dict: dict
            Dictionary containing all comments within a submission
        comment: PRAW object
        raw: bool
            Boolean denoting appending comments in raw or structured format
        submission: PRAW submission object
            Reddit submission object

        Returns
        -------
        None
        """

        add = GetComments().add_comment(comment)

        if raw:
            SortComments._raw_comments(add, all_dict, comment)
        else:
            cpid = comment.parent_id.split("_", 1)[1]
            SortComments._structured_comments(add, all_dict, comment, cpid, submission)

    @staticmethod
    def sort(all_dict, raw, submission):
        """
        Sort all comments. 
        
        Calls previously defined private methods:

            SortComments._to_all()

        Parameters
        ----------
        all_dict: dict
            Dictionary containing all comments within a submission
        raw: bool
            Boolean denoting appending comments in raw or structured format
        submission: PRAW submission object
            Reddit submission object

        Returns
        -------
        None
        """

        for comment in submission.comments.list():
            SortComments._to_all(all_dict, comment, raw, submission)

class GetSort():
    """
    Methods for getting comments from a Reddit submission.
    """

    def __init__(self, post, reddit):
        """
        Initialize variables used in later methods:

            self._submission: PRAW submission object

        Calls replace_more() method on submission object to get nested comments.

        Returns
        -------
        None
        """

        self._submission = reddit.submission(url = post)

        print(Fore.CYAN + Style.BRIGHT + "\nResolving instances of MoreComments...")
        print("\nThis may take a while. Please wait.")

        self._submission.comments.replace_more(limit = None)

    def _get_raw(self, all_dict, submission):
        """
        Get comments in raw format. 
        
        Calls previously defined public method:

            SortComments().sort()

        Parameters
        ----------
        all_dict: dict
            Dictionary containing all comments within a submission
        submission: PRAW submission object
            Reddit submission object

        Returns
        -------
        None
        """

        print(Style.BRIGHT + "\nProcessing all comments in raw format from submission '%s'..." % submission.title)
        SortComments().sort(all_dict, True, submission)

    def _get_structured(self, all_dict, limit, submission):
        """
        Get comments in structured format. 
        
        Calls previously defined public method:

            SortComments().sort()

        Parameters
        ----------
        all_dict: dict
            Dictionary containing all comments within a submission
        submission: PRAW submission object
            Reddit submission object

        Returns
        -------
        None
        """

        plurality = "comment" \
            if int(limit) == 1 \
            else "comments"
        print(Style.BRIGHT + "\nProcessing %s %s in structured format from submission '%s'..." % (limit, plurality, submission.title))

        SortComments().sort(all_dict, False, submission)
        
        return {key: all_dict[key] for key in list(all_dict)[:int(limit)]}

    def get_sort(self, limit):
        """
        Get comments from posts. 
        
        Calls previously defined private methods:

            self._get_raw()
            self._get_structured()

        Parameters
        ----------
        all_dict: dict
            Dictionary containing all comments within a submission
        submission: PRAW submission object
            Reddit submission object

        Returns
        -------
        all_dict: dict
            Dictionary containing all comments within a submission
        """

        all_dict = dict()

        if int(limit) == 0:
            self._get_raw(all_dict, self._submission)
            return all_dict
        else:
            return self._get_structured(all_dict, limit, self._submission)

class Write():
    """
    Methods for writing scraped comments to CSV or JSON.
    """

    @staticmethod
    def _make_json_skeleton(limit, post, title):
        """
        Create a skeleton for JSON export. Include scrape details at the top.

        Parameters
        ----------
        limit: str
            Integer of string type denoting n_results or RAW format
        post: str
            String denoting submission URL
        title: str
            String denoting submission title

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
                    else "RAW",
                "submission_url": post
            },
            "data": []
        }

        return skeleton

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
            Dictionary containing all scraped data
        f_name: str
            String denoting the filename

        Returns
        -------
        None
        """

        export_option = eo[1] \
            if not args.csv \
            else eo[0]

        Export.export(data, f_name, export_option, "comments")

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

        export_option = "JSON" \
            if not args.csv \
            else "CSV"

        confirmation = "\n%s file for '%s' comments created." % (export_option, title)
        
        print(Style.BRIGHT + Fore.GREEN + confirmation)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(confirmation) - 1))

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

        for post, limit in c_master.items():
            title = reddit.submission(url = post).title
            data = Write._make_json_skeleton(limit, post, title)
            data["data"].append(GetSort(post, reddit).get_sort(limit))
            f_name = NameFile().c_fname(limit, title)

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
