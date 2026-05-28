# import needed modules
import datetime
import sqlite3

# import user created modules
from db import DATABASE_DIRECTORY


# insert_investment: insert an investment into the database
def insert_investment(date, account_id, ticker, shares, inv_type, value, description=None, note=""):
    # get current time
    cur_date = datetime.datetime.now()

    # update description if not provided
    if description is None:
        if inv_type == "BUY":
            description = "BUY " + str(shares) + " @ " + str(value / shares)
        elif inv_type == "SELL":
            description = "SELL " + str(shares) + " @ " + str(value / shares)

    # insert into table 'investment'
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO investment (date, \
            account_id, \
            ticker, \
            shares, \
            trans_type, \
            value, \
            description, \
            note, \
            date_added) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (date,
             account_id,
             ticker,
             shares,
             inv_type,
             value,
             description,
             note,
             cur_date),
        )
    return True


# delete_transaction: deletes a Transaction
def delete_investment(sql_key: str) -> bool:
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM investment WHERE id=?", (sql_key,))
    return True

# get_account_ticker: gets all the tickers for an account
def get_account_ticker(account_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT ticker FROM investment WHERE account_id=?", (account_id,))
        ledger_data = cur.fetchall()
    return ledger_data


def get_ticker_shares(account_id, ticker):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT ticker,
            account_id,
            SUM(CASE WHEN trans_type="BUY" THEN shares
                                   WHEN trans_type="DIV" then shares
                                   WHEN trans_type="SELL" THEN -1*shares
                                   ELSE 0 END) as net_shares
            FROM investment
            WHERE account_id = ?
            AND ticker = ?
            GROUP BY ticker""", (account_id, ticker))
        ledger_data = cur.fetchall()
    return ledger_data[0]


def get_ticker_cost_basis(account_id, ticker):
    """
    Returns (avg_cost_per_share, first_buy_date) for a position.
    avg_cost = total buy value / total buy shares (average-cost method).
    first_buy_date = earliest BUY transaction date (YYYY-MM-DD string or None).
    """
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                CASE WHEN SUM(CASE WHEN trans_type='BUY' THEN shares ELSE 0 END) > 0
                     THEN SUM(CASE WHEN trans_type='BUY' THEN ABS(value) ELSE 0 END) /
                          SUM(CASE WHEN trans_type='BUY' THEN shares ELSE 0 END)
                     ELSE 0 END AS avg_cost,
                MIN(CASE WHEN trans_type='BUY' THEN date END) AS first_buy
            FROM investment
            WHERE account_id=? AND ticker=?
        """, (account_id, ticker))
        row = cur.fetchone()
    if row:
        return (float(row[0]) if row[0] else 0.0), row[1]
    return 0.0, None


def get_investment_ledge_data():
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
