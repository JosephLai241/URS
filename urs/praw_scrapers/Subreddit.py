"""
Subreddit scraper
=================
Defining methods for the Subreddit scraper.
"""


from colorama import (
    init, 
    Fore, 
    Style
)
from prettytable import PrettyTable

from urs.praw_scrapers.utils.Validation import Validation

from urs.utils.Cli import GetPRAWScrapeSettings
from urs.utils.Export import (
    Export,
    NameFile
)
from urs.utils.Global import (
    categories,
    convert_time,
    eo,
    make_list_dict,
    options,
    s_t,
    short_cat,
)
from urs.utils.Logger import (
    LogExport, 
    LogPRAWScraper
)
from urs.utils.Titles import PRAWTitles

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class CheckSubreddits():
    """
    Method for checking if Subreddit(s) exist. Print invalid Subreddits if
    applicable.
    """

    ### Check if Subreddits exist and list invalid Subreddits if applicable.
    @staticmethod
    def list_subreddits(parser, reddit, s_t, sub_list):
        print("\nChecking if Subreddit(s) exist...")
        subs, not_subs = Validation().existence(s_t[0], sub_list, parser, reddit, s_t)
        
        if not_subs:
            print(Fore.YELLOW + Style.BRIGHT + "\nThe following Subreddits were not found and will be skipped:")
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
                
                pretty_subs.add_row([
                    sub, 
                    categories[cat_i], 
                    time_filter, 
                    each_sub[1]
                ])

    ### Print scraping details for each Subreddit.
    @staticmethod
    def print_settings(args, s_master):
        print(Fore.CYAN + Style.BRIGHT + "\nCurrent settings for each Subreddit")

        pretty_subs = PrettyTable()
        pretty_subs.field_names = [
            "Subreddit", 
            "Category", 
            "Time Filter",
            "Number of results / Keywords"
        ]

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

class GetRules():
    """
    Methods for getting a Subreddit's rules and post requirements.
    """

    ### Return post requirements and Subreddit rules.
    @staticmethod
    def get(subreddit):
        rules = [rule_list for rule, rule_list in subreddit.rules().items() if rule == "rules"]
        return subreddit.post_requirements(), rules[0]

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
        print(Style.BRIGHT + "\nSearching posts in r/%s for '%s'..." % (sub, search_for))
        
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
        index = short_cat.index(cat_i) \
            if args.subreddit \
            else cat_i
            
        print(Style.BRIGHT + "\nProcessing %s %s results from r/%s..." % (search_for, category, sub))
        
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
        self._titles = [
            "title", 
            "flair", 
            "date_created", 
            "upvotes", 
            "upvote_ratio", 
            "id", 
            "edited", 
            "is_locked", 
            "nsfw", 
            "is_spoiler", 
            "stickied", 
            "url", 
            "comment_count", 
            "text"
        ]

    ### Initialize dictionary depending on export option.
    def _initialize_dict(self, args):
        return make_list_dict(self._titles) \
            if args.csv \
            else dict()

    ### Fix "Edited?" date.
    def _fix_edit_date(self, post):
        return str(post.edited) \
            if str(post.edited).isalpha() \
            else str(convert_time(post.edited))

    ### Get post data.
    def _get_data(self, post):
        edited = self._fix_edit_date(post)
        post_data = [
            post.title, 
            post.link_flair_text, 
            convert_time(post.created), 
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
            post.selftext
        ]

        return post_data

    ### Append data to overview dictionary for CSV export.
    def _csv_format(self, overview, post_data):
        for title, data in zip(self._titles, post_data):
            overview[title].append(data)

    ### Create a skeleton for JSON export. Include scrape details at the top.
    def _make_json_skeleton(self, cat_i, search_for, sub, time_filter):
        json_data = {
            "scrape_settings": {
                "subreddit": sub,
                "category": categories[short_cat.index(cat_i)].lower(),
                "n_results_or_keywords": search_for,
                "time_filter": time_filter
            },
            "data": []
        }

        return json_data

    ### Add Subreddit rules and post requirements to the JSON skeleton.
    def _add_json_subreddit_rules(self, json_data, post_requirements, rules):
        json_data["subreddit_rules"] = {}
        json_data["subreddit_rules"]["rules"] = rules
        json_data["subreddit_rules"]["post_requirements"] = post_requirements

    ### Append submission data to the data list in the JSON skeleton.
    def _add_json_submission_data(self, json_data, post_data):
        json_data["data"].append({
            title: value for title, value in zip(self._titles, post_data)
        })
    
    ### Sort collected dictionary based on export option.
    def sort(self, args, cat_i, collected, post_requirements, rules, search_for, sub, time_filter):
        print("\nThis may take a while. Please wait.")

        if args.csv:
            overview = self._initialize_dict(args)
            for post in collected:
                post_data = self._get_data(post)
                self._csv_format(overview, post_data)

            return overview
            
        json_data = self._make_json_skeleton(cat_i, search_for, sub, time_filter)
        
        if args.rules:
            print(Fore.CYAN + Style.BRIGHT + "\nIncluding Subreddit rules...")
            self._add_json_subreddit_rules(json_data, post_requirements, rules)
        
        for post in collected:
            post_data = self._get_data(post)
            self._add_json_submission_data(json_data, post_data)

        return json_data

