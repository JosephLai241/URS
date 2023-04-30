"""
Testing `DirInit.py`.
"""


import os

from urs.utils.DirInit import InitializeDirectory


class TestInitializeDirectoryCreateDirsMethod:
    """
    Testing InitializeDirectory class create_dirs() method.
    """

    def test_create_dirs_method(self):
        test_path = "../scrapes/test_dir/another_test_dir/a_final_dir"

        InitializeDirectory.create_dirs(test_path)

        assert True if os.path.isdir(test_path) else False
