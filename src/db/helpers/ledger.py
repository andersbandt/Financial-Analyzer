import datetime
import sqlite3

from db import DATABASE_DIRECTORY
from statement_types.Transaction import Transaction


# insert_transaction: inserts a Transaction object into the SQL database
def insert_transaction(transaction: Transaction) -> bool:
    """
    Put the transaction into ledger_new table.
    """
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        # TODO: should this say "ledger_new" instead of "ledger"?
        cur.execute(
            "INSERT INTO ledger_new (trans_date, account_id, category_id, amount, description, date_added) VALUES(?, ?, ?, ?, ?)",
            (
                transaction.date,
                transaction.account_id,
                transaction.category_id,
                transaction.amount,
                transaction.description,
                datetime.datetime.now(),
            ),
        )
        conn.set_trace_callback(None)
    return True


# updates Transaction objects (must have sql key)
def update_transaction(transaction: Transaction) -> bool:
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE ledger SET category_id=? WHERE key=?",
            (transaction.category_id, transaction.sql_key),
        )
    return True


# delete_transaction: deletes a Transaction
def delete_transaction(sql_key: str) -> bool:
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM ledger WHERE key=?", (sql_key,))
    return True


# gets ledger data for ALL the transactions in a certain date range
#   note: date must be in the format of year-month-date
def get_transactions_between_date(date_start, date_end):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM ledger WHERE trans_date BETWEEN ? AND ? ORDER BY trans_date ASC",
            (date_start, date_end),
        )
        ledger_data = cur.fetchall()
        conn.set_trace_callback(None)
    return ledger_data


# get_uncategorized_transactions:
def get_uncategorized_transactions():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM ledger WHERE category_id=0")
        ledger_data = cur.fetchall()
        conn.set_trace_callback(None)
    return ledger_data


# gets ledger data for a certain account's transactions in a certain date range
def get_account_transactions_between_date(
    account_id, date_start, date_end, printmode=None
):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM ledger WHERE account_id=? AND trans_date BETWEEN ? AND ? ORDER BY trans_date ASC",
            (account_id, date_start, date_end),
        )
        ledger_data = cur.fetchall()
    return ledger_data
