# Display Directory Tree

![Display Directory Tree Demo GIF][display directory tree demo]

## All Flags

These are all the flags that may be used when displaying the directory tree.

```
[-t [<optional_date>]]
```

## Usage

If no date is provided, you can quickly view the directory structure for the current date. This is a quick alternative to [`nomad`][nomad] or the `tree` command.

You can also display a different day's scrapes by providing a date after the `-t` flag.

```
poetry run Urs.py -t [<optional_date>]
```

The following date formats are supported:

- `YYYY-MM-DD`
- `YYYY/MM/DD`

An error is displayed if `URS` was not run on the entered date (if the date directory is not found within the `scrapes/` directory).

[display directory tree demo]: https://github.com/JosephLai241/URS/blob/demo-gifs/utilities/tree_demo.gif?raw=true
[nomad]: https://github.com/JosephLai241/nomad
