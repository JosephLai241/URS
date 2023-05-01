"""
Wordcloud Generator
===================
Generate a wordcloud based on word frequencies extracted from scraped data.
"""


from argparse import Namespace
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
from colorama import Fore, Style
from halo import Halo
from wordcloud import WordCloud

from urs.analytics.utils.PrepData import GetPath, PrepData
from urs.utils.Global import Status
from urs.utils.Logger import LogAnalytics
from urs.utils.Titles import AnalyticsTitles


class SetUpWordcloud:
    """
    Methods for setting up the wordcloud.
    """

    @staticmethod
    def initialize_wordcloud(file: List[str], scrape_type: str) -> WordCloud:
        """
        Initialize wordcloud by setting dimensions, max font size, and generating
        it from word frequencies.

        :param list[str] file: A `list[str]` containing scrape files and file
            formats to generate wordclouds with.
        :param str scrape_type: The scrape type.

        :returns: A `WordCloud` instance.
        :rtype: `WordCloud`
        """

        frequencies = PrepData.prep(file[0], scrape_type)

        initialize_status = Status(
            "Generated wordcloud.", "Generating wordcloud.", "white"
        )

        initialize_status.start()
        wordcloud = WordCloud(
            height=1200, max_font_size=400, width=1600
        ).generate_from_frequencies(frequencies)
        initialize_status.succeed()

        return wordcloud

    @staticmethod
    def modify_wordcloud(wc: WordCloud):
        """
        Further modify wordcloud preferences.

        :param WordCloud wc: The `WordCloud` instance.

        :returns: A `matplotlib.pyplot` instance.
        :rtype: `matplotlib.pyplot`
        """

        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")

        return plt


class FinalizeWordcloud:
    """
    Methods for either saving or displaying the wordcloud.
    """

    @LogAnalytics.log_show("wordcloud")
    def show_wordcloud(self, plt) -> None:
        """
        Display wordcloud.

        :param matplotlib.pyplot plt: A `matplotlib.pyplot` instance.
        """

        Halo().info(Style.BRIGHT + Fore.GREEN + "Displaying wordcloud.")
        print()

        plt.show()

    @LogAnalytics.log_save("wordcloud")
    def save_wordcloud(
        self, analytics_dir: str, scrape_file: List[str], wc: WordCloud
    ) -> str:
        """
        Save wordcloud to file.

        :param str analytics_dir: the path to the directory in which the analytical
            data will be written.
        :param list[str] scrape_file: A `list[str]` containing scrape files and
            file formats to generate wordclouds with.
        :param WordCloud wc: The `WordCloud` instance.

        :returns: The filename for the exported wordcloud.
        :rtype: `str`
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
            "white",
        )

        export_status.start()
        wc.to_file(new_filename)
        export_status.succeed()
        print()

        return new_filename


class GenerateWordcloud:
    """
    Methods for generating a wordcloud.
    """

    @staticmethod
    @LogAnalytics.generator_timer("wordcloud")
    def generate(args: Namespace) -> None:
        """
        Generate wordcloud.

        :param Namespace args: A `Namespace` object containing all arguments used
            in the CLI.
        """

        AnalyticsTitles.wc_title()

        for scrape_file in args.wordcloud:
            analytics_dir, scrape_type = GetPath.get_scrape_type(
                scrape_file[0], "wordcloud"
            )
            wc = SetUpWordcloud.initialize_wordcloud(scrape_file, scrape_type)
            plt = SetUpWordcloud.modify_wordcloud(wc)

            FinalizeWordcloud().show_wordcloud(
                plt
            ) if args.nosave else FinalizeWordcloud().save_wordcloud(
                analytics_dir, scrape_file, wc
            )
