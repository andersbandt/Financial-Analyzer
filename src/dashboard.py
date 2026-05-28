"""
dashboard.py — graphical dashboard entry point.

Usage:
    python src/dashboard.py

Opens the Financial Dashboard at http://127.0.0.1:8050
The CLI (python src/main.py) remains unchanged for data loading and categorization.
"""

import sys
import os

# Ensure src/ is on the path regardless of where the script is run from
sys.path.insert(0, os.path.dirname(__file__))

from loguru import logger


def db_init():
    from db import DATABASE_DIRECTORY, TableStatements, all_tables_init, populate_tables

    logger.info(f"Using database: {DATABASE_DIRECTORY}")
    statements = [
        v for v in TableStatements.__dict__.values()
        if str(v).startswith("CREATE")
    ]
    ok = all_tables_init(statements, DATABASE_DIRECTORY)
    if not ok:
        logger.error("Database could not be opened. Check DATABASE_DIRECTORY in src/db/__init__.py")
        sys.exit(1)
    populate_tables(DATABASE_DIRECTORY)


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    db_init()

    from web.app import create_app
    app = create_app()
    print("\n  Financial Dashboard -> http://127.0.0.1:8050\n")
    app.run(debug=False, host="127.0.0.1", port=8050)
