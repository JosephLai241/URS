# Generating Word Frequencies

![Frequencies Demo GIF][frequencies demo]

## All Flags

These are all the flags that may be used when generating word frequencies.

```
[-f <file_path>]
    [--csv]
```

## Usage

```
poetry run Urs.py -f <file_path>
```

**Supports exporting to CSV.** To export to CSV, include the `--csv` flag.

You can generate a dictionary of word frequencies created from the words within the target fields. These frequencies are sorted from highest to lowest.

Frequencies export to JSON by default, but this tool also works well in CSV format.

Exported files will be saved to the `analytics/frequencies` directory.

# Generating Wordclouds

![Wordcloud Demo GIF][wordcloud demo]

## All Flags

```
[-wc <file_path> [<optional_export_format>]]
    [--nosave]
```

## Usage

```
poetry run Urs.py -wc <file_path>
```

## Supported Export Formats

The following are the supported export formats for wordclouds:

- `eps`
- `jpeg`
- `jpg`
- `pdf`
- `png` (default)
- `ps`
- `rgba`
- `tif`
- `tiff`

Taking word frequencies to the next level, you can generate wordclouds based on word frequencies. This tool is independent of the frequencies generator -- you do not need to run the frequencies generator before creating a wordcloud.

PNG is the default format, but you can also export to any of the options listed above by including the format as the second flag argument.

```
poetry run Urs.py -wc <file_path> [<optional_export_format>]
```

Exported files will be saved to the `analytics/wordclouds` directory.

## Display Wordcloud Instead of Saving

Wordclouds are saved to file by default. If you do not want to keep a file, include the `--nosave` flag to only display the wordcloud.

[frequencies demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/analytical_tools/frequencies_generator_demo.gif?raw=true
[wordcloud demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/analytical_tools/wordcloud_generator_demo.gif?raw=true
