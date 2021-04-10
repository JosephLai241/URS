"""
Testing `DirInit.py`.
"""


import os

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Global import date

class TestInitializeDirectoryCreateMethod():
    """
    Testing InitializeDirectory class _create() method.
    """

    def test_create(self):
        destination = "../test_dir"

        InitializeDirectory._create(destination)
        if os.path.isdir(destination) == True:
            os.rmdir(destination)
            assert True
        else:
            assert False
    
class TestInitializeDirectoryMakeDirectoryMethod():
    """
    Testing InitializeDirectory class make_directory() method.
    """

    def test_make_directory(self):
        InitializeDirectory.make_directory()

        assert True \
            if os.path.isdir("../scrapes") == True \
            and os.path.isdir("../scrapes/" + date) == True \
            else False
            
class TestInitializeDirectoryMakeTypeDirectoryMethod():
    """
    Testing InitializeDirectory class make_type_directory() method.
    """

    def test_make_type_directory(self):
        scrape = "subreddit"

        InitializeDirectory.make_type_directory(scrape)

        assert True \
            if os.path.isdir("../scrapes/%s/%s" % (date, scrape)) == True \
            else False

class TestInitializeDirectoryMakeAnalyticsDirectoryMethod():
    """
    Testing InitializeDirectory class make_analytics_directory() method.
    """

    def test_make_analytics_directory(self):
        tool_type = "wordcloud"

        InitializeDirectory.make_analytics_directory(date, tool_type)

        assert True \
            if os.path.isdir("../scrapes/%s/analytics/%s" % (date, tool_type)) == True \
            else False
