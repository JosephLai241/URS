#===============================================================================
#                                  Exporting
#===============================================================================
import csv
import json
import re

from . import Global

class NameFile():
    """
    Methods for naming the exported files.
    """

    ### Initialize objects that will be used in class methods.
    def __init__(self):
        self._illegal_chars = re.compile("[@!#$%^&*()<>?/\\\\|}{~:+`=]")

    ### Verify f_name is not too long.
    def _check_len(self, name):
        if len(name) > 50:
            return name[0:48] + "--"

        return name

    ### Fix f_name if illegal filename characters are present.
    def _fix(self, name):
        fixed = ["_" if self._illegal_chars.search(char) != None
            else char for char in name]

        return "".join(fixed)

    ### Category name switch.
    def _r_category(self, cat_i, category_n):
        switch = {
            0: Global.categories[5],
            1: Global.categories[Global.short_cat.index(cat_i)] \
                if cat_i != Global.short_cat[5] and isinstance(cat_i, str) \
                else None,
            2: Global.categories[cat_i] if isinstance(cat_i, int) else None
        }

        return switch.get(category_n)

    ### Choose category name.
    def _r_get_category(self, args, cat_i):
        if args.subreddit:
            category_n = 0 if cat_i == Global.short_cat[5] else 1
        elif args.basic:
            category_n = 2

        return category_n

    ### File name switch that stores all possible Subreddit file name formats.
    def _get_sub_fname(self, category, end, index, n_res_or_kwds, subreddit, time_filter):
        filter_str = "-past-%s" % time_filter
        search = "r-%s-%s-'%s'" % (subreddit, category, n_res_or_kwds)
        standard = "r-%s-%s-%s-%s" % (subreddit, category, n_res_or_kwds, end)

        filenames = {
            0: search,
            1: standard,
            2: search + filter_str,
            3: standard + filter_str
        }

        return filenames.get(index)

    ### Determine file name format for CLI Subreddit scraper.
    def _get_raw_n(self, args, cat_i, end, each_sub, sub):
        category_n = self._r_get_category(args, cat_i)
        category = self._r_category(cat_i, category_n)

        ending = None if cat_i == Global.short_cat[5] or cat_i == 5 else end
        time_filter = None \
            if each_sub[2] == None or each_sub[2] == "all" \
            else each_sub[2]

        if each_sub[2] == None or each_sub[2] == "all":
            index = 0 if cat_i == Global.short_cat[5] or cat_i == 5 else 1
        else:
            index = 2 if cat_i == Global.short_cat[5] or cat_i == 5 else 3

        return self._get_sub_fname(category, ending, index, each_sub[1], sub, time_filter)

    ### Determine file name format for Subreddit scraping.
    def r_fname(self, args, cat_i, each_sub, sub):
        raw_n = ""
        end = "result" \
            if isinstance(each_sub[1], int) and int(each_sub[1]) < 2 \
            else "results"

        raw_n = self._get_raw_n(args, cat_i, end, each_sub, sub)
        raw_n = self._check_len(raw_n)
        f_name = self._fix(raw_n)

        return f_name

    ### Determine file name format for Redditor scraping.
    def u_fname(self, limit, string):
        end = "result" if int(limit) < 2 else "results"
        raw_n = str(("u-%s-%s-%s") % (string, limit, end))
        raw_n = self._check_len(raw_n)

        return self._fix(raw_n)

    ### Determine file name format for comments scraping.
    def c_fname(self, limit, string):
        if int(limit) != 0:
            end = "result" if int(limit) < 2 else "results"
            raw_n = str(("c-%s-%s-%s") % (string, limit, end))
        else:
            raw_n = str(("c-%s-%s") % (string, "RAW"))

        raw_n = self._check_len(raw_n)

        return self._fix(raw_n)

class Export():
    """
    Methods for creating directories and export the file.
    """

    ### Export to CSV.
    @staticmethod
    def _write_csv(filename, overview):
        with open(filename, "w", encoding = "utf-8") as results:
            writer = csv.writer(results, delimiter = ",")
            writer.writerow(overview.keys())
            writer.writerows(zip(*overview.values()))

    ### Export to JSON.
    @staticmethod
    def _write_json(filename, overview):
        with open(filename, "w", encoding = "utf-8") as results:
            json.dump(overview, results, indent = 4)

    ### Get filename extension.
    @staticmethod
    def _get_filename_extension(f_name, f_type):
        dir_path = "../scrapes/%s" % Global.date

        return dir_path + "/%s.json" % f_name \
            if f_type == Global.eo[1] \
            else dir_path + "/%s.csv" % f_name

    ### Write overview dictionary to CSV or JSON.
    @staticmethod
    def export(f_name, f_type, overview):
        filename = Export._get_filename_extension(f_name, f_type)

        Export._write_json(filename, overview) \
            if f_type == Global.eo[1] \
            else Export._write_csv(filename, overview)
