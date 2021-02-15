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

from analytics.utils.PrepData import (
    GetPath,
    PrepData
)

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Export import Export
from urs.utils.Global import (
    analytical_tools,
    eo
)
from urs.utils.Logger import LogAnalytics
from urs.utils.Titles import AnalyticsTitles

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class ExportFrequencies():
    """
    Methods for exporting the frequencies data.
    """

    ### Write data dictionary to CSV or JSON.
    @staticmethod
    @LogAnalytics.log_export
    def export(data, filename, f_type):
        Export.write_json(data, filename) \
            if f_type == eo[1] \
            else Export.write_csv(data, filename)

class SortAndConfirm():
    """
    Methods for sorting and confirming the data.
    """

    ### Get data from scrape file.
    def get_data(self, file):
        scrape_type = GetPath.get_scrape_type(file[0])
        return PrepData.prep(file[0], scrape_type)

    ### Name the new file and create the analytics directory.
    def name_and_create(self, args, file):
        f_type = eo[0] \
            if args.csv \
            else eo[1]

        date_dir, filename = GetPath.name_file(f_type, file[0], "frequencies")
        InitializeDirectory.make_analytics_directory(date_dir, "frequencies")

        return f_type, filename

    ### Create the JSON structure for exporting.
    def create_json(self, file, plt_dict):
        return {
            "raw_file": file[0],
            "data": plt_dict
        }

    ### Print confirmation message.
    def print_confirmation(self, filename):
        confirmation = "\nFrequencies exported to %s" % filename
        print(Style.BRIGHT + Fore.GREEN + confirmation)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(confirmation) - 1))

class GenerateFrequencies():
    """
    Methods for generating word frequencies.
    """

    ### Generate frequencies.
    @staticmethod
    @LogAnalytics.generator_timer(analytical_tools[0])
    def generate(args):
        AnalyticsTitles.f_title()

        for file in args.frequencies:
            print("\nGenerating frequencies...\n")

            plt_dict = SortAndConfirm().get_data(file)
            f_type, filename = SortAndConfirm().name_and_create(args, file)

            json_data = SortAndConfirm().create_json(file, plt_dict)

            ExportFrequencies.export(json_data, filename, f_type)
            SortAndConfirm().print_confirmation(filename)
