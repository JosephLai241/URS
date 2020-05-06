#===============================================================================
#                                 Validation
#===============================================================================
import praw
from prawcore import NotFound, PrawcoreException

### Check if Subreddit(s), Redditor(s), or post exists and catch PRAW exceptions
def existence(reddit,list,parser,s_t,l_type):
    found = []
    not_found = []
    try:
        if l_type == s_t[0]:
            for sub in list:
                try:
                    reddit.subreddits.search_by_name(sub, exact = True)
                    found.append(sub)
                except NotFound:
                    not_found.append(sub)
        elif l_type == s_t[1]:
            for user in list:
                try:
                    reddit.redditor(user).id
                    found.append(user)
                except NotFound:
                    not_found.append(user)
        elif l_type == s_t[2]:
            for post in list:
                try:
                    reddit.submission(url=post)
                    found.append(post)
                except praw.exceptions.ClientException:
                    not_found.append(post)
    except PrawcoreException as error:
        print("\nERROR: %s" % error)
        print("Please recheck Reddit credentials.")
        if parser.parse_args().basic == False:
            print("\nExiting.")
            parser.exit()

    return found,not_found
