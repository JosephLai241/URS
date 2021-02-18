"""
Preparing data for analytical tools
===================================
Helper methods to prepare data for frequencies, wordcloud, or chart generators.
"""


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
    def name_file(export_option, path, tool_type):
        split_path = path.split(".")

        split_scrapes_path = split_path[2].split("/")
        date_dir = split_scrapes_path[2]
        split_scrapes_path[3] = "analytics/%s" % tool_type
        split_path[2] = "/".join(split_scrapes_path)

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
            return json.load(raw_data)

class PrepSubreddit():
    """
    Methods for preparing Subreddit data.
    """

    ### Prepare Subreddit data.
    @staticmethod
    def prep_subreddit(data, file):
        plt_dict = dict()

        for submission in data:
            PrepData.count_words("title", submission, plt_dict)
            PrepData.count_words("text", submission, plt_dict)

        return dict(sorted(plt_dict.items(), key = lambda item: item[1], reverse = True))

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
                        PrepData.count_words("title", obj, plt_dict)
                        PrepData.count_words("body", obj, plt_dict)
                    elif obj["type"] == "comment":
                        PrepData.count_words("text", obj, plt_dict)
                ### Indicates this field is forbidden.
                elif isinstance(obj, str):
                    continue

        return dict(sorted(plt_dict.items(), key = lambda item: item[1], reverse = True))

class PrepComments():
    """
    Methods for preparing submission comments data.
    """

    ### Prepare RAW submission comments.
    @staticmethod
    def _prep_raw(data, plt_dict):
        for comment_data in data[0].values():
            PrepData.count_words("text", comment_data, plt_dict)

    ### A recursive method to prepare structured submission comments.
    @staticmethod
    def _prep_structured(data, plt_dict):
        for comment_object in data:
            for comment_data in comment_object.values():
                PrepData.count_words("text", comment_data, plt_dict)

                ### Recursive call if the comment contains the "replies" field and 
                ### if there are comments within the replies list.
                if "replies" in comment_data.keys() and comment_data["replies"]:
                    PrepComments._prep_structured(comment_data["replies"], plt_dict)
    
    ### Prepare submission comments data.
    @staticmethod
    def prep_comments(data, file):
        plt_dict = dict()

        PrepComments._prep_raw(data["data"], plt_dict) \
            if data["scrape_settings"]["n_results"] == "RAW" \
            else PrepComments._prep_structured(data["data"], plt_dict)

        return dict(sorted(plt_dict.items(), key = lambda item: item[1], reverse = True))
    
class PrepData():
    """
    Calling all methods for preparing scraped data. 
    """

    ### Removing unnecessary characters from words.
    @staticmethod
    def _remove_extras(word):
        illegal_chars = [char for char in "[(),:;.}{<>`]"]
        fixed = [
            " "
                if char in illegal_chars
                else char for char in word
        ]

        return "".join(fixed).strip()

    ### Count words that are present in a field, then update the plt_dict dictionary.
    @staticmethod
    def count_words(field, obj, plt_dict):
        words = obj[field].split(" ")
        for word in words:
            word = PrepData._remove_extras(word)
            if not word:
                continue
            
            if word not in plt_dict.keys():
                plt_dict[word] = 1
            else:
                plt_dict[word] += 1

    ### Combine all prep methods into one public method.
    @staticmethod
    def prep(file, scrape_type):
        data = Extract.extract(file)

        if scrape_type == "subreddits":
            return PrepSubreddit.prep_subreddit(data["data"], file)
        elif scrape_type == "redditors":
            return PrepRedditor.prep_redditor(data["data"], file)
        elif scrape_type == "comments":
            return PrepComments.prep_comments(data, file)
    