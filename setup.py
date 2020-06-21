#!/usr/bin/python
from setuptools import find_packages, setup
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

DESCRIPTION = "URS: An advanced Reddit scraping & OSINT command-line tool."
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",

    "Intended Audience :: Information Technology", 
    "Intended Audience :: Other Audience", 
    "Intended Audience :: Science/Research", 
    
    "License :: OSI Approved :: MIT License", 
    
    "Operating System :: OS Independent", 
    
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3 :: Only", 

    "Topic :: Terminals", 
    "Topic :: Utilities"
]
KEYWORDS = [
    "API", 
    "comments", 
    "OSINT", 
    "Reddit", 
    "Redditor", 
    "scraper", 
    "scraping",
    "submission", 
    "Subreddit",
    "web"
]

LICENSE = "MIT"

PACKAGES = find_packages()

REQUIRES_PYTHON = ">=3.5"

PROJECT_URLS = {
    "Bug Reports": "https://github.com/JosephLai241/Universal-Reddit-Scraper/issues",
    "Build Status": "https://travis-ci.org/github/JosephLai241/URS",
    "Coverage": "https://codecov.io/gh/JosephLai241/URS",
    "Say Thanks!": "https://saythanks.io/to/jlai24142%40gmail.com",
    "Source": "https://github.com/JosephLai241/Universal-Reddit-Scraper/"
}

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
    include_package_data = True,
    python_requires = REQUIRES_PYTHON
)
