"""
Utilities
=========
Miscellaneous utilities for URS.
"""


import logging
import rich

from colorama import (
    Fore,
    Style
)
from halo import Halo
from pathlib import (
    Path,
    PurePath
)
from rich.filesize import decimal
from rich.tree import Tree

from urs.utils.Global import (
    date,
    Status
)
from urs.utils.Titles import Errors

class DateTree():
    """
    Methods for creating a visual representation of a target date directory located
    within the `scrapes` directory.
    """

    @staticmethod
    def _check_date_format(date):
        """
        Check if the date format is valid. Revise date separation character if
        '/' was used instead of '-'.

        Parameters
        ----------
        date: str
            String denoting the date of the scrapes directory

        Raises
        ------
        TypeError: 
            raised if an invalid date format is entered

        Returns
        -------
        search_date:
            String denoting the date to search for
        """

        split_date = [char for char in date]

        if not any(char in split_date for char in ["-", "/"]) or len(split_date) < 10:
            raise TypeError

        if "/" in split_date:
            for i in range(len(split_date)):
                if split_date[i] == "/":
                    split_date[i] = "-"

        return "".join(split_date)

    @staticmethod
    def _find_date_directory(date):
        """
        Traverse the `scrapes/` directory to find the corresponding date directory.

        Parameters
        ----------
        date: str
            String denoting the date of the scrapes directory

        Returns
        -------
        dir_exists: boolean
            Boolean denoting whether the date directory exists within the `scrapes/`
                directory
        """

        dir_exists = False

        scrapes_dir = f"{Path(Path.cwd()).parents[0]}/scrapes"
        for path in Path(scrapes_dir).iterdir():
            if path.is_dir() and PurePath(path).name == date:
                dir_exists = True

        return dir_exists

    @staticmethod
    def _create_stack(directory, tree):
        """
        Create a stack containing paths within a directory.

        Parameters
        ----------
        directory: str
            String denoting the path to the directory
        tree: Tree instance

        Returns
        -------
        stack: list
            List containing tuples of type (Path, Tree)
        """

        return [
            (path, tree)
            for path in sorted(
                Path(directory).iterdir(), 
                key = lambda path: (path.is_file(), path.name.lower())
            )
        ]

    @staticmethod
    def _create_directory_tree(date_dir, tree):
        """
        Create the directory Tree based on the date_dir Path using iterative 
        depth-first search.

        Parameters
        ----------
        date_dir: str
            String denoting the path to the date directory
        tree: Tree instance

        Returns
        -------
        None
        """

        build_tree_status = Status(
            "Displaying directory tree.",
            f"Building directory tree for {date_dir}.",
            "cyan"
        )

        stack = DateTree._create_stack(date_dir, tree)

        visited = set()
        visited.add(Path(date_dir))

        build_tree_status.start()
        while stack:
            current = stack.pop(0)
            current_path, current_tree = current[0], current[1]

            if current_path in visited:
                continue
            elif current_path.is_dir():
                sub_tree = current_tree.add(f"[bold blue]{current_path.name}")
                sub_paths = DateTree._create_stack(current_path, sub_tree)
                
                stack = sub_paths + stack
            elif current_path.is_file():
                file_size = current_path.stat().st_size
                current_tree.add(f"[bold]{current_path.name} [{decimal(file_size)}]")

                visited.add(current_path)
        
        build_tree_status.succeed()
        print()

    @staticmethod
    def display_tree(search_date):
        """
        Display the scrapes directory for a specific date.

        Calls previously defined private methods:

            DateTree._check_date_format()
            DateTree._create_directory_tree()
            DateTree._find_date_directory()

        Parameters
        ----------
        search_date: str
            String denoting the date within the scrapes directory to search for

        Returns
        -------
        None
        """

        logging.info(f"Running tree command...")
        logging.info("")

        try:
            search_date = DateTree._check_date_format(search_date)

            find_dir_halo = Halo(color = "white", text = f"Searching for {search_date} directory within `scrapes`.")

            find_dir_halo.start()
            
            dir_exists = DateTree._find_date_directory(search_date)
            if dir_exists:
                find_dir_halo.succeed(text = f"URS was run on {search_date}.")

                date_dir = f"{Path(Path.cwd()).parents[0]}/scrapes/{search_date}"
                
                tree = Tree(f"[bold blue]scrapes/")
                dir_tree = tree.add(f"[bold blue]{search_date}")

                DateTree._create_directory_tree(date_dir, dir_tree)

                rich.print(tree)
                logging.info(f"Displayed directory tree for scrapes run on {search_date}.")
                logging.info("")
                print()
            else:
                error_messsage = f"URS was not run on {search_date}."
                find_dir_halo.fail(Fore.RED + Style.BRIGHT + error_messsage)
                print()

                logging.critical(error_messsage)
                logging.critical("ABORTING URS.\n")

                quit()
        except TypeError:
            logging.critical("INVALID DATE FORMAT.")
            logging.critical("ABORTING URS.\n")

            Errors.e_title("INVALID DATE FORMAT. ACCEPTED FORMATS: MM-DD-YYYY or MM/DD/YYYY.")
            quit()
