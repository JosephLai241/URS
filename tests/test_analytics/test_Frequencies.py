"""
Testing `Frequencies.py`.
"""


from urs.analytics import Frequencies

class TestSortGetDataMethod():
    """
    Testing Sort class get_data() method found on line 39 in Frequencies.py.
    """

    def test_get_data_method(self):
        pass

class TestSortNameAndCreateDirMethod():
    """
    Testing Sort class name_and_create_dir() method found on line 44 in 
    Frequencies.py.
    """

    def test_name_and_create_dir_method(self):
        pass

class TestSortCreateCsvMethod():
    """
    Testing Sort class create_csv() method found on line 55 in Frequencies.py.
    """

    def test_create_csv_method(self):
        plt_dict = {
            "test": 1,
            "testing": 2
        }

        assert Frequencies.Sort().create_csv(plt_dict) == {
            "words": ["test", "testing"],
            "frequencies": [1, 2]
        }
    
class TestSortCreateJsonMethod():
    """
    Testing Sort class create_json() method found on line 68 in Frequencies.py.
    """

    def test_create_json_method(self):
        file = ["test", "something"]
        plt_dict = {
            "test": 1,
            "testing": 2
        }

        assert Frequencies.Sort().create_json(file, plt_dict) == {
            "raw_file": "test",
            "data": {
                "test": 1,
                "testing": 2
            }
        }

class TestExportFrequenciesExportMethod():
    """
    Testing ExportFrequencies class export() method found on line 82 in 
    Frequencies.py.
    """

    def test_export_method(self):
        pass


class TestPrintConfirmConfirmMethod():
    """
    Testing PrintConfirm class confirm() method found on line 93 in Frequencies.py.
    """

    def test_confirm_method(self):
        pass
