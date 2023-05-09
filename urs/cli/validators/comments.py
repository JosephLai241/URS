"""
Submission Comments Validator
=============================
Contains Pydantic validation Models for submission comments scraping.
"""

from pydantic import BaseModel


class CommentsSettings(BaseModel):
    """
    A `Pydantic` Model containing submission comments scrape settings.
    """

    n_results: int | None
    """
    The number of results to return, or `None` if `scrape_all` is set to `True`.
    """
    scrape_all: bool
    """
    Whether to scrape all comments within the submission.
    """
    url: str
    """
    The URL of the submission.
    """
