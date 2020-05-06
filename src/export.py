#===============================================================================
#                               Export Functions
#===============================================================================
import csv
import json
from . import global_vars

### Fix fname if illegal filename characters are present
def fix(name,illegal_chars):
    fix = ["_" if char in illegal_chars else char for char in name]
    return "".join(fix)

### Determine file name format for Subreddit scraping
def r_fname(args,cat_i,search_for,sub,illegal_chars):
    raw_n = ""
    if args.sub:
        if cat_i == global_vars.short_cat[5]:
            raw_n = str(("r-%s-%s-'%s' %s") % (sub,global_vars.categories[5],search_for,global_vars.date))
            fname = fix(raw_n,illegal_chars)
        else:
            raw_n = str(("r-%s-%s %s") % (sub,global_vars.categories[global_vars.short_cat.index(cat_i)],global_vars.date))
            fname = fix(raw_n,illegal_chars)
    elif args.basic:
        if cat_i == 5:
            raw_n = str(("r-%s-%s-'%s' %s") % (sub,global_vars.categories[cat_i],search_for,global_vars.date))
            fname = fix(raw_n,illegal_chars)
        else:
            raw_n = str(("r-%s-%s %s") % (sub,global_vars.categories[cat_i],global_vars.date))
            fname = fix(raw_n,illegal_chars)

    return fname

### Determine file name format for Redditor scraping
def u_fname(string,illegal_chars):
    raw_n = str(("u-%s %s") % (string,global_vars.date))
    return fix(raw_n,illegal_chars)

### Determine file name format for comments scraping
def c_fname(string,illegal_chars):
    raw_n = str(("c-%s %s") % (string,global_vars.date))
    return fix(raw_n,illegal_chars)

### Write overview dictionary to CSV or JSON
def export(fname,overview,f_type):
    if f_type == global_vars.eo[0]:
        with open("%s.csv" % fname, "w", encoding = "utf-8") as results:
            writer = csv.writer(results, delimiter = ",")
            writer.writerow(overview.keys())
            writer.writerows(zip(*overview.values()))
    elif f_type == global_vars.eo[1]:
        with open("%s.json" % fname, "w", encoding = "utf-8") as results:
            json.dump(overview,results,indent = 4)
