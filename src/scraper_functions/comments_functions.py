#===============================================================================
#                        Post Comments Scraping Functions
#===============================================================================
from .. import export, global_vars, validation

### Global variables
convert_time = global_vars.convert_time
eo = global_vars.eo
illegal_chars = global_vars.illegal_chars
s_t = global_vars.s_t

### Check if posts exist and list posts that are not found
def list_posts(reddit,post_list,parser):
    print("\nChecking if post(s) exist...")
    posts,not_posts = validation.existence(reddit,post_list,parser,s_t,s_t[2])
    if not_posts:
        print("\nThe following posts were not found and will be skipped:")
        print("-"*55)
        print(*not_posts,sep = "\n")

    return posts

### Make c_master dictionary from posts list
def c_c_dict(posts):
    return dict((post,None) for post in posts)

### Add list of dictionary of comments attributes to use when sorting.
### Handle deleted Redditors or edited time if applicable.
def add_comment(titles,comment,usr):
    c_set = dict((title,None) for title in titles)
    c_set[titles[0]] = comment.parent_id
    c_set[titles[1]] = comment.id
    if usr:
        c_set[titles[2]] = comment.author.name
    else:
        c_set[titles[2]] = "[deleted]"
    c_set[titles[3]] = convert_time(comment.created_utc)
    c_set[titles[4]] = comment.score
    c_set[titles[5]] = comment.body
    if str(comment.edited).isalpha():
        c_set[titles[6]] = comment.edited
    else:
        c_set[titles[6]] = convert_time(comment.edited)
    c_set[titles[7]] = comment.is_submitter
    c_set[titles[8]] = comment.stickied

    return [c_set]

### Recycle that code. Append comments to all dictionary differently if raw is
### True or False
def to_all(titles,comment,submission,all,bool,raw):
    if raw:
        add = add_comment(titles,comment,bool)
        all[comment.id] = add
    else:
        cpid = comment.parent_id.split("_",1)[1]
        if cpid == submission.id:
            add = add_comment(titles,comment,bool)
            all[comment.id] = [add]
        elif cpid in all.keys():
            append = add_comment(titles,comment,bool)
            all[cpid].append({comment.id:append})
        else:
            for more_c in all.values():
                for d in more_c:
                    if isinstance(d,dict):
                        sub_set = add_comment(titles,comment,bool)
                        if cpid in d.keys():
                            d[cpid].append({comment.id:sub_set})
                        else:
                            d[comment.id] = [sub_set]

### Sort comments. Handle submission author name if Redditor has deleted their account
def s_comments(all,titles,submission,raw):
    for comment in submission.comments.list():
        try:
            to_all(titles,comment,submission,all,True,raw)
        except AttributeError:
            to_all(titles,comment,submission,all,False,raw)

### Get and sort comments from posts
def gs_comments(reddit,post,limit):
    submission = reddit.submission(url=post)
    titles = ["Parent ID","Comment ID","Author","Date Created","Upvotes","Text","Edited?","Is Submitter?","Stickied?"]
    submission.comments.replace_more(limit=None)

    all = dict()
    if int(limit) == 0:
        print("\nProcessing all comments in raw format from Reddit post '%s'..." % submission.title)
        print("\nThis may take a while. Please wait.")
        s_comments(all,titles,submission,True)
    else:
        print(("\nProcessing %s comments and including second and third-level replies from Reddit post '%s'...") % (limit,submission.title))
        print("\nThis may take a while. Please wait.")
        s_comments(all,titles,submission,False)
        all = {key: all[key] for key in list(all)[:int(limit)]}

    return all

### Get, sort, then write scraped comments to CSV or JSON
def w_comments(reddit,post_list,c_master,args):
    for post,limit in c_master.items():
        title = reddit.submission(url=post).title
        overview = gs_comments(reddit,post,limit)
        f_name = export.c_fname(title,illegal_chars)
        if args.csv:
            export.export(f_name,overview,eo[0])
            csv = "\nCSV file for '%s' comments created." % title
            print(csv)
            print("-"*(len(csv) - 1))
        elif args.json:
            export.export(f_name,overview,eo[1])
            json = "\nJSON file for '%s' comments created." % title
            print(json)
            print("-"*(len(json) - 1))
