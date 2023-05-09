"""
Analytical Tools Validator
==========================
Contains Pydantic validation Models for analytical tools.
"""

from typing import Optional

from pydantic import BaseModel

from urs.cli.utils import DebuggableEnum


class WordcloudExportFormats(DebuggableEnum):
    """
    Contains all possible export formats for wordcloud generation.
    """

    EPS = "eps"
    """
    Export to .eps format.
    """
    JPEG = "jpeg"
    """
    Export to .jpeg format.
    """
    JPG = "jpg"
    """
    Export to .jpg format.
    """
    PDF = "pdf"
    """
    Export to .pdf format.
    """
    PNG = "png"
    """
    Export to .png format. This is the default export format.
    """
    PS = "ps"
    """
    Export to .ps format.
    """
    RGBA = "rgba"
    """
    Export to .rgba format.
    """
    TIF = "tif"
    """
    Export to .tif format.
    """
    TIFF = "tiff"
    """
    Export to .tiff format.
    """


class WordcloudSettings(BaseModel):
    """
    A `Pydantic` Model containing Subreddit scrape settings.
    """

    export_format: Optional[WordcloudExportFormats] = WordcloudExportFormats.PNG
    file: str
