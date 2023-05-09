"""
Redditor Validator
==================
Contains Pydantic validation Models for Redditor scraping.
"""

from pydantic import BaseModel


class RedditorSettings(BaseModel):
    """
    A `Pydantic` Model containing Redditor scrape settings.
    """

    n_results: int
    """
    The number of results to return.
    """
    redditor: str
    """
    The name of the Redditor.
    """
