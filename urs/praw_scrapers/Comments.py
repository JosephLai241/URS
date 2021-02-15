"""
Submission comments scraper
===========================
Defining methods for the submission comments scraper.
"""


from colorama import (
    init, 
    Fore, 
    Style
)

from utils.Cli import GetPRAWScrapeSettings
from utils.Export import (
    Export,
    NameFile
)
from utils.Global import (
    convert_time,
    eo,
    make_none_dict,
    s_t
)
from utils.Logger import (
    LogExport, 
    LogPRAWScraper
)
from utils.Titles import PRAWTitles
from utils.Validation import Validation

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class CheckSubmissions():
    """
    Method for printing found and invalid Reddit posts.
    """

    ### Check if posts exist and list posts that are not found.
    @staticmethod
    def list_submissions(reddit, post_list, parser):
        print("\nChecking if post(s) exist...")
        posts, not_posts = Validation.existence(s_t[2], post_list, parser, reddit, s_t)
        
        if not_posts:
            print(Fore.YELLOW + Style.BRIGHT + "\nThe following posts were not found and will be skipped:")
            print(Fore.YELLOW + Style.BRIGHT + "-" * 55)
            print(*not_posts, sep = "\n")

        if not posts:
            print(Fore.RED + Style.BRIGHT + "\nNo submissions to scrape!")
            print(Fore.RED + Style.BRIGHT + "\nExiting.\n")
            quit()

        return posts

class GetComments():
    """
    Methods for getting comments from a post.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
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

    ### If applicable, handle deleted Redditors or edited time.
    def _fix_attributes(self, comment):
        try:
            author_name = comment.author.name
        except AttributeError:
            author_name = "[deleted]"

        edit_date = comment.edited \
            if str(comment.edited).isalpha() \
            else convert_time(comment.edited)

        return author_name, edit_date

    ### Add list of dictionary of comments attributes to use when sorting.
    def add_comment(self, comment):
        c_set = make_none_dict(self._titles)

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
            c_set[title] = attribute
        
        return c_set

class SortComments():
    """
    Methods for sorting comments depending on which style of comments was 
    specified (raw or structured).
    """

    ### Append comments in raw export format.
    @staticmethod
    def _raw_comments(add, all_dict, comment):
        all_dict[comment.id] = add

    ### Append top level comments to all_dict.
    @staticmethod
    def _top_level_comment(add, all_dict, comment):
        add["replies"] = []
        SortComments._raw_comments(add, all_dict, comment)

    ### Append second-level comments to all_dict.
    @staticmethod
    def _second_level_comment(add, all_dict, comment, cpid):
        add["replies"] = []
        all_dict[cpid]["replies"].append({comment.id: add})

    ### Append third-level comments to all_dict.
    @staticmethod
    def _third_level_comment(add, all_dict, comment, cpid):
        for all_comments in all_dict.values():
            for second_level_replies in all_comments["replies"]:
                if cpid in second_level_replies.keys():
                    second_level_replies[cpid]["replies"].append({comment.id: add})
        
    ### Appending structured comments to all_dict.
    @staticmethod
    def _structured_comments(add, all_dict, comment, cpid, submission):
        if cpid == submission.id:
            SortComments._top_level_comment(add, all_dict, comment)
        elif cpid in all_dict.keys():
            SortComments._second_level_comment(add, all_dict, comment, cpid)
        else:
            SortComments._third_level_comment(add, all_dict, comment, cpid)

    ### Append comments to all dictionary differently if raw is True or False.
    @staticmethod
    def _to_all(all_dict, comment, raw, submission):
        add = GetComments().add_comment(comment)

        if raw:
            SortComments._raw_comments(add, all_dict, comment)
        else:
            cpid = comment.parent_id.split("_", 1)[1]
            SortComments._structured_comments(add, all_dict, comment, cpid, submission)

    ### Sort comments.
    @staticmethod
    def sort(all_dict, raw, submission):
        for comment in submission.comments.list():
            SortComments._to_all(all_dict, comment, raw, submission)

class GetSort():
    """
    Methods for getting comments from a Reddit submission.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self, post, reddit):
        self._submission = reddit.submission(url = post)

        print(Fore.CYAN + Style.BRIGHT + "\nResolving instances of MoreComments...")
        print("\nThis may take a while. Please wait.")

        self._submission.comments.replace_more(limit = None)

    ### Get comments in raw format.
    def _get_raw(self, all_dict, submission):
        print(Style.BRIGHT + "\nProcessing all comments in raw format from submission '%s'..." % submission.title)
        SortComments().sort(all_dict, True, submission)

    ### Get comments in structured format.
    def _get_structured(self, all_dict, limit, submission):
        plurality = "comment" \
            if int(limit) == 1 \
            else "comments"
        print(Style.BRIGHT + "\nProcessing %s %s in structured format from submission '%s'..." % (limit, plurality, submission.title))

        SortComments().sort(all_dict, False, submission)
        
        return {key: all_dict[key] for key in list(all_dict)[:int(limit)]}

    ### Get comments from posts.
    def get_sort(self, limit):
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

    ### Create a skeleton for JSON export. Include scrape details at the top.
    @staticmethod
    def _make_json_skeleton(limit, post, title):
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

    ### Export to either CSV or JSON.
    @staticmethod
    def _determine_export(args, data, f_name):
        export_option = eo[1] \
            if not args.csv \
            else eo[0]

        Export.export(data, f_name, export_option, "comments")

    ### Print confirmation message and set print length depending on string length.
    @staticmethod
    def _print_confirm(args, title):
        export_option = "JSON" \
            if not args.csv \
            else "CSV"

        confirmation = "\n%s file for '%s' comments created." % (export_option, title)
        
        print(Style.BRIGHT + Fore.GREEN + confirmation)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(confirmation) - 1))

    ### Get, sort, then write scraped comments to CSV or JSON.
    @staticmethod
    def write(args, c_master, reddit):
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

    ### Run comments scraper.
    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer(s_t[2])
    def run(args, parser, reddit):
        PRAWTitles.c_title()

        post_list = GetPRAWScrapeSettings().create_list(args, s_t[2])
        posts = CheckSubmissions.list_submissions(reddit, post_list, parser)
        c_master = make_none_dict(posts)
        GetPRAWScrapeSettings().get_settings(args, c_master, s_t[2])

        Write.write(args, c_master, reddit)
