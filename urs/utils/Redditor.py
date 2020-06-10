#===============================================================================
#                               Redditor Scraping
#===============================================================================
import praw

from colorama import Fore, init, Style
from prawcore import PrawcoreException
from . import Cli, Export, Global, Titles, Validation

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

### Global variables
convert_time = Global.convert_time
s_t = Global.s_t

class PrintUsers():
    """
    Function for printing found and invalid Redditors.
    """

    ### Check if Redditors exist and list Redditors who are not found.
    def list_users(self, parser, reddit, user_list):
        print("\nChecking if Redditor(s) exist...")
        users, not_users = Validation.Validation().existence(s_t[1], user_list, 
            parser, reddit, s_t)
        if not_users:
            print("\nThe following Redditors were not found and will be skipped:")
            print("-" * 59)
            print(*not_users, sep = "\n")

        return users

class ProcessInteractions():
    """
    Functions for sorting and labeling comment or submission objects correctly. 
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

    ### Initialize objects that will be used in class methods.
    def __init__(self, limit, overview, user):
        self.overview = overview

        self.comments = user.comments.new(limit = limit)
        self.controversial = user.controversial(limit = limit)
        self.downvoted = user.downvoted(limit = limit)          # May be forbidden
        self.gilded = user.gilded(limit = limit)
        self.gildings = user.gildings(limit = limit)            # May be forbidden
        self.hidden = user.hidden(limit = limit)                # May be forbidden
        self.hot = user.hot(limit = limit)
        self.new = user.new(limit = limit)
        self.saved = user.saved(limit = limit)                  # May be forbidden
        self.submissions = user.submissions.new(limit = limit)
        self.top = user.top(limit = limit)
        self.upvoted = user.upvoted(limit = limit)              # May be forbidden

        self.comment_titles = ["Date Created", "Score", "Text", "Parent ID", "Link ID",
            "Edited?", "Stickied?", "Replying to", "In Subreddit"]
        self.submission_titles = ["Title", "Date Created", "Upvotes", "Upvote Ratio",
            "ID", "NSFW?", "In Subreddit", "Body"]

        self.s_types = ["Submissions", "Comments", "Mutts", "Access"]

        self.mutts = [self.controversial, self.gilded, self.hot, self.new, self.top]
        self.mutt_names = ["Controversial", "Gilded", "Hot", "New", "Top"]

        self.access = [self.downvoted, self.gildings, self.hidden, self.saved, self.upvoted]
        self.access_names = ["Downvoted", "Gildings", "Hidden", "Saved", "Upvoted"]

    ### Make dictionary from zipped lists.
    def make_zip_dict(self, titles, items):
        return dict((title, item) for title, item in zip(titles, items))

    ### Make submission list.
    def make_submission_list(self, item):
        items = [item.title, convert_time(item.created), item.score, item.upvote_ratio, 
            item.id, item.over_18, item.subreddit.display_name, item.selftext]

        return self.make_zip_dict(self.submission_titles, items)

    ### Make comment list.
    def make_comment_list(self, item):
        edit_date = item.edited if str(item.edited).isalpha() \
            else convert_time(item.edited)
        items = [convert_time(item.created_utc), item.score, item.body, item.parent_id, 
            item.link_id, edit_date, item.stickied, item.submission.selftext, 
            item.submission.subreddit.display_name]

        return self.make_zip_dict(self.comment_titles, items)

    ### Determine how to append the list to the overview dictionary.
    def determine_append(self, cat, redditor_list, s_type):
        switch = {
            0: "Submissions",
            1: "Comments",
            2: "%s" % cat.capitalize() if cat != None else None,
            3: "%s (may be forbidden)" % cat.capitalize() if cat != None else None
        }

        index = self.s_types.index(s_type)
        self.overview[switch.get(index)].append(redditor_list)

    ### Extracting submission or comment attributes and appending to overview 
    ### dictionary.
    def extract(self, cat, obj, s_types, s_type):
        for item in obj:
            redditor_list = self.make_submission_list(item) \
                if isinstance(item, praw.models.Submission) \
                    else self.make_comment_list(item)

            self.determine_append(cat, redditor_list, s_type) 

    ### Sort Redditor submissions.
    def sort_submissions(self):
        self.extract(None, self.submissions, self.s_types, self.s_types[0])

    ### Sort Redditor comments.
    def sort_comments(self):
        self.extract(None, self.comments, self.s_types, self.s_types[1])

    ### Sort Controversial, Gilded, Hot, New and Top Redditor posts. The ListingGenerator
    ### returns a mix of submissions and comments, so handling each differently is
    ### necessary.
    def sort_mutts(self):
        for cat, obj in zip(self.mutt_names, self.mutts):
            self.extract(cat, obj, self.s_types, self.s_types[2])

    ### Sort upvoted, downvoted, gildings, hidden, and saved Redditor posts. These
    ### lists tend to raise a 403 HTTP Forbidden exception, so naturally exception
    ### handling is necessary.
    def sort_access(self):
        for cat, obj in zip(self.access_names, self.access):
            try:
                self.extract(cat, obj, self.s_types, self.s_types[3])
            except PrawcoreException as error:
                print(Style.BRIGHT + Fore.RED + 
                    ("\nACCESS TO %s OBJECTS FORBIDDEN: %s. SKIPPING.") % 
                    (cat.upper(), error))
                self.overview["%s (may be forbidden)" % 
                    cat.capitalize()].append("FORBIDDEN")

class GetInteractions():
    """
    Functions for getting Redditor information and interactions.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self.titles = ["Name", "Fullname", "ID", "Date Created", "Comment Karma", 
            "Link Karma", "Is Employee?", "Is Friend?", "Is Mod?", "Is Gold?", 
            "Submissions", "Comments", "Hot", "New", "Controversial", "Top", 
            "Upvoted (may be forbidden)", "Downvoted (may be forbidden)", "Gilded", 
            "Gildings (may be forbidden)", "Hidden (may be forbidden)", 
            "Saved (may be forbidden)"]

    ### Make Redditor dictionary to store data.
    def make_user_profile(self, limit, reddit, user):
        print(Style.BRIGHT + ("\nProcessing %s results from u/%s's profile...") % 
                (limit, user))
        print("\nThis may take a while. Please wait.")

        user = reddit.redditor(user)
        overview = Global.make_list_dict(self.titles)

        return overview, user

    ### Get Redditor account information.
    def get_user_info(self, limit, overview, reddit, user):
        user_info_titles = self.titles[:10]
        user_info = [user.name, user.fullname, user.id, convert_time(user.created_utc),
            user.comment_karma, user.link_karma, user.is_employee, user.is_friend,
            user.is_mod, user.is_gold]

        for title, user_item in zip(user_info_titles, user_info):
            overview[title].append(user_item) 

    ### Get Redditor interactions on Reddit.
    def get_user_interactions(self, limit, overview, user):
        interactions = ProcessInteractions(int(limit), overview, user)
        interactions.sort_submissions()
        interactions.sort_comments()
        interactions.sort_mutts()
        interactions.sort_access()

    ### Get Redditor information and interactions.
    def get(self, limit, reddit, user):
        overview, user = self.make_user_profile(limit, reddit, user)
        self.get_user_info(limit, overview, reddit, user)
        self.get_user_interactions(limit, overview, user)

        return overview

class Write():
    """
    Functions for writing scraped Redditor information to CSV or JSON.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self.eo = Global.eo

    ### Export to either CSV or JSON.
    def determine_export(self, args, f_name, overview):
        Export.Export().export(self.eo[1], f_name, overview) if args.json else \
            Export.Export().export(self.eo[0], f_name, overview)

    ### Set print length depending on string length.
    def print_confirm(self, args, user):
        confirmation = "\nJSON file for u/%s created." % user if args.json \
            else "\nCSV file for u/%s created." % user
        print(Style.BRIGHT + Fore.GREEN + confirmation)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(confirmation) - 1))

    ### Get, sort, then write scraped Redditor information to CSV or JSON.
    def write(self, args, reddit, u_master):
        for user, limit in u_master.items():
            overview = GetInteractions().get(limit, reddit, user)
            f_name = Export.NameFile().u_fname(limit, user)
            self.determine_export(args, f_name, overview)
            self.print_confirm(args, user)

class RunRedditor():
    """
    Run the Redditor scraper.
    """

    ### Run Redditor scraper.
    def run(self, args, parser, reddit):
        Titles.Titles().u_title()

        user_list = Cli.GetScrapeSettings().create_list(args, s_t[1])
        users = PrintUsers().list_users(parser, reddit, user_list)
        u_master = Global.make_none_dict(users)
        Cli.GetScrapeSettings().get_settings(args, u_master, reddit, s_t[1])

        Write().write(args, reddit, u_master)