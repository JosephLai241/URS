#!/usr/bin/python
from setuptools import setup
import io
import os
import sys

with open("README.md", "r") as readme:
    LONG_DESCRIPTION = readme.read()

NAME = "URS"
VERSION = "3.1.0"
AUTHOR = "Joseph Lai"
EMAIL = "urs_project@protonmail.com"
URL = "https://github.com/JosephLai241/Universal-Reddit-Scraper/"

DESCRIPTION = "An advanced Reddit scraping & OSINT tool."
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"

CLASSIFIERS = ["Development Status :: 5 - Production/Stable", 
    "License :: OSI Approved :: MIT License", "Operating System :: OS Independent", 
    "Programming Language :: Python :: 3", "Topic :: Terminals", "Topic :: Utilities"]
KEYWORDS = ["API", "comments", "osint", "reddit", "redditor", "scraper", 
    "scraping", "subreddit"]

LICENSE = "MIT"

PACKAGES = ["urs"]

REQUIRES_PYTHON = ">=3.5.0"

setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = EMAIL,
    url = URL,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    long_description_content_type = LONG_DESCRIPTION_CONTENT_TYPE,
    classifiers = CLASSIFIERS,
    keywords = KEYWORDS,
    license = LICENSE,
    packages = PACKAGES,
    python_requires = REQUIRES_PYTHON
)