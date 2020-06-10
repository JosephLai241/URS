#===============================================================================
#                               Export Functions
#===============================================================================
import csv
import json
import os

from . import Global

class NameFile():
    """
    Functions for naming the exported files.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self.illegal_chars = Global.illegal_chars

    ### Fix f_name if illegal filename characters are present.
    def fix(self, name):
        fix = ["_" if char in self.illegal_chars else char for char in name]
        return "".join(fix)

    ### Category name switch.
    def r_category(self, cat_i, category_n):
        switch = {
            0: Global.categories[5],
            1: Global.categories[Global.short_cat.index(cat_i)] \
                if cat_i != Global.short_cat[5] and isinstance(cat_i, str) \
                    else None,
            2: Global.categories[cat_i] \
                if isinstance(cat_i, int) \
                    else None
        }

        return switch.get(category_n)

    ### Choose category name.
    def r_get_category(self, args, cat_i):
        if args.subreddit:
            category_n = 0 if cat_i == Global.short_cat[5] else 1
        elif args.basic:
            category_n = 2

        return category_n

    ### Determine file name format for CLI scraper.
    def get_raw_n(self, args, cat_i, end, search_for, sub):
        category_n = self.r_get_category(args, cat_i)
        category = self.r_category(cat_i, category_n)

        return str(("r-%s-%s-'%s'") % (sub, category, search_for)) \
            if cat_i == Global.short_cat[5] \
            else str(("r-%s-%s-%s-%s") % 
                (sub, category, search_for, end))

    ### Determine file name format for Subreddit scraping.
    def r_fname(self, args, cat_i, search_for, sub):
        raw_n = ""
        end = "result" if isinstance(search_for, int) and int(search_for) < 2 \
            else "results"

        raw_n = self.get_raw_n(args, cat_i, end, search_for, sub)
        f_name = self.fix(raw_n)

        return f_name

    ### Determine file name format for Redditor scraping.
    def u_fname(self, limit, string):
        end = "result" if int(limit) < 2 else "results"
        raw_n = str(("u-%s-%s-%s") % (string, limit, end))
        return self.fix(raw_n)

    ### Determine file name format for comments scraping.
    def c_fname(self, limit, string):
        end = "result" if int(limit) < 2 else "results"
        raw_n = str(("c-%s-%s-%s") % (string, limit, end))
        return self.fix(raw_n)

class Export():
    """
    Functions for creating directories and export the file.
    """

    ### On the first run, create the directory scrapes/. Then make a sub-directory 
    ### corresponding with the date in which the user scraped data from Reddit if it 
    ### does not exist.
    def make_directory(self):
        scrapes_dir = "../scrapes"
        if not os.path.isdir(scrapes_dir):
            os.mkdir(scrapes_dir)
        
        dir_path = "../scrapes/%s" % Global.date
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        
    ### Write overview dictionary to CSV or JSON.
    def export(self, f_type, f_name, overview):
        dir_path = "../scrapes/%s" % Global.date

        if f_type == Global.eo[0]:
            filename = dir_path + "/%s.csv" % f_name
            with open(filename, "w", encoding = "utf-8") as results:
                writer = csv.writer(results, delimiter = ",")
                writer.writerow(overview.keys())
                writer.writerows(zip(*overview.values()))
        elif f_type == Global.eo[1]:
            filename = dir_path + "/%s.json" % f_name
            with open(filename, "w", encoding = "utf-8") as results:
                json.dump(overview, results, indent = 4)
