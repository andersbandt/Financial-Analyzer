import sqlite3

from db import DATABASE_DIRECTORY


# insert_investment: insert an investment into the database
def insert_investment(date, account_id, ticker, amount, inv_type):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO investment (trans_date, account_id, ticker, shares, inv_type, value, calc_type) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (date, account_id, ticker, amount, inv_type, 0, 1),
        )
    return True


def get_inv_ledge_data():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM investment")
        ledger_data = cur.fetchall()
    return ledger_data


# get_all_ticker: gets all the tickers in the database
def get_all_ticker():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT ticker FROM investment")
        tickers = cur.fetchall()
    return tickers
