     __  __  _ __   ____
    /\ \/\ \/\`'__\/',__\
    \ \ \_\ \ \ \//\__, `\
     \ \____/\ \_\\/\____/
      \/___/  \/_/ \/___/

> **U**niversal **R**eddit **S**craper - A comprehensive Reddit scraping command-line tool written in Python.

![GitHub top language](https://img.shields.io/github/languages/top/JosephLai241/URS?logo=Python)
[![PRAW Version](https://img.shields.io/badge/PRAW-7.3.0-red?logo=Reddit)][praw]
[![Build Status](https://img.shields.io/github/actions/workflow/status/JosephLai241/URS/pytest.yml?branch=master)][github workflow status]
[![Codecov](https://img.shields.io/codecov/c/gh/JosephLai241/URS?logo=Codecov)][codecov]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/JosephLai241/URS)][releases]
![Total lines](https://img.shields.io/tokei/lines/github/JosephLai241/URS)
![License](https://img.shields.io/github/license/JosephLai241/URS)

```
[-h]
[-e]
[-v]

[-t [<optional_date>]]
[--check]

[-r <subreddit> <(h|n|c|t|r|s)> <n_results_or_keywords> [<optional_time_filter>]]
    [-y]
    [--csv]
    [--rules]
[-u <redditor> <n_results>]
[-c <submission_url> <n_results>]
    [--raw]
[-b]
    [--csv]

[-lr <subreddit>]
[-lu <redditor>]

    [--nosave]
    [--stream-submissions]

[-f <file_path>]
    [--csv]
[-wc <file_path> [<optional_export_format>]]
    [--nosave]
```

[codecov]: https://codecov.io/gh/JosephLai241/URS
[github workflow status]: https://github.com/JosephLai241/URS/actions/workflows/pytest.yml
[praw]: https://pypi.org/project/praw/
[releases]: https://github.com/JosephLai241/URS/releases
