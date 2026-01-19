

# import needed modules
import sys
import argparse
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


# main: main function of the program
def main(tab_num=None, action_num=None):
    """
    Main function that starts the CLI application.

    Args:
        tab_num: Optional tab number (1-9) to run directly
        action_num: Optional action number within the tab to run directly
    """
    # set log level
    logger.remove()
    level = ["INFO", "DEBUG"]
    logger.add(sys.stdout, level=level[1])

    # run main CLI with optional direct action
    cli_main.main(tab_num=tab_num, action_num=action_num)


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
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Financial Analyzer CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              Run interactive menu
  python main.py -15          Run tab 1, action 5
  python main.py -64          Run tab 6, action 4
        """
    )
    parser.add_argument(
        '-t', '--target',
        type=str,
        metavar='XY',
        help='Run specific tab X and action Y (e.g., -t 15 for tab 1, action 5)'
    )

    # Also support shorthand like -15 (without -t flag)
    # Check if there's an argument that looks like -XY
    if len(sys.argv) == 2 and sys.argv[1].startswith('-') and sys.argv[1][1:].isdigit():
        # Convert -15 to --target 15
        sys.argv = [sys.argv[0], '--target', sys.argv[1][1:]]

    args = parser.parse_args()

    # Parse tab and action numbers
    tab_num = None
    action_num = None
    if args.target:
        if len(args.target) < 2:
            print(f"Error: Target '{args.target}' must be at least 2 digits (tab + action)")
            sys.exit(1)
        try:
            tab_num = int(args.target[0])
            action_num = int(args.target[1:])
        except ValueError:
            print(f"Error: Invalid target format '{args.target}'. Expected format: XY (e.g., 15)")
            sys.exit(1)

    # Initialize database
    status = db_init()
    if not status:
        print("Something went wrong with database. EXITING!")
        sys.exit()

    # Run main with optional direct action
    main(tab_num=tab_num, action_num=action_num)
