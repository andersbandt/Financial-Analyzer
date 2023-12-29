
# import needed modules
import sqlite3

# import user definitions
from db import DATABASE_DIRECTORY


def insert_account_balance(account_id, amount, date):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO balance (account_id, amount, bal_date) VALUES(?, ?, ?)",
            (account_id, amount, date),
        )
    return True


def get_recent_balance(account_id, add_date=False):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM balance WHERE account_id=? ORDER BY bal_date ASC",
            (account_id,),
        )
        balances_data = cur.fetchall()
    try:
        rec_bal = balances_data[-1][2]
        rec_bal_date = balances_data[-1][3]
    except IndexError:
        rec_bal = 0
        rec_bal_date = 0
    if add_date:
        return rec_bal, rec_bal_date
    else:
        return rec_bal


# gets balance data for ALL the balances in a certain date range
#   note: date must be in the format of year-month-date
def get_balances_between_date(date_start, date_end):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM balance WHERE bal_date BETWEEN ? AND ? ORDER BY bal_date ASC",
            (date_start, date_end),
        )
        balances_data = cur.fetchall()
    return balances_data
