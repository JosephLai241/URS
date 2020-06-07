#===============================================================================
#                       Subreddit Scraping Functions
#===============================================================================
from colorama import Fore, init, Style
from . import cli, export, global_vars, titles

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

### Global variables
categories = global_vars.categories
convert_time = global_vars.convert_time
eo = global_vars.eo
options = global_vars.options
short_cat = global_vars.short_cat

class PrintConfirm():
    """
    Print Subreddit settings, then confirm settings.
    """

    ### Print each Subreddit setting.
    def print_each(self, args, s_master):
        for sub, settings in s_master.items():
            for each in settings:
                cat_i = short_cat.index(each[0].upper()) if not args.basic \
                    else each[0]
                specific = each[1]
                
                print("\n{:<25}{:<17}{:<30}".format(sub, categories[cat_i], specific))

    ### Print scraping details for each Subreddit.
    def print_settings(self, args, s_master):
        print(Style.BRIGHT + "\n------------------Current settings for each Subreddit-------------------")
        print(Style.BRIGHT + "\n{:<25}{:<17}{:<30}".format("Subreddit", "Category", 
                "Number of results / Keyword(s)"))
        print(Style.BRIGHT + "-" * 72)

        self.print_each(args, s_master)

    ### Confirm scraping options.
    def confirm_settings(self):
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

class GetPosts():
    """
    Implementing Pythonic switch case to determine which category to scrape a
    Subreddit.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self, reddit, search_for):
        self.hot = reddit.subreddit.hot(limit = int(search_for))
        self.new = reddit.subreddit.new(limit = int(search_for))
        self.controversial = reddit.subreddit.controversial(limit = int(search_for))
        self.top = reddit.subreddit.top(limit = int(search_for))
        self.rising = reddit.subreddit.rising(limit = int(search_for))

        self.switch = {
            0: self.hot,
            1: self.new,
            2: self.controversial,
            3: self.top,
            4: self.rising
        }

    ### Return a command based on the chosen category.
    def scrape_sub(self, index):
        return self.switch.get(index)

    ### Return PRAW ListingGenerator for searching keywords.
    def collect_search(self, search_for, sub, subreddit):
        print((Style.BRIGHT + "\nSearching posts in r/%s for '%s'...") % 
            (sub, search_for))

        return subreddit.search("%s" % search_for)

    ### Return PRAW ListingGenerator for all other categories.
    def collect_others(self, args, cat_i, search_for, sub):
        category = categories[short_cat.index(cat_i)] if args.subreddit \
            else categories[cat_i]
        index = short_cat.index(cat_i) if args.subreddit else cat_i
            
        print(Style.BRIGHT + ("\nProcessing %s %s results from r/%s...") % 
            (search_for, category, sub))
        
        return self.scrape_sub(index)

    ### Get Subreddit posts and return the PRAW ListingGenerator.
    def get(self, args, reddit, sub, cat_i, search_for):
        subreddit = reddit.subreddit(sub)

        self.collect_search(self, search_for, sub, subreddit) \
            if cat_i == short_cat[5] or cat_i == 5 \
            else self.collect_others(self, args, cat_i, search_for, sub)

class SortPosts():
    """
    Sort posts based on export option.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self.titles = ["Title", "Flair", "Date Created", "Upvotes", "Upvote Ratio", 
                        "ID", "Edited?", "Is Locked?", "NSFW?", "Is Spoiler?", 
                        "Stickied?", "URL", "Comment Count", "Text"]

    ### Initialize dictionary depending on export option.
    def initialize_dict(self, args):
        return global_vars.make_list_dict(self.titles) if args.csv else dict()

    ### Fix "Edited?" date.
    def fix_edit_date(self, post):
        return str(post.edited) if str(post.edited).isalpha() \
                else str(convert_time(post.edited))

    ### Get post data.
    def get_data(self, post):
        edited = self.fix_edit_date(self, post)
        post_data = [post.title, post.link_flair_text, convert_time(post.created), 
            post.score, post.upvote_ratio, post.id, edited, post.locked, 
            post.over_18, post.spoiler, post.stickied, post.url, 
            post.num_comments, post.selftext]

        return edited, post_data

    ### Append data to overview dictionary for CSV export.
    def csv_format(self, overview, post_data):
        for title, data in zip(self.titles, post_data):
                overview[title].append(data)

    ### Append data to overview dictionary for JSON export.
    def json_format(self, count, post_data):
        overview["Post %s" % count] = {
            title:value for title, value in zip(self.titles, post_data)}
    
    ### Sort collected dictionary based on export option.
    def sort(self, args, collected):
        print("\nThis may take a while. Please wait.")

        overview = self.initialize_dict(self, args)

        if args.csv:
            for post in collected:
                post_data = self.get_data(self, post)
                self.csv_format(self, overview, post_data)
        elif args.json:
            for count, post in enumerate(collected, start = 1):
                post_data = self.get_data(self, post)
                self.json_format(self, count, post_data)

        return overview

class GetSortWrite():
    """
    Get, sort, then write scraped Subreddit posts to CSV or JSON.
    """

    ### Get and sort posts.
    def get_sort(self, args, cat_i, each, reddit, search_for, sub):
        collected = GetPosts(reddit, search_for).\
                    get(args, reddit, sub, cat_i, search_for)
        
        return SortPosts().sort(args, collected)

    ### Write posts.
    def write(self, args, cat_i, overview, search_for, sub):
        fname = export.r_fname(args, cat_i, search_for, sub)
        if args.csv:
            export.export(fname, overview, eo[0])
            csv = "\nCSV file for r/%s created." % sub
            print(Style.BRIGHT + Fore.GREEN + csv)
            print(Style.BRIGHT + Fore.GREEN + "-" * (len(csv) - 1))
        elif args.json:
            export.export(fname, overview, eo[1])
            json = "\nJSON file for r/%s created." % sub
            print(Style.BRIGHT + Fore.GREEN + json)
            print(Style.BRIGHT + Fore.GREEN + "-" * (len(json) - 1))

    ### Get, sort, then write.
    def gsw(self, reddit, args, s_master):
        for sub, settings in s_master.items():
            for each in settings:
                cat_i = each[0].upper() if not args.basic else each[0]
                search_for = each[1]

                overview = self.get_sort(args, cat_i, each, reddit, search_for, sub)
                
                self.write(args, cat_i, overview, search_for, sub)

class RunSubreddit():
    """
    Run Subreddit scraper.
    """

    ### Create settings for each user input.
    def create_settings(self, args, parser, reddit, s_t):
        sub_list = cli.create_list(args, s_t, s_t[0])
        subs = cli.confirm_subs(reddit, sub_list, parser)
        s_master = global_vars.make_list_dict(subs)
        cli.get_cli_settings(reddit, args, s_master, s_t, s_t[0])

        return s_master

    ### Skip or print Subreddit scraping settings if the `-y` flag is entered.
    ### Then write or quit scraping.
    def print_write(self, s_master):
        if self.args.y:
            GetSortWrite().gsw(self.reddit, self.args, s_master)
        else:
            PrintConfirm().print_settings(self.args, s_master)
            confirm = PrintConfirm().confirm_settings()
            
            GetSortWrite().gsw(self.reddit, self.args, s_master) if confirm == self.options[0] \
                else print(Fore.RED + Style.BRIGHT + "\nCancelling.")

    ### Run Subreddit scraper.
    def run(self, args, parser, reddit, s_t):
        titles.r_title()

        s_master = self.create_settings(args, parser, reddit, s_t)
        self.print_write(s_master)
