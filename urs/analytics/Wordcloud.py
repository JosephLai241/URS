"""
Wordcloud Generator
===================
Generate a wordcloud based on word frequencies extracted from scraped data.
"""


import matplotlib.pyplot as plt

from colorama import (
    Fore, 
    Style
)
from halo import Halo
from pathlib import Path
from wordcloud import WordCloud

from urs.analytics.utils.PrepData import (
    GetPath,
    PrepData
)

from urs.utils.Global import Status
from urs.utils.Logger import LogAnalytics
from urs.utils.Titles import AnalyticsTitles

class SetUpWordcloud():
    """
    Methods for setting up the wordcloud.
    """

    @staticmethod
    def initialize_wordcloud(file, scrape_type):
        """
        Initialize wordcloud by setting dimensions, max font size, and generating
        it from word frequencies.

        Calls a public method from an external module:

            PrepData.prep()

        Parameters
        ----------
        file: list
            List containing scrape files and file formats to generate wordcloud with
        scrape_type: str
            String denoting the scrape type

        Returns
        -------
        wc: WordCloud
            WordCloud instance
        """

        frequencies = PrepData.prep(file[0], scrape_type)

        initialize_status = Status(
            "Generated wordcloud.",
            "Generating wordcloud.",
            "white"
        )

        initialize_status.start()
        wordcloud = WordCloud(
            height = 1200,
            max_font_size = 400,
            width = 1600
        ).generate_from_frequencies(frequencies)
        initialize_status.succeed()

        return wordcloud

    @staticmethod
    def modify_wordcloud(wc):
        """
        Further modify wordcloud preferences.

        Parameters
        ----------
        wc: WordCloud
            Wordcloud instance

        Returns
        -------
        plt: matplotlib.pyplot
            matplotlib.pyplot instance
        """

        plt.imshow(wc, interpolation = "bilinear")
        plt.axis("off")

        return plt

class FinalizeWordcloud():
    """
    Methods for either saving or displaying the wordcloud.
    """

    @LogAnalytics.log_show("wordcloud")
    def show_wordcloud(self, plt):
        """
        Display wordcloud.

        Parameters
        ----------
        plt: matplotlib.pyplot
            matplotlib.pyplot instance

        Returns
        -------
        None
        """

        Halo().info(Style.BRIGHT + Fore.GREEN + "Displaying wordcloud.")
        print()

        plt.show()

    @LogAnalytics.log_save("wordcloud")
    def save_wordcloud(self, analytics_dir, scrape_file, wc):
        """
        Save wordcloud to file.

        Calls a public method from an external module:

            GetPath.name_file()

        Parameters
        ----------
        analytics_dir: str
            String denoting the path to the directory in which the analytical
            data will be written
        scrape_file: list
            List containing scrape files and file formats to generate wordcloud with
        wc: WordCloud
            Wordcloud instance

        Returns
        -------
        new_filename: str
            String denoting the filename for the exported wordcloud
        """

        filename = GetPath.name_file(analytics_dir, scrape_file[0])

        split_path = list(Path(filename).parts)

        split_filename = split_path[-1].split(".")
        split_filename[-1] = scrape_file[-1]

        split_path[-1] = ".".join(split_filename)
        new_filename = "/".join(split_path)

        export_status = Status(
            Style.BRIGHT + Fore.GREEN + f"Wordcloud exported to {new_filename}.",
            "Exporting wordcloud.",
            "white"
        )

        export_status.start()
        wc.to_file(new_filename)
        export_status.succeed()
        print()
        
        return new_filename

class GenerateWordcloud():
    """
    Methods for generating a wordcloud.
    """

    @staticmethod
    @LogAnalytics.generator_timer("wordcloud")
    def generate(args):
        """
        Generate wordcloud.

        Calls previously defined public methods:

            FinalizeWordcloud().show_wordcloud()
            FinalizeWordcloud().save_wordcloud()
            SetUpWordcloud.initialize_wordcloud()
            SetUpWordcloud.modify_wordcloud()

        Calls public methods from external modules:

            AnalyticsTitles.wc_title()
            GetPath.get_scrape_type()
        
        Parameters
        ----------
        args: Namespace
            Namespace object containing all arguments used in the CLI

        Returns
        -------
        None
        """

        AnalyticsTitles.wc_title()

        for scrape_file in args.wordcloud:
            analytics_dir, scrape_type = GetPath.get_scrape_type(scrape_file[0], "wordcloud")
            wc = SetUpWordcloud.initialize_wordcloud(scrape_file, scrape_type)
            plt = SetUpWordcloud.modify_wordcloud(wc)

            FinalizeWordcloud().show_wordcloud(plt) \
                if args.nosave \
                else FinalizeWordcloud().save_wordcloud(analytics_dir, scrape_file, wc)
