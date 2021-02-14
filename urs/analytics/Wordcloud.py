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
from urs.utils.Titles import AnalyticsTitles

### Automate sending reset sequences to turn off color changes at the end of 
### every print.
init(autoreset = True)

class GenerateWordcloud():
    """
    Methods for generating a wordcloud.
    """

    ### Initialize wordcloud.
    def _initialize_wordcloud(self, file, scrape_type):
        return WordCloud().generate_from_frequencies(PrepData.prep(file[0], scrape_type))

    ### Set wordcloud preferences.
    def _modify_wordcloud(self, wc):
        plt.imshow(wc, interpolation = "bilinear")
        plt.axis("off")

        return plt

    ### Show wordcloud.
    def _show_wordcloud(self, plt):
        display_msg = "\nDisplaying wordcloud..."
        print(Style.BRIGHT + Fore.GREEN + display_msg)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(display_msg) - 1))

        plt.show()

    ### Save wordcloud.
    def _save_wordcloud(self, file, wc):
        date_dir, filename = GetPath.name_file(file[1], file[0], "wordclouds")
        InitializeDirectory.make_analytics_directory(date_dir, "wordclouds")
        wc.to_file(filename)     

        confirmation = "\nWordcloud exported to %s" % filename
        print(Style.BRIGHT + Fore.GREEN + confirmation)
        print(Style.BRIGHT + Fore.GREEN + "-" * (len(confirmation) - 1))
    
    ### Generate wordcloud.
    def generate(self, args):
        AnalyticsTitles.wc_title()

        for file in args.wordcloud:
            print("\nGenerating wordcloud...\n")

            scrape_type = GetPath.get_scrape_type(file[0])
            wc = self._initialize_wordcloud(file, scrape_type)
            plt = self._modify_wordcloud(wc)
            
            self._show_wordcloud(plt) \
                if args.nosave \
                else self._save_wordcloud(file, wc)
    