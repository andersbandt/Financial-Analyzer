
# import needed modules
import sqlite3
import sys
from collections import defaultdict
from random import choice
from loguru import logger

# import user created modules
import cli

colors = ["blue", "cyan", "green", "magenta", "red", "yellow"]
color_per_module = defaultdict(lambda: choice(colors))


def formatter(record):
    color_tag = color_per_module[record["name"]]
    return "<" + color_tag + ">[{name}]</> <bold>{message}</>\n{exception}"


logger.add(sys.stdout, colorize=True, format=formatter)


# main: main function of the program. Really just calls gui_driver
def main():
    cli.main()


def db_init():
    """Create the database using the values of TableStatements."""
    from db import DATABASE_DIRECTORY, TableStatements, all_tables_init, populate_tables

    # append every single variable string in class
    statements = []
    for value in TableStatements.__dict__.values():
        if str(value).startswith(
            "CREATE"
        ):  # Only append the values of the variables. Without this we would get the built-ins and the docstring.
            statements.append(value)

    # execute init sequence
    try:
        all_tables_init(statements, DATABASE_DIRECTORY)
        populate_tables(DATABASE_DIRECTORY)
    except sqlite3.Error: # I don't think this is needed as I added a try/except bblock in the db/__init__.py
        logger.exception("Tables already in db file.")


# thing that's gotta be here
if __name__ == "__main__":
    db_init() # only used if database doesn't exist
    main()
