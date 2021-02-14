#===============================================================================
#                             Prepare Scrape Data
#===============================================================================
import json

class GetPath():
    """
    Methods for determining file paths.
    """

    ### Get the name of the scrape-specific directory in which the data is stored.
    @staticmethod
    def get_scrape_type(file):
        return file.split("/")[3]

    ### Name the chart or wordcloud when saving to file.
    @staticmethod
    def name_file(chart_type, export_option, path):
        split_path = path.split(".")

        split_scrapes_path = split_path[2].split("/")
        date_dir = split_scrapes_path[2]
        split_scrapes_path[3] = "analytics"
        split_path[2] = "/".join(split_scrapes_path)

        split_path[-2] = split_path[-2] + "-%s" % chart_type
        split_path[-1] = export_option

        return date_dir, ".".join(split_path)

class Extract():
    """
    Methods for extracting the data from scrape files.
    """

    ### Extract data from the file.
    @staticmethod
    def extract(file):
        with open(str(file), "r", encoding = "utf-8") as raw_data:
            return json.load(raw_data)["data"]

class PrepSubreddit():
    """
    Methods for preparing Subreddit data.
    """

    ### Prepare Subreddit data.
    @staticmethod
    def prep_subreddit(data, file):
        plt_dict = dict()

        for submission in data:
            PrepData._count_words("title", submission, plt_dict)

        return plt_dict

class PrepRedditor():
    """
    Methods for preparing Redditor data.
    """

    ### Prepare Redditor data.
    @staticmethod
    def prep_redditor(data, file):
        plt_dict = dict()

        for interactions in data["interactions"].values():
            for obj in interactions:
                ### Indicates there is valid data in this field.
                if isinstance(obj, dict):
                    if obj["type"] == "submission":
                        PrepData._count_words("title", obj, plt_dict)
                        PrepData._count_words("body", obj, plt_dict)
                    elif obj["type"] == "comment":
                        PrepData._count_words("text", obj, plt_dict)
                ### Indicates this field is forbidden.
                elif isinstance(obj, str):
                    continue

        return plt_dict

class PrepComments():
    """
    Methods for preparing submission comments data.
    """

    ### Prepare submission comments data.
    @staticmethod
    def prep_comments(data, file):
        plt_dict = dict()

        for comment in data:
            PrepData._count_words("text", comment, plt_dict)

        print(data)
        print(plt_dict)
        return plt_dict
    
class PrepData():
    """
    Calling all methods for preparing scraped data. 
    """

    ### Count words that are present in a field, then update the plt_dict dictionary.
    @staticmethod
    def _count_words(field, obj, plt_dict):
        words = obj[field].split(" ")
        for word in words:
            if word not in plt_dict.keys():
                plt_dict[word] = 1
            else:
                plt_dict[word] += 1

    ### Combine all prep methods into one public method.
    @staticmethod
    def prep(file, scrape_type):
        data = Extract.extract(file)

        if scrape_type == "subreddits":
            return PrepSubreddit.prep_subreddit(data, file)
        elif scrape_type == "redditors":
            return PrepRedditor.prep_redditor(data, file)
        elif scrape_type == "comments":
            return PrepComments.prep_comments(data, file)
    