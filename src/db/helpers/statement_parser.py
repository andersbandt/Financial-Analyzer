
# import needed modules
import sqlite3
from db import DATABASE_DIRECTORY


TABLE_NAME = "statement_parser"


def get_parser_config(account_id):
    """Return parser config dict for account_id, or None if not found."""
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE account_id = ?", (account_id,))
        row = cur.fetchone()
    if row is None:
        return None
    return dict(row)


def insert_parser_config(account_id, class_name, date_col=-1, amount_col=-1,
                         description_col=-1, category_col=-1, credit_col=-1,
                         exclude_header=False, inverse_amount=False):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO {TABLE_NAME} "
            "(account_id, class_name, date_col, amount_col, description_col, "
            "category_col, credit_col, exclude_header, inverse_amount) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (account_id, class_name, date_col, amount_col, description_col,
             category_col, credit_col, int(exclude_header), int(inverse_amount)),
        )


def get_all_configs():
    """Return list of all parser config dicts."""
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cur.fetchall()
    return [dict(r) for r in rows]
