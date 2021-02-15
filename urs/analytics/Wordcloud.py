#===============================================================================
#                              Wordcloud Generator
#===============================================================================
import matplotlib.pyplot as plt

from colorama import (
    init, 
    Fore, 
    Style
)
from wordcloud import (
    ImageColorGenerator,
    WordCloud
)

from analytics.utils.PrepData import (
    GetPath,
    PrepData
)

from urs.utils.DirInit import InitializeDirectory
from urs.utils.Global import analytical_tools
from urs.utils.Logger import LogAnalytics
from urs.utils.Titles import AnalyticsTitles

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class SetUpWordcloud():
    """
    Methods for setting up the wordcloud.
    """

    ### Initialize wordcloud.
    def initialize_wordcloud(self, file, scrape_type):
        return WordCloud().generate_from_frequencies(PrepData.prep(file[0], scrape_type))

    ### Set wordcloud preferences.
    def modify_wordcloud(self, wc):
        plt.imshow(wc, interpolation = "bilinear")
        plt.axis("off")

        return plt

class FinalizeWordcloud():
    """
    Methods for either saving or displaying the wordcloud.
    """

    ### Show wordcloud.
    @LogAnalytics.log_show(analytical_tools[2])
    def show_wordcloud(self, plt):
        display_msg = "\nDisplaying wordcloud..."
        print(Style.BRIGHT + Fore.GREEN + display_msg)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(display_msg) - 1))

        plt.show()

    ### Save wordcloud.
    @LogAnalytics.log_save(analytical_tools[2])
    def save_wordcloud(self, file, wc):
        date_dir, filename = GetPath.name_file(file[1], file[0], "wordclouds")
        InitializeDirectory.make_analytics_directory(date_dir, "wordclouds")
        wc.to_file(filename)     

        confirmation = "\nWordcloud exported to %s" % filename
        print(Style.BRIGHT + Fore.GREEN + confirmation)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(confirmation) - 1))

        return filename

class GenerateWordcloud():
    """
    Methods for generating a wordcloud.
    """

    ### Generate wordcloud.
    @staticmethod
    @LogAnalytics.generator_timer(analytical_tools[2])
    def generate(args):
        AnalyticsTitles.wc_title()

        for file in args.wordcloud:
            print("\nGenerating wordcloud...\n")

            scrape_type = GetPath.get_scrape_type(file[0])
            wc = SetUpWordcloud().initialize_wordcloud(file, scrape_type)
            plt = SetUpWordcloud().modify_wordcloud(wc)
            
            FinalizeWordcloud().show_wordcloud(plt) \
                if args.nosave \
                else FinalizeWordcloud().save_wordcloud(file, wc)
