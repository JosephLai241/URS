#===============================================================================
#                               Export Functions
#===============================================================================
import csv
import json
import os
from . import global_vars

illegal_chars = global_vars.illegal_chars

### Fix fname if illegal filename characters are present
def fix(name):
    fix = ["_" if char in illegal_chars else char for char in name]
    return "".join(fix)

### Determine file name format for Subreddit scraping
def r_fname(args, cat_i, search_for, sub):
    raw_n = ""
    end = "result" if isinstance(search_for, int) and int(search_for) < 2 else "results"
    if args.subreddit:
        if cat_i == global_vars.short_cat[5]:
            raw_n = str(("r-%s-%s-'%s'") % 
                (sub, global_vars.categories[5], search_for))
            fname = fix(raw_n)
        else:
            raw_n = str(("r-%s-%s-%s-%s") % 
                (sub, global_vars.categories[global_vars.short_cat.index(cat_i)], 
                    search_for, end))
            fname = fix(raw_n)
    elif args.basic:
        if cat_i == 5:
            raw_n = str(("r-%s-%s-'%s'") % 
                (sub, global_vars.categories[cat_i], search_for))
            fname = fix(raw_n)
        else:
            raw_n = str(("r-%s-%s-%s-%s") % 
                (sub, global_vars.categories[cat_i], search_for, end))
            fname = fix(raw_n)

    return fname

### Determine file name format for Redditor scraping
def u_fname(string, limit):
    end = "result" if int(limit) < 2 else "results"
    raw_n = str(("u-%s-%s-%s") % (string, limit, end))
    return fix(raw_n)

### Determine file name format for comments scraping
def c_fname(string, limit):
    end = "result" if int(limit) < 2 else "results"
    raw_n = str(("c-%s-%s-%s") % (string, limit, end))
    return fix(raw_n)

### On the first run, create the directory scrapes/. Then make a sub-directory 
### corresponding with the date in which the user scraped data from Reddit if it 
### does not exist
def make_directory():
    scrapes_dir = "../scrapes"
    if not os.path.isdir(scrapes_dir):
        os.mkdir(scrapes_dir)
    
    sub_path = "../scrapes/%s" % global_vars.date
    if not os.path.isdir(sub_path):
        os.mkdir(sub_path)
    
    return sub_path

### Write overview dictionary to CSV or JSON
def export(fname, overview, f_type):
    dir_path = make_directory()

    if f_type == global_vars.eo[0]:
        filename = dir_path + "/%s.csv" % fname
        with open(filename, "w", encoding = "utf-8") as results:
            writer = csv.writer(results, delimiter = ",")
            writer.writerow(overview.keys())
            writer.writerows(zip(*overview.values()))
    elif f_type == global_vars.eo[1]:
        filename = dir_path + "/%s.json" % fname
        with open(filename, "w", encoding = "utf-8") as results:
            json.dump(overview, results, indent = 4)
