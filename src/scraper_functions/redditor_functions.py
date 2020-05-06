#===============================================================================
#                        Redditor Scraping Functions
#===============================================================================
import praw
from prawcore import PrawcoreException
from .. import export, global_vars, validation

### Global variables
convert_time = global_vars.convert_time
eo = global_vars.eo
illegal_chars = global_vars.illegal_chars
s_t = global_vars.s_t

### Check if Redditor(s) exist and list Redditor(s) who are not found
def list_users(reddit,user_list,parser):
    print("\nChecking if Redditor(s) exist...")
    users,not_users = validation.existence(reddit,user_list,parser,s_t,s_t[1])
    if not_users:
        print("\nThe following Redditors were not found and will be skipped:")
        print("-"*55)
        print(*not_users,sep = "\n")

    return users

### Make u_master dictionary from Redditor list
def c_u_dict(users):
    return dict((user,None) for user in users)

### This class made my code so much cleaner man. It was created to reuse code where I had
### to pass different objects into numerous blocks of code. I never really messed
### around with classes too much before this, but I am so glad I did :')
class Listables():
    ### Initialize objects that will be used in class methods
    def __init__(self,user,overview,limit):
        self.user = user
        self.overview = overview
        self.limit = limit

        self.submissions = user.submissions.new(limit = limit)
        self.comments = user.comments.new(limit = limit)
        self.hot = user.hot(limit = limit)
        self.new = user.new(limit = limit)
        self.controversial = user.controversial(time_filter = "all", limit = limit)
        self.top = user.top(time_filter = "all", limit = limit)
        self.gilded = user.gilded(limit = limit)
        self.upvoted = user.upvoted(limit = limit)
        self.downvoted = user.downvoted(limit = limit)
        self.gildings = user.gildings(limit = limit)
        self.hidden = user.hidden(limit = limit)
        self.saved = user.saved(limit = limit)

        self.s_types = ["Submissions","Comments","Mutts","Access"]

        self.mutt_names = ["Hot","New","Controversial","Top","Gilded"]
        self.mutts = [self.hot,self.new,self.controversial,self.top,self.gilded]

        self.access_names = ["Upvoted","Downvoted","Gildings","Hidden","Saved"]
        self.access = [self.upvoted,self.downvoted,self.gildings,self.hidden,self.saved]

    ### Extracting submission or comment attributes and appending to overview dictionary
    def extract(self,cat,obj,s_types,s_type):
        for item in obj:
            if isinstance(item,praw.models.Submission):
                l = ["Title: %s" % item.title, "Date Created: %s" % convert_time(item.created),\
                        "Upvotes: %s" % item.score,"Upvote Ratio: %s" % item.upvote_ratio,\
                        "ID: %s" % item.id,"NSFW? %s" % item.over_18,"In Subreddit: %s" % item.subreddit.display_name,\
                        "Body: %s" % item.selftext]
                if s_type == s_types[0]:
                    self.overview["Submissions"].append(l)
                elif s_type == s_types[2]:
                    self.overview["%s" % cat.capitalize()].append(l)
                elif s_type == s_types[3]:
                    self.overview["%s (may be forbidden)" % cat.capitalize()].append(l)
            elif isinstance(item,praw.models.Comment):
                l = ["Date Created: %s" % convert_time(item.created_utc),\
                        "Score: %s" % item.score,"Text: %s" % item.body,"Parent ID: %s" % item.parent_id,\
                        "Link ID: %s" % item.link_id,\
                        "Edited? %s" % item.edited if str(item.edited).isalpha() else "Edited? %s" % convert_time(item.edited),\
                        "Stickied? %s" % item.stickied, "Replying to: %s" % item.submission.selftext,\
                        "In Subreddit: %s" % item.submission.subreddit.display_name]
                if s_type == s_types[1]:
                    self.overview["Comments"].append(l)
                elif s_type == s_types[2]:
                    self.overview["%s" % cat.capitalize()].append(l)
                elif s_type == s_types[3]:
                    self.overview["%s (may be forbidden)" % cat.capitalize()].append(l)

    ### Sort Redditor submissions
    def sort_submissions(self):
        self.extract(None,self.submissions,self.s_types,self.s_types[0])

    ### Sort Redditor comments
    def sort_comments(self):
        self.extract(None,self.comments,self.s_types,self.s_types[1])

    ### Sort hot, new, controversial, top, and gilded Redditor posts. The ListGenerator
    ### returns a mix of submissions and comments, so handling each differently is
    ### necessary
    def sort_mutts(self):
        for cat,obj in zip(self.mutt_names,self.mutts):
            self.extract(cat,obj,self.s_types,self.s_types[2])

    ### Sort upvoted, downvoted, gildings, hidden, and saved Redditor posts. These
    ### lists tend to raise a 403 HTTP Forbidden exception, so naturally exception
    ### handling is necessary
    def sort_access(self):
        for cat,obj in zip(self.access_names,self.access):
            try:
                self.extract(cat,obj,self.s_types,self.s_types[3])
            except PrawcoreException as error:
                print(("\nACCESS TO %s OBJECTS FORBIDDEN: %s. SKIPPING.") % (cat.upper(),error))
                self.overview["%s (may be forbidden)" % cat.capitalize()].append("FORBIDDEN")

### Get and sort Redditor information
def gs_user(reddit,user,limit):
    print(("\nProcessing %s results from u/%s's profile...") % (limit,user))
    print("\nThis may take a while. Please wait.")
    user = reddit.redditor(user)
    titles = ["Name","Fullname","ID","Date Created","Comment Karma","Link Karma", \
                "Is Employee?","Is Friend?","Is Mod?","Is Gold?","Submissions","Comments", \
                "Hot","New","Controversial","Top","Upvoted (may be forbidden)","Downvoted (may be forbidden)", \
                "Gilded","Gildings (may be forbidden)","Hidden (may be forbidden)","Saved (may be forbidden)"]

    overview = dict((title,[]) for title in titles)
    overview["Name"].append(user.name)
    overview["Fullname"].append(user.fullname)
    overview["ID"].append(user.id)
    overview["Date Created"].append(convert_time(user.created_utc))
    overview["Comment Karma"].append(user.comment_karma)
    overview["Link Karma"].append(user.link_karma)
    overview["Is Employee?"].append(user.is_employee)
    overview["Is Friend?"].append(user.is_friend)
    overview["Is Mod?"].append(user.is_mod)
    overview["Is Gold?"].append(user.is_gold)
    listable = Listables(user,overview,limit = int(limit))
    listable.sort_submissions()
    listable.sort_comments()
    listable.sort_mutts()
    listable.sort_access()

    return overview

### Get, sort, then write scraped Redditor information to CSV or JSON
def w_user(reddit,users,u_master,args):
    for user,limit in u_master.items():
         overview = gs_user(reddit,user,limit)
         f_name = export.u_fname(user,illegal_chars)
         if args.csv:
             export.export(f_name,overview,eo[0])
             csv = "\nCSV file for u/%s created." % user
             print(csv)
             print("-"*(len(csv) - 1))
         elif args.json:
             export.export(f_name,overview,eo[1])
             json = "\nJSON file for u/%s created." % user
             print(json)
             print("-"*(len(json) - 1))
