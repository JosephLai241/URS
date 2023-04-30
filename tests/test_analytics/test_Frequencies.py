"""
Testing `Frequencies.py`.
"""


from urs.analytics import Frequencies


class TestSortGetDataMethod:
    """
    Testing Sort class get_data() method.
    """

    def test_get_data_method(self):
        pass


class TestSortNameAndCreateDirMethod:
    """
    Testing Sort class name_and_create_dir() method.
    """

    def test_name_and_create_dir_method(self):
        pass


class TestSortCreateCsvMethod:
    """
    Testing Sort class create_csv() method.
    """

    def test_create_csv_method(self):
        plt_dict = {"test": 1, "testing": 2}

        assert Frequencies.Sort().create_csv(plt_dict) == {
            "words": ["test", "testing"],
            "frequencies": [1, 2],
        }


class TestSortCreateJsonMethod:
    """
    Testing Sort class create_json() method.
    """

    def test_create_json_method(self):
        scrape_file = ["test", "something"]
        plt_dict = {"test": 1, "testing": 2}

        assert Frequencies.Sort().create_json(plt_dict, scrape_file) == {
            "raw_file": "test",
            "data": {"test": 1, "testing": 2},
        }


class TestExportFrequenciesExportMethod:
    """
    Testing ExportFrequencies class export() method.
    """

    def test_export_method(self):
        pass