class GetSortWrite():
    """
    Methods to get, sort, then write scraped Subreddit posts to CSV or JSON.
    """

    ### Get and sort posts.
    @staticmethod
    def _get_sort(args, cat_i, reddit, search_for, sub, time_filter):
        post_requirements, rules = GetRules.get(reddit.subreddit(sub))
        collected = GetPosts.get(args, reddit, sub, cat_i, search_for, time_filter)

        return SortPosts().sort(args, cat_i, collected, post_requirements, rules, search_for, sub, time_filter)

    ### Export to either CSV or JSON.
    @staticmethod
    def _determine_export(args, data, f_name):
        export_option = eo[1] \
            if not args.csv \
            else eo[0]

        Export.export(data, f_name, export_option, "subreddits")

    ### Set print length depending on string length.
    @staticmethod
    def _print_confirm(args, sub):
        export_option = "JSON" \
            if not args.csv \
            else "CSV"

        confirmation = "\n%s file for r/%s created." % (export_option, sub)

        print(Style.BRIGHT + Fore.GREEN + confirmation)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(confirmation) - 1))

    ### Write posts.
    @staticmethod
    def _write(args, cat_i, data, each_sub, sub):
        f_name = NameFile().r_fname(args, cat_i, each_sub, sub)
        GetSortWrite._determine_export(args, data, f_name)
        GetSortWrite._print_confirm(args, sub)

    ### Get, sort, then write.
    @staticmethod
    def gsw(args, reddit, s_master):
        for sub, settings in s_master.items():
            for each_sub in settings:
                cat_i = each_sub[0].upper() \
                    if not args.basic \
                    else short_cat[each_sub[0]]
                data = GetSortWrite._get_sort(args, cat_i, reddit, str(each_sub[1]), sub, each_sub[2])
                GetSortWrite._write(args, cat_i, data, each_sub, sub)

class RunSubreddit():
    """
    Run the Subreddit scraper.
    """

    ### Create settings for each user input.
    @staticmethod
    def _create_settings(args, parser, reddit, s_t):
        sub_list = GetPRAWScrapeSettings().create_list(args, s_t[0])
        subs = CheckSubreddits.list_subreddits(parser, reddit, s_t, sub_list)
        s_master = make_list_dict(subs)
        GetPRAWScrapeSettings().get_settings(args, s_master, s_t[0])

        return s_master

    ### Print the confirm screen if the user did not specify the `-y` flag.
    @staticmethod
    @LogPRAWScraper.log_cancel
    def _confirm_write(args, reddit, s_master):
        PrintConfirm.print_settings(args, s_master)
        confirm = PrintConfirm.confirm_settings()

        if confirm == options[0]:
            GetSortWrite.gsw(args, reddit, s_master)
        else:
            raise KeyboardInterrupt

    ### Skip or print Subreddit scraping settings if the `-y` flag is entered.
    ### Then write or quit scraper.
    @staticmethod
    def _write_file(args, reddit, s_master):
        if args.y:
            GetSortWrite.gsw(args, reddit, s_master)
        else:
            RunSubreddit._confirm_write(args, reddit, s_master)

    ### Run Subreddit scraper.
    @staticmethod
    @LogExport.log_export
    @LogPRAWScraper.scraper_timer(s_t[0])
    def run(args, parser, reddit, s_t):
        PRAWTitles.r_title()

        s_master = RunSubreddit._create_settings(args, parser, reddit, s_t)
        RunSubreddit._write_file(args, reddit, s_master)
    