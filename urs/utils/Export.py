#===============================================================================
#                                  Exporting
#===============================================================================
import csv
import json
import re

from utils.DirInit import InitializeDirectory
from utils.Global import (
    categories,
    date,
    eo,
    short_cat
)

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
        fixed = [
            "_" 
                if self._illegal_chars.search(char) != None
                else char for char in name
        ]

        return "".join(fixed)

    ### Category name switch.
    def _r_category(self, cat_i, category_n):
        switch = {
            0: categories[5],
            1: categories[short_cat.index(cat_i)] \
                if cat_i != short_cat[5] and isinstance(cat_i, str) \
                else None,
            2: categories[cat_i] \
                if isinstance(cat_i, int) \
                else None
        }

        return switch.get(category_n)

    ### Choose category name.
    def _r_get_category(self, args, cat_i):
        if args.subreddit:
            category_n = 0 \
                if cat_i == short_cat[5] \
                else 1
        elif args.basic:
            category_n = 2

        return category_n

    ### File name switch that stores all possible Subreddit file name formats.
    def _get_sub_fname(self, category, end, index, n_res_or_kwds, subreddit, time_filter):
        filter_str = "-past-%s" % time_filter
        search = "%s-%s-'%s'" % (subreddit, category.lower(), n_res_or_kwds)
        standard = "%s-%s-%s-%s" % (subreddit, category.lower(), n_res_or_kwds, end)

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

        ending = None \
            if cat_i == short_cat[5] or cat_i == 5 \
            else end
        time_filter = None \
            if each_sub[2] == None or each_sub[2] == "all" \
            else each_sub[2]

        if each_sub[2] == None or each_sub[2] == "all":
            index = 0 \
                if cat_i == short_cat[5] or cat_i == 5 \
                else 1
        else:
            index = 2 \
                if cat_i == short_cat[5] or cat_i == 5 \
                else 3

        filename = self._get_sub_fname(category, ending, index, each_sub[1], sub, time_filter)
        filename = self._check_len(filename)

        if args.rules:
            return filename + "-rules"
        
        return filename

    ### Determine file name format for Subreddit scraping.
    def r_fname(self, args, cat_i, each_sub, sub):
        raw_n = ""
        end = "result" \
            if isinstance(each_sub[1], int) and int(each_sub[1]) < 2 \
            else "results"

        raw_n = self._get_raw_n(args, cat_i, end, each_sub, sub)

        return self._fix(raw_n)

    ### Determine file name format for Redditor scraping.
    def u_fname(self, limit, string):
        end = "result" \
            if int(limit) < 2 \
            else "results"
        string = self._fix(string)
        raw_n = str("%s-%s-%s" % (string, limit, end))

        return self._fix(raw_n)

    ### Determine file name format for comments scraping.
    def c_fname(self, limit, string):
        string = self._check_len(string)
        if int(limit) != 0:
            end = "result" \
                if int(limit) < 2 \
                else "results"
            raw_n = str("%s-%s-%s" % (string, limit, end))
        else:
            raw_n = str("%s-%s" % (string, "RAW"))

        return self._fix(raw_n)

class Export():
    """
    Methods for creating directories and export the file.
    """

    ### Get filename extension.
    @staticmethod
    def _get_filename_extension(f_name, f_type, scrape):
        dir_path = "../scrapes/%s/%s" % (date, scrape)

        extension = ".csv" \
            if f_type == eo[0] \
            else ".json"

        return dir_path + "/%s%s" % (f_name, extension)

    ### Export to CSV.
    @staticmethod
    def _write_csv(data, filename):
        with open(filename, "w", encoding = "utf-8") as results:
            writer = csv.writer(results, delimiter = ",")
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))

    ### Export to JSON.
    @staticmethod
    def _write_json(data, filename):
        with open(filename, "w", encoding = "utf-8") as results:
            json.dump(data, results, indent = 4)
    
    ### Write data dictionary to CSV or JSON.
    @staticmethod
    def export(data, f_name, f_type, scrape):
        InitializeDirectory.make_type_directory(scrape)
        filename = Export._get_filename_extension(f_name, f_type, scrape)

        Export._write_json(data, filename) \
            if f_type == eo[1] \
            else Export._write_csv(data, filename)
