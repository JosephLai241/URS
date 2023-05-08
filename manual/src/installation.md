> **_NOTE:_ Requires Python 3.11+ and [Poetry][poetry installation page] installed on your system.**

Run the following commands to install `URS`:

```
git clone --depth=1 https://github.com/JosephLai241/URS.git
cd URS
poetry install
poetry shell
maturin develop --release
```

> **_TIP:_** If `poetry shell` does not activate the virtual environment created by `Poetry`, run the following command to activate it:
>
> ```
> source .venv/bin/activate
> ```

[poetry installation page]: https://python-poetry.org/docs/#installation
