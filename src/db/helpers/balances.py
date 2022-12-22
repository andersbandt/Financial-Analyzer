import sqlite3
from db import DATABASE_DIRECTORY

def insert_account_balance(account_id, amount, date):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO balances (account_id, amount, bal_date) VALUES(?, ?, ?)",
                    (account_id, amount, date))
    return True


# gets balance data for ALL the balances in a certain date range
#   note: date must be in the format of year-month-date
def get_balances_between_date(date_start, date_end):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM balances WHERE bal_date BETWEEN ? AND ? ORDER BY bal_date ASC",
                    (date_start, date_end))
        balances_data = cur.fetchall()
    return balances_data