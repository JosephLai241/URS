#===============================================================================
#                             Subreddit Scraping
#===============================================================================
from colorama import (
    init, 
    Fore, 
    Style)
from prettytable import PrettyTable

from . import (
    Cli, 
    Export, 
    Global, 
    Titles, 
    Validation)
from .Logger import (
    LogExport, 
    LogScraper)

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

### Global variables.
categories = Global.categories
options = Global.options
short_cat = Global.short_cat

class CheckSubreddits():
    """
    Method for checking if Subreddit(s) exist. Print invalid Subreddits if
    applicable.
    """

    ### Check if Subreddits exist and list invalid Subreddits if applicable.
    @staticmethod
    def list_subreddits(parser, reddit, s_t, sub_list):
        print("\nChecking if Subreddit(s) exist...")
        subs, not_subs = Validation.Validation().existence(s_t[0], sub_list, parser, reddit, s_t)
        
        if not_subs:
            print(Fore.YELLOW + Style.BRIGHT + 
                "\nThe following Subreddits were not found and will be skipped:")
            print(Fore.YELLOW + Style.BRIGHT + "-" * 60)
            print(*not_subs, sep = "\n")

        if not subs:
            print(Fore.RED + Style.BRIGHT + "\nNo Subreddits to scrape!")
            print(Fore.RED + Style.BRIGHT + "\nExiting.\n")
            quit()

        return subs

class PrintConfirm():
    """
    Methods for printing Subreddit settings and confirm settings.
    """

    ### Print each Subreddit setting.
    @staticmethod
    def _print_each(args, pretty_subs, s_master):
        for sub, settings in s_master.items():
            for each_sub in settings:
                cat_i = short_cat.index(each_sub[0].upper()) \
                    if not args.basic \
                    else each_sub[0]
                time_filter = each_sub[2].capitalize() \
                    if each_sub[2] != None \
                    else each_sub[2]
                
                pretty_subs.add_row([sub, categories[cat_i], time_filter, each_sub[1]])

    ### Print scraping details for each Subreddit.
    @staticmethod
    def print_settings(args, s_master):
        print(Fore.CYAN + Style.BRIGHT + "\nCurrent settings for each Subreddit")

        pretty_subs = PrettyTable()
        pretty_subs.field_names = [
            "Subreddit", 
            "Category", 
            "Time Filter",
            "Number of results / Keywords"]

        PrintConfirm._print_each(args, pretty_subs, s_master)
        pretty_subs.align = "l"

        print(pretty_subs)

    ### Confirm scraping options.
    @staticmethod
    def confirm_settings():
        while True:
            try:
                confirm = input("\nConfirm options? [Y/N] ").strip().lower()

                if confirm == options[0]:
                    return confirm
                elif confirm == options[1]:
                    break
                elif confirm not in options:
                    raise ValueError
            except ValueError:
                print("Not an option! Try again.")

class GetPostsSwitch():
    """
    Implementing Pythonic switch case to determine which Subreddit category to
    get results from.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self, search_for, subreddit, time_filter):
        self._controversial = subreddit.controversial(limit = int(search_for), time_filter = time_filter) \
            if time_filter != None \
            else subreddit.controversial(limit = int(search_for))
        self._hot = subreddit.hot(limit = int(search_for))
        self._new = subreddit.new(limit = int(search_for))
        self._rising = subreddit.rising(limit = int(search_for))
        self._top = subreddit.top(limit = int(search_for), time_filter = time_filter) \
            if time_filter != None \
            else subreddit.top(limit = int(search_for))

        self._switch = {
            0: self._hot,
            1: self._new,
            2: self._controversial,
            3: self._top,
            4: self._rising
        }

    ### Return a command based on the chosen category.
    def scrape_sub(self, index):
        return self._switch.get(index)

class GetPosts():
    """
    Methods for getting posts from a Subreddit.
    """

    ### Return PRAW ListingGenerator for searching keywords.
    @staticmethod
    def _collect_search(search_for, sub, subreddit, time_filter):
        print((Style.BRIGHT + "\nSearching posts in r/%s for '%s'...") % 
            (sub, search_for))
        
        if time_filter != None:
            print(Style.BRIGHT + "Time filter: %s" % time_filter.capitalize())

        return subreddit.search("%s" % search_for, time_filter = time_filter) \
            if time_filter != None \
            else subreddit.search("%s" % search_for)

    ### Return PRAW ListingGenerator for all other categories.
    @staticmethod
    def _collect_others(args, cat_i, search_for, sub, subreddit, time_filter):
        category = categories[short_cat.index(cat_i)] \
            if args.subreddit \
            else categories[cat_i]
        index = short_cat.index(cat_i) if args.subreddit else cat_i
            
        print(Style.BRIGHT + ("\nProcessing %s %s results from r/%s...") % 
            (search_for, category, sub))
        
        if time_filter != None:
            print(Style.BRIGHT + "Time filter: %s" % time_filter.capitalize())

        return GetPostsSwitch(search_for, subreddit, time_filter).scrape_sub(index)

    ### Get Subreddit posts and return the PRAW ListingGenerator.
    @staticmethod
    def get(args, reddit, sub, cat_i, search_for, time_filter):
        subreddit = reddit.subreddit(sub)

        return GetPosts._collect_search(search_for, sub, subreddit, time_filter) \
            if cat_i == short_cat[5] or cat_i == 5 \
            else GetPosts._collect_others(args, cat_i, search_for, sub, subreddit, time_filter)

class SortPosts():
    """
    Methods for sorting posts based on the export option.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._convert_time = Global.convert_time
        self._titles = [
            "Title", 
            "Flair", 
            "Date Created", 
            "Upvotes", 
            "Upvote Ratio", 
            "ID", 
            "Edited?", 
            "Is Locked?", 
            "NSFW?", 
            "Is Spoiler?", 
            "Stickied?", 
            "URL", 
            "Comment Count", 
            "Text"]

    ### Initialize dictionary depending on export option.
    def _initialize_dict(self, args):
        return Global.make_list_dict(self._titles) if args.csv else dict()

    ### Fix "Edited?" date.
    def _fix_edit_date(self, post):
        return str(post.edited) \
            if str(post.edited).isalpha() \
            else str(self._convert_time(post.edited))

    ### Get post data.
    def _get_data(self, post):
        edited = self._fix_edit_date(post)
        post_data = [
            post.title, 
            post.link_flair_text, 
            self._convert_time(post.created), 
            post.score, 
            post.upvote_ratio, 
            post.id, 
            edited, 
            post.locked, 
            post.over_18, 
            post.spoiler, 
            post.stickied, 
            post.url, 
            post.num_comments, 
            post.selftext]

        return post_data

    ### Append data to overview dictionary for CSV export.
    def _csv_format(self, overview, post_data):
        for title, data in zip(self._titles, post_data):
            overview[title].append(data)

    ### Append data to overview dictionary for JSON export.
    def _json_format(self, count, overview, post_data):
        overview["Post %s" % count] = {
            title: value for title, value in zip(self._titles, post_data)
        }
    
    ### Sort collected dictionary based on export option.
    def sort(self, args, collected):
        print("\nThis may take a while. Please wait.")

        overview = self._initialize_dict(args)

        if args.csv:
            for post in collected:
                post_data = self._get_data(post)
                self._csv_format(overview, post_data)
        elif args.json:
            for count, post in enumerate(collected, start = 1):
                post_data = self._get_data(post)
                self._json_format(count, overview, post_data)

        return overview

class GetSortWrite():
    """
    Methods to get, sort, then write scraped Subreddit posts to CSV or JSON.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._eo = Global.eo

    ### Get and sort posts.
    def _get_sort(self, args, cat_i, reddit, search_for, sub, time_filter):
        collected = GetPosts.get(args, reddit, sub, cat_i, search_for, time_filter)        
        return SortPosts().sort(args, collected)

    ### Export to either CSV or JSON.
    def _determine_export(self, args, f_name, overview):
        Export.Export.export(f_name, self._eo[1], overview) \
            if args.json \
            else Export.Export.export(f_name, self._eo[0], overview)

    ### Set print length depending on string length.
    def _print_confirm(self, args, sub):
        confirmation = "\nJSON file for r/%s created." % sub \
            if args.json \
            else "\nCSV file for r/%s created." % sub
        print(Style.BRIGHT + Fore.GREEN + confirmation)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(confirmation) - 1))

    ### Write posts.
    def _write(self, args, cat_i, overview, each_sub, sub):
        f_name = Export.NameFile().r_fname(args, cat_i, each_sub, sub)
        self._determine_export(args, f_name, overview)
        self._print_confirm(args, sub)

    ### Get, sort, then write.
    def gsw(self, args, reddit, s_master):
        for sub, settings in s_master.items():
            for each_sub in settings:
                cat_i = each_sub[0].upper() if not args.basic else each_sub[0]
                
                overview = self._get_sort(args, cat_i, reddit, str(each_sub[1]), sub, each_sub[2])
                self._write(args, cat_i, overview, each_sub, sub)

class RunSubreddit():
    """
    Run the Subreddit scraper.
    """

    ### Create settings for each user input.
    @staticmethod
    def _create_settings(args, parser, reddit, s_t):
        sub_list = Cli.GetScrapeSettings().create_list(args, s_t[0])
        subs = CheckSubreddits.list_subreddits(parser, reddit, s_t, sub_list)
        s_master = Global.make_list_dict(subs)
        Cli.GetScrapeSettings().get_settings(args, s_master, s_t[0])

        return s_master

    ### Print the confirm screen if the user did not specify the `-y` flag.
    @staticmethod
    @LogScraper.log_cancel
    def _confirm_write(args, reddit, s_master):
        PrintConfirm.print_settings(args, s_master)
        confirm = PrintConfirm.confirm_settings()

        if confirm == options[0]:
            GetSortWrite().gsw(args, reddit, s_master)
        else:
            raise KeyboardInterrupt

    ### Skip or print Subreddit scraping settings if the `-y` flag is entered.
    ### Then write or quit scraper.
    @staticmethod
    def _write_file(args, reddit, s_master):
        if args.y:
            GetSortWrite().gsw(args, reddit, s_master)
        else:
            RunSubreddit._confirm_write(args, reddit, s_master)

    ### Run Subreddit scraper.
    @staticmethod
    @LogExport.log_export
    @LogScraper.scraper_timer(Global.s_t[0])
    def run(args, parser, reddit, s_t):
        Titles.Titles.r_title()

        s_master = RunSubreddit._create_settings(args, parser, reddit, s_t)
        RunSubreddit._write_file(args, reddit, s_master)
