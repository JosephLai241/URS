#===============================================================================
#                       Subreddit Scraping Functions
#===============================================================================
from .. import export, global_vars

### Global variables
categories = global_vars.categories
convert_time = global_vars.convert_time
eo = global_vars.eo
illegal_chars = global_vars.illegal_chars
options = global_vars.options
short_cat = global_vars.short_cat

### Make s_master dictionary from Subreddit list
def c_s_dict(subs):
    return dict((sub,[]) for sub in subs)

### Print scraping details for each Subreddit
def print_settings(s_master,args):
    print("\n------------------Current settings for each Subreddit-------------------")
    print("\n{:<25}{:<17}{:<30}".format("Subreddit","Category","Number of results / Keyword(s)"))
    print("-"*72)
    for sub,settings in s_master.items():
        for each in settings:
            if args.basic == False:
                cat_i = short_cat.index(each[0].upper())
                specific = each[1]
            else:
                cat_i = each[0]
                specific = each[1]
            print("\n{:<25}{:<17}{:<30}".format(sub,categories[cat_i],specific))

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

### Get Subreddit posts
def get_posts(args,reddit,sub,cat_i,search_for):
    subreddit = reddit.subreddit(sub)
    if cat_i == short_cat[5] or cat_i == 5:
        print(("\nSearching posts in r/%s for '%s'...") % (sub,search_for))
        collected = subreddit.search("%s" % search_for)
    else:
        if args.sub:
            print(("\nProcessing %s %s results from r/%s...") % (search_for,categories[short_cat.index(cat_i)],sub))
        elif args.basic:
            print(("\nProcessing %s %s results from r/%s...") % (search_for,categories[cat_i],sub))
        if cat_i == short_cat[0] or cat_i == 0:
            collected = subreddit.hot(limit = int(search_for))
        elif cat_i == short_cat[1] or cat_i == 1:
            collected = subreddit.new(limit = int(search_for))
        elif cat_i == short_cat[2] or cat_i == 2:
            collected = subreddit.controversial(limit = int(search_for))
        elif cat_i == short_cat[3] or cat_i == 3:
            collected = subreddit.top(limit = int(search_for))
        elif cat_i == short_cat[4] or cat_i == 4:
            collected = subreddit.rising(limit = int(search_for))

    return collected

### Sort collected dictionary. Reformat dictionary if exporting to JSON
def sort_posts(args,collected):
    print("\nThis may take a while. Please wait.")
    titles = ["Title","Flair","Date Created","Upvotes","Upvote Ratio","ID",\
                "Edited?","Is Locked?","NSFW?","Is Spoiler?","Stickied?",\
                "URL","Comment Count","Text"]

    if args.csv:
        overview = dict((title,[]) for title in titles)
        for post in collected:
            overview["Title"].append(post.title)
            overview["Flair"].append(post.link_flair_text)
            overview["Date Created"].append(convert_time(post.created))
            overview["Upvotes"].append(post.score)
            overview["Upvote Ratio"].append(post.upvote_ratio)
            overview["ID"].append(post.id)
            if str(post.edited).isalpha():
                overview["Edited?"].append(post.edited)
            else:
                overview["Edited?"].append(convert_time(post.edited))
            overview["Is Locked?"].append(post.locked)
            overview["NSFW?"].append(post.over_18)
            overview["Is Spoiler?"].append(post.spoiler)
            overview["Stickied?"].append(post.stickied)
            overview["URL"].append(post.url)
            overview["Comment Count"].append(post.num_comments)
            overview["Text"].append(post.selftext)
    elif args.json:
        overview = dict()
        counter = 1
        for post in collected:
            edit_t = "%s" % post.edited if str(post.edited).isalpha() else "%s" % convert_time(post.edited)
            e_p = [post.title,post.link_flair_text,\
                    convert_time(post.created),\
                    post.score,post.upvote_ratio,post.id,edit_t,post.locked,\
                    post.over_18,post.spoiler,post.stickied,post.url,post.num_comments,post.selftext]
            overview["Post %s" % counter] = {title:value for title,value in zip(titles,e_p)}
            counter += 1

    return overview

### Get, sort, then write scraped Subreddit posts to CSV or JSON
def gsw_sub(reddit,args,s_master):
    for sub,settings in s_master.items():
        for each in settings:
            if args.basic == False:
                cat_i = each[0].upper()
            else:
                cat_i = each[0]
            search_for = each[1]
            collected = get_posts(args,reddit,sub,cat_i,search_for)
            overview = sort_posts(args,collected)
            fname = export.r_fname(args,cat_i,search_for,sub,illegal_chars)
            if args.csv:
                export.export(fname,overview,eo[0])
                csv = "\nCSV file for r/%s created." % sub
                print(csv)
                print("-"*(len(csv) - 1))
            elif args.json:
                export.export(fname,overview,eo[1])
                json = "\nJSON file for r/%s created." % sub
                print(json)
                print("-"*(len(json) - 1))
