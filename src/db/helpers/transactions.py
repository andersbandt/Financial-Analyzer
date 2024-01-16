"""
    @file transactions.py
    @brief SQL database helper for the 'transactions' table
"""


# import needed modules
import datetime
import sqlite3

# import user created modules
from db import DATABASE_DIRECTORY
from statement_types.Transaction import Transaction


##############################################################################
####      DATABASE MODIFICATION FUNCTIONS    #################################
##############################################################################

# insert_transaction: inserts a Transaction object into the SQL database
def insert_transaction(transaction: Transaction) -> bool:
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO transactions (date, account_id, category_id, amount, description, note, date_added) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (
                transaction.date,
                transaction.account_id,
                transaction.category_id,
                transaction.amount,
                transaction.description,
                transaction.note,
                datetime.datetime.now(),
            ),
        )
        conn.set_trace_callback(None)
    return True


# updates Transaction objects (must have sql key)
def update_transaction_category(transaction: Transaction) -> bool:
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE transactions SET category_id=? WHERE id=?",
            (transaction.category_id, transaction.sql_key),
        )
    return True


def update_transaction_note(sql_key, note):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE transactions SET note=? WHERE id=?",
            (note, sql_key),
        )
    return True


# delete_transaction: deletes a Transaction
def delete_transaction(sql_key: str) -> bool:
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE key=?", (sql_key,))
    return True


##############################################################################
####      DATABASE RETRIEVAL FUNCTIONS    ####################################
##############################################################################

def get_transaction(transaction: Transaction):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM transactions WHERE date=? AND account_id=? AND amount=? AND description=?",
            (transaction.date, transaction.account_id, transaction.amount, transaction.description),
        )
        results = cur.fetchall()
    if len(results) == 0:
        return None
    else:
        return results


# gets ledger data for ALL the transactions in a certain date range
#   note: date must be in the format of year-month-date
def get_transactions_between_date(date_start, date_end):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date ASC",
            (date_start, date_end),
        )
        ledger_data = cur.fetchall()
    return ledger_data


# get_uncategorized_transactions:
def get_uncategorized_transactions():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE category_id=0 ORDER BY date DESC")
        ledger_data = cur.fetchall()
    return ledger_data


# get_uncategorized_transactions:
def get_transactions_description_keyword(desc_str):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE description LIKE ? ORDER BY date ASC", (f"%{desc_str}%",))
        ledger_data = cur.fetchall()
    return ledger_data



def get_transaction_by_sql_key(sql_key):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE id=?", (sql_key,))
        ledger_data = cur.fetchall()
    return ledger_data


def get_transactions_by_category_id(category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE category_id=? ORDER BY date ASC", (category_id,))
        ledger_data = cur.fetchall()
    return ledger_data


# gets ledger data for a certain account's transactions in a certain date range
def get_account_transactions_between_date(account_id, date_start, date_end):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM transactions WHERE account_id=? AND date BETWEEN ? AND ? ORDER BY date ASC",
            (account_id, date_start, date_end),
        )
        ledger_data = cur.fetchall()
    return ledger_data


def get_transactions_ledge_data():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM transactions",
        )
        ledger_data = cur.fetchall()
    return ledger_data

