"""
Frequencies generator
=====================
Get frequencies for words that are found in submission titles, bodies, and/or
comments within scraped data.
"""


from colorama import (
    Fore, 
    Style
)
from halo import Halo

from urs.analytics.utils.PrepData import (
    GetPath,
    PrepData
)

from urs.utils.Export import Export
from urs.utils.Global import Status
from urs.utils.Logger import LogAnalytics
from urs.utils.Titles import AnalyticsTitles

class Sort():
    """
    Methods for sorting the frequencies data.
    """

    def get_data(self, scrape_file):
        """
        Get data from scrape file.

        Calls public methods from external modules:

            GetPath.get_scrape_type()
            PrepData.prep()

        Parameters
        ----------
        scrape_file: list
            List containing scrape files and file formats to generate wordcloud with

        Returns
        -------
        analytics_dir: str
            String denoting the path to the directory in which the analytical
            data will be written
        frequency_data: dict
            Dictionary containing extracted scrape data
        """

        analytics_dir, scrape_type = GetPath.get_scrape_type(scrape_file[0], "frequencies")

        return analytics_dir, PrepData.prep(scrape_file[0], scrape_type)

    def name_and_create_dir(self, analytics_dir, args, scrape_file):
        """
        Name the new file and create the analytics directory.

        Calls public methods from external modules:

            GetPath.name_file()

        Parameters
        ----------
        analytics_dir: str
            String denoting the path to the directory in which the analytical
            data will be written
        args: Namespace
            Namespace object containing all arguments used in the CLI
        scrape_file: list
            List containing scrape files and file formats to generate wordcloud with

        Returns
        -------
        f_type: str
            String denoting the file format
        filename: str
            String denoting the filename
        """

        f_type = "csv" \
            if args.csv \
            else "json"

        filename = GetPath.name_file(analytics_dir, scrape_file[0])

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

    def create_json(self, plt_dict, scrape_file):
        """
        Create JSON structure for exporting.

        Parameters
        ----------
        plt_dict: dict
            Dictionary containing frequency data
        scrape_file: list
            List containing scrape files and file formats to generate wordcloud with

        Returns
        -------
        json_data: dict
            Dictionary containing frequency data
        """

        return {
            "raw_file": scrape_file[0],
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
            if f_type == "json" \
            else Export.write_csv(data, filename)

class GenerateFrequencies():
    """
    Methods for generating word frequencies.
    """

    @staticmethod
    @LogAnalytics.generator_timer("frequencies")
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

        for scrape_file in args.frequencies:
            analytics_dir, plt_dict = Sort().get_data(scrape_file)
            f_type, filename = Sort().name_and_create_dir(analytics_dir, args, scrape_file)

            Halo().info("Generating frequencies.")
            print()
            data = Sort().create_csv(plt_dict) \
                if args.csv \
                else Sort().create_json(plt_dict, scrape_file)

            export_status = Status(
                Style.BRIGHT + Fore.GREEN + f"Frequencies exported to {'/'.join(filename.split('/')[filename.split('/').index('scrapes'):])}.",
                "Exporting frequencies.",
                "white"
            )
            
            export_status.start()
            ExportFrequencies.export(data, f_type, filename)
            export_status.succeed()
            print()
