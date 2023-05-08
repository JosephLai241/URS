"""
Cleanup scripts that are run after tests are done.
"""


from pathlib import Path

import pytest


def remove_directories(directory):
    """
    Recursively remove directories created by `pytest`.

    Parameters
    ----------
    directory: Path

    Returns
    -------
    None
    """

    directory = Path(directory)
    for item in directory.iterdir():
        remove_directories(item) if item.is_dir() else item.unlink()

    directory.rmdir()


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish():
    """
    Clean up after `pytest` is done running tests.
    """

    print("\nCleaning up tests...")

    try:
        remove_directories(Path("../scrapes"))
        print("Done.")
    except Exception as e:
        print("An error has occurred: %s" % e)
