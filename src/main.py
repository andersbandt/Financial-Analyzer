

# import needed modules
import sys
from collections import defaultdict
from random import choice
from loguru import logger

# import user created modules
from cli import cli_main

colors = ["blue", "cyan", "green", "magenta", "red", "yellow"]
color_per_module = defaultdict(lambda: choice(colors))


def formatter(record):
    color_tag = color_per_module[record["name"]]
    return "<" + color_tag + ">[{name}]</> <bold>{message}</>\n{exception}"


# main: main function of the programr
# TODO: add an argument path that runs a certain sub menu action. Like "python main.py -64 would run 06_balances/04_retirement_modeling"
def main():
    # set log level
    logger.remove()
    level = ["INFO", "DEBUG"]
    logger.add(sys.stdout, level=level[1])

    # run main CLI
    cli_main.main()


def db_init():
    """Create the database using the values of TableStatements."""
    from db import DATABASE_DIRECTORY, TableStatements, all_tables_init, populate_tables

    print("NOTICE: you are currently using ...")
    print(f"\t\t {DATABASE_DIRECTORY}")
    print("... as your database directory!!!\n")

    # append every single variable string in class
    statements = []
    for value in TableStatements.__dict__.values():
        if str(value).startswith(
                "CREATE"
        ):  # Only append the values of the variables. Without this we would get the built-ins and the docstring.
            statements.append(value)

    # execute init sequence
    db_status = all_tables_init(statements, DATABASE_DIRECTORY)
    if not db_status:
        print("I don't think database file was able to be located!!!")
        return False

    populate_tables(DATABASE_DIRECTORY)
    return True


# thing that's gotta be here
if __name__ == "__main__":
    status = db_init()  # only used if database doesn't exist
    if not status:
        print("Something went wrong with database. EXITING!")
        sys.exit()
    main()
