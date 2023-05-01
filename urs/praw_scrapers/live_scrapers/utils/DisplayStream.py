"""
Display stream
==============
Defining methods to format data that will appear in the terminal. 
"""


from typing import Any, Dict, List

from prettytable import PrettyTable


class DisplayStream:
    """
    Methods to format and display Reddit stream objects.
    """

    @staticmethod
    def _populate_table(
        include_fields: List[str],
        obj: Dict[str, Any],
        prefix: str,
        pretty_stream: PrettyTable,
    ) -> None:
        """
        Populate the PrettyTable rows with Reddit object metadata.

        :param list[str] include_fields: A `list[str]` containing dictionary keys
            that will be added to the `PrettyTable` row.
        :param dict[str, Any] obj: A `dict[str, Any]` containing Reddit comment
            submission data.
        :param str prefix: The prefix to prepend to an attribute.
        :param PrettyTable pretty_stream: A `PrettyTable` instance.
        """

        for attribute, data in obj.items():
            if attribute in include_fields:
                pretty_stream.add_row([prefix + attribute, data])

    @staticmethod
    def display(obj: Dict[str, Any]) -> None:
        """
        Format and print string containing stream information.

        :param dict[str, Any] obj: A `dict[str, Any]` containing Reddit comment
            submission data.
        """

        pretty_stream = PrettyTable()
        pretty_stream.field_names = [f"{obj['type'].capitalize()} Attribute", "Data"]

        if obj["type"] == "submission":
            include_fields = [
                "author",
                "created_utc",
                "link_flair_text",
                "nsfw",
                "selftext",
                "spoiler",
                "title",
                "url",
            ]
        elif obj["type"] == "comment":
            include_fields = [
                "author",
                "body",
                "created_utc",
                "is_submitter",
            ]

            submission_fields = [
                "author",
                "created_utc",
                "link_flair_text",
                "nsfw",
                "num_comments",
                "score",
                "title",
                "upvote_ratio",
                "url",
            ]

            DisplayStream._populate_table(
                submission_fields, obj["submission"], "submission_", pretty_stream
            )

        DisplayStream._populate_table(include_fields, obj, "", pretty_stream)

        pretty_stream.sortby = f"{obj['type'].capitalize()} Attribute"
        pretty_stream.align = "l"
        pretty_stream.max_width = 120

        print(pretty_stream)
