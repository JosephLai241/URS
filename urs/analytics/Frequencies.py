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

class Sort():
    """
    Methods for sorting the frequencies data.
    """

    ### Get data from scrape file.
    def get_data(self, file):
        scrape_type = GetPath.get_scrape_type(file[0])
        return PrepData.prep(file[0], scrape_type)

    ### Name the new file and create the analytics directory.
    def name_and_create_dir(self, args, file):
        f_type = eo[0] \
            if args.csv \
            else eo[1]

        date_dir, filename = GetPath.name_file(f_type, file[0], "frequencies")
        InitializeDirectory.make_analytics_directory(date_dir, "frequencies")

        return f_type, filename

    ### Create CSV structure for exporting.
    def create_csv(self, plt_dict):
        overview = {
            "words": [],
            "frequencies": []
        }

        for word, frequency in plt_dict.items():
            overview["words"].append(word)
            overview["frequencies"].append(frequency)

        return overview

    ### Create JSON structure for exporting.
    def create_json(self, file, plt_dict):
        return {
            "raw_file": file[0],
            "data": [plt_dict]
        }

class ExportFrequencies():
    """
    Methods for exporting the frequencies data.
    """

    ### Write data dictionary to JSON or CSV.
    @staticmethod
    @LogAnalytics.log_export
    def export(data, filename, f_type):
        Export.write_json(data, filename) \
            if f_type == eo[1] \
            else Export.write_csv(data, filename)

class PrintConfirm():
    """
    Methods for printing successful export message.
    """

    ### Print confirmation message.
    def confirm(self, filename):
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
            print("\nGenerating frequencies...")

            plt_dict = Sort().get_data(file)
            f_type, filename = Sort().name_and_create_dir(args, file)

            data = Sort().create_csv(plt_dict) \
                if args.csv \
                else Sort().create_json(file, plt_dict)

            ExportFrequencies.export(data, filename, f_type)
            PrintConfirm().confirm(filename)
