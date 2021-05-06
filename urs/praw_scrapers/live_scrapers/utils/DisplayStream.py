"""
Display stream
==============
Defining methods to format data that will appear in the terminal. 
"""


from colorama import (
    Fore,
    Style
)

class DisplayStream():
    """
    Methods to format and display Reddit stream objects.
    """

    @staticmethod
    def display(obj, object_type):
        """
        Format and print string containing stream information.

        Parameters
        ----------
        obj: dict
            Dictionary containing Reddit comment or submission data
        object_type: str
            String denoting which string format to use

        Returns
        -------
        None
        """

        if object_type == "submissions":
            submission_stream = r"""
created_utc: {created_utc} 
type: submission

author: {author}
id: {id}
is_original_content: {is_original_content}
is_self: {is_self}
link_flair_text: {link_flair_text}
name: {name}
nsfw: {nsfw}
num_comments: {num_comments}
permalink: {permalink}
score: {score}
selftext: {selftext}
spoiler: {spoiler}
stickied: {stickied}
title: {title}
upvote_ratio: {upvote_ratio}
url: {url}
""".format(created_utc = obj["created_utc"],
            author = obj["author"],
            id = obj["id"],
            is_original_content = obj["is_original_content"],
            is_self = obj["is_self"],
            link_flair_text = obj["link_flair_text"],
            name = obj["name"],
            nsfw = obj["nsfw"],
            num_comments = obj["num_comments"],
            permalink = obj["permalink"],
            score = obj["score"],
            title = obj["title"],
            selftext = obj["selftext"] \
                if obj["selftext"] \
                else None,
            spoiler = obj["spoiler"],
            stickied = obj["stickied"],
            upvote_ratio = obj["upvote_ratio"],
            url = obj["url"],
            )

            print(submission_stream)
            print(Fore.WHITE + Style.BRIGHT + "-" * 30)