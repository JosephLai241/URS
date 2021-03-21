"""
Frequencies generator
=====================
Get frequencies for words that are found in submission titles, bodies, and/or
comments within scraped data.
"""


from colorama import (
    init, 
    Fore, 
    Style
)
from halo import Halo

from urs.analytics.utils.PrepData import (
    GetPath,
    PrepData
)

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Export import Export
from urs.utils.Global import (
    analytical_tools,
    eo,
    Status
)
from urs.utils.Logger import LogAnalytics
from urs.utils.Titles import AnalyticsTitles

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class Sort():
    """
    Methods for sorting the frequencies data.
    """

    def get_data(self, file):
        """
        Get data from scrape file.

        Calls public methods from external modules:

            GetPath.get_scrape_type()
            PrepData.prep()

        Parameters
        ----------
        file: list
            List containing scrape files and file formats to generate wordcloud with

        Returns
        -------
        frequency_data: dict
            Dictionary containing extracted scrape data
        """

        scrape_type = GetPath.get_scrape_type(file[0])
        return PrepData.prep(file[0], scrape_type)

    def name_and_create_dir(self, args, file):
        """
        Name the new file and create the analytics directory.

        Calls public methods from external modules:

            GetPath.name_file()
            InitializeDirectory.make_analytics_directory(

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI
        file: list
            List containing scrape files and file formats to generate wordcloud with

        Returns
        -------
        f_type: str
            String denoting the file format
        filename: str
            String denoting the filename
        """

        f_type = eo[0] \
            if args.csv \
            else eo[1]

        date_dir, filename = GetPath.name_file(f_type, file[0], "frequencies")
        InitializeDirectory.make_analytics_directory(date_dir, "frequencies")

        return f_type, filename

    def create_csv(self, plt_dict):
        """
        Create CSV structure for exporting.

        Parameters
        ----------
        plt_dict: dict
            Dictionary containing frequency data

        Returns
        -------
        overview: dict
            Dictionary containing frequency data
        """

        overview = {
            "words": [],
            "frequencies": []
        }

        for word, frequency in plt_dict.items():
            overview["words"].append(word)
            overview["frequencies"].append(frequency)

        return overview

    def create_json(self, file, plt_dict):
        """
        Create JSON structure for exporting.

        Parameters
        ----------
        file: list
            List containing scrape files and file formats to generate wordcloud with
        plt_dict: dict
            Dictionary containing frequency data

        Returns
        -------
        json_data: dict
            Dictionary containing frequency data
        """

        return {
            "raw_file": file[0],
            "data": plt_dict
        }

class ExportFrequencies():
    """
    Methods for exporting the frequencies data.
    """

    @staticmethod
    @LogAnalytics.log_export
    def export(data, f_type, filename):
        """
        Write data dictionary to JSON or CSV.

        Calls public methods found in external modules:

            Export.write_json()
            Export.write_csv()

        Parameters
        ----------
        data: dict
            Dictionary containing frequency data
        f_type: str
            String denoting the file format
        filename: str
            String denoting the filename

        Returns
        -------
        None
        """

        Export.write_json(data, filename) \
            if f_type == eo[1] \
            else Export.write_csv(data, filename)

class GenerateFrequencies():
    """
    Methods for generating word frequencies.
    """

    @staticmethod
    @LogAnalytics.generator_timer(analytical_tools[0])
    def generate(args):
        """
        Generate frequencies.

        Calls previously defined public methods:

            ExportFrequencies.export()
            PrintConfirm().confirm()
            Sort().create_csv()
            Sort().create_json()
            Sort().get_data()
            Sort().name_and_create_dir()
        
        Calls public methods from external modules:

            AnalyticsTitles.f_title()

        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI

        Returns
        -------
        None
        """

        AnalyticsTitles.f_title()

        for file in args.frequencies:
            f_type, filename = Sort().name_and_create_dir(args, file)
            plt_dict = Sort().get_data(file)

            generator_status = Status(
                "Generated frequencies.",
                "Generating frequencies.",
                "white"
            )

            generator_status.start()
            data = Sort().create_csv(plt_dict) \
                if args.csv \
                else Sort().create_json(file, plt_dict)
            generator_status.succeed()
            print()

            export_status = Status(
                Style.BRIGHT + Fore.GREEN + "Frequencies exported to %s." % "/".join(filename.split("/")[filename.split("/").index("scrapes"):]),
                "Exporting frequencies.",
                "white"
            )
            
            export_status.start()
            ExportFrequencies.export(data, f_type, filename)
            export_status.succeed()
            print()
            