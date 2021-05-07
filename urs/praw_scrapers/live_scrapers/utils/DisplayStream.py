"""
Display stream
==============
Defining methods to format data that will appear in the terminal. 
"""


from colorama import (
    Fore,
    Style
)
from prettytable import PrettyTable

class DisplayStream():
    """
    Methods to format and display Reddit stream objects.
    """

    @staticmethod
    def populate_table(include_fields, obj, prefix, pretty_stream):
        """
        Populate the PrettyTable rows with Reddit object metadata.

        Parameters
        ----------
        include_fields: list
            List containing dictionary keys that will be added to the PrettyTable
            row
        obj: dict
            Dictionary containing Reddit comment or submission data
        prefix: str
            String denoting a prefix to prepend to an attribute
        pretty_stream: PrettyTable instance

        Returns
        -------
        None
        """

        for attribute, data in obj.items():
            if attribute in include_fields:
                pretty_stream.add_row([
                    prefix + attribute,
                    data
                ])

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

        pretty_stream = PrettyTable()
        pretty_stream.field_names = [
            "%s Attribute" % object_type.capitalize(),
            "Data"
        ]

        if object_type == "submission":
            include_fields = [
                "author",
                "created_utc",
                "distinguished",
                "edited",
                "id",
                "is_original_content",
                "is_self",
                "link_flair_text",
                "nsfw",
                "score",
                "selftext",
                "spoiler",
                "stickied",
                "title",
                "url"
            ]
        elif object_type == "comment":
            include_fields = [
                "author",
                "body",
                "created_utc",
                "distinguished",
                "edited",
                "id",
                "is_submitter",
                "link_id",
                "parent_id",
                "score",
                "stickied"
            ]
            
            submission_fields = [
                "created_utc",
                "nsfw",
                "num_comments",
                "score",
                "title",
                "upvote_ratio",
                "url",
            ]

            DisplayStream.populate_table(submission_fields, obj["submission"], "submission_", pretty_stream)

        DisplayStream.populate_table(include_fields, obj, "", pretty_stream)

        pretty_stream.sortby = "%s Attribute" % object_type.capitalize()
        pretty_stream.align = "l"
        pretty_stream.max_width = 120

        print(pretty_stream)
