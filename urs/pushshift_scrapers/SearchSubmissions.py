"""
Search submissions
==================
Search all publicly available submissions.
"""


import requests

class SearchSubmissions():
    """
    Methods for searching Reddit for submissions based on search parameters.
    """

    @staticmethod
    def get_submissions():
        response = requests.get("https://api.pushshift.io/reddit/search/submission?")
