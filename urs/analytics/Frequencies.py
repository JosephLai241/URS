"""
Frequencies generator
=====================
Get frequencies for words that are found in submission titles, bodies, and/or
comments within scraped data.
"""


from argparse import Namespace
from typing import Any, Dict, List, Literal, Tuple, Union

from colorama import Fore, Style
from halo import Halo

from urs.analytics.utils.PrepData import GetPath, PrepData
from urs.utils.Export import Export
from urs.utils.Global import Status
from urs.utils.Logger import LogAnalytics
from urs.utils.Titles import AnalyticsTitles


class Sort:
    """
    Methods for sorting the frequencies data.
    """

    def get_data(self, scrape_file: List[str]) -> Tuple[str, Dict[str, int]]:
        """
        Get data from scrape file.

        :param list[str] scrape_file: The path to the directory in which the analytical
            data will be written.

        :returns: The path to the directory in which the analytical data will be
            written, and a `dict[str, int]` containing extracted scrape data.
        :rtype: `(str, dict[str, int])`
        """

        analytics_dir, scrape_type = GetPath.get_scrape_type(
            scrape_file[0], "frequencies"
        )

        return analytics_dir, PrepData.prep(scrape_file[0], scrape_type)

    def name_and_create_dir(
        self, analytics_dir: str, args: Namespace, scrape_file: List[str]
    ) -> Tuple[Literal["csv", "json"], str]:
        """
        Name the new file and create the analytics directory.

        :param str analytics_dir: The path to the directory in which the analytical
            data will be written.
        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        :param list[str] scrape_file: A `list[str]` containing scrape files and
            file formats to generate wordclouds with.

        :returns: The file format and the filename.
        :rtype: `(str, str)`
        """

        f_type = "csv" if args.csv else "json"

        filename = GetPath.name_file(analytics_dir, scrape_file[0])

        return f_type, filename

    def create_csv(self, plt_dict: Dict[str, int]) -> Dict[str, List[Union[str, int]]]:
        """
        Create CSV structure for exporting.

        :param dict[str, int] plt_dict: A `dict[str, int]` containing word frequency
            data.

        :returns: A `dict[str, list[str | int]]` containing word frequency data.
        :rtype: `Dict[str, List[Union[str, int]]]`
        """

        overview = {"words": [], "frequencies": []}

        for word, frequency in plt_dict.items():
            overview["words"].append(word)
            overview["frequencies"].append(frequency)

        return overview

    def create_json(
        self, plt_dict: Dict[str, int], scrape_file: List[str]
    ) -> Dict[str, Any]:
        """
        Create JSON structure for exporting.

        :param dict[str, int] plt_dict: A `dict[str, int]` containing word frequency
            data.
        :param list[str] scrape_file: A `list[str]` containing files and file
            formats to generate wordclouds with.

        :returns: A `dict[str, list[str | int]]` containing word frequency data.
        :rtype: `Dict[str, List[Union[str, int]]]`
        """

        return {"raw_file": scrape_file[0], "data": plt_dict}


class ExportFrequencies:
    """
    Methods for exporting the frequencies data.
    """

    @staticmethod
    @LogAnalytics.log_export
    def export(data: Dict[str, Any], f_type: str, filename: str) -> None:
        """
        Write data dictionary to JSON or CSV.

        :param dict[str, Any] data: A dictionary containing word frequency data.
        :param str f_type: The file format.
        :param str filename: The file name.
        """

        Export.write_json(data, filename) if f_type == "json" else Export.write_csv(
            data, filename
        )


class GenerateFrequencies:
    """
    Methods for generating word frequencies.
    """

    @staticmethod
    @LogAnalytics.generator_timer("frequencies")
    def generate(args: Namespace) -> None:
        """
        Generate frequencies.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        """

        AnalyticsTitles.f_title()

        for scrape_file in args.frequencies:
            analytics_dir, plt_dict = Sort().get_data(scrape_file)
            f_type, filename = Sort().name_and_create_dir(
                analytics_dir, args, scrape_file
            )

            Halo().info("Generating frequencies.")
            print()
            data = (
                Sort().create_csv(plt_dict)
                if args.csv
                else Sort().create_json(plt_dict, scrape_file)
            )

            export_status = Status(
                Style.BRIGHT
                + Fore.GREEN
                + f"Frequencies exported to {'/'.join(filename.split('/')[filename.split('/').index('scrapes'):])}.",
                "Exporting frequencies.",
                "white",
            )

            export_status.start()
            ExportFrequencies.export(data, f_type, filename)
            export_status.succeed()
            print()
