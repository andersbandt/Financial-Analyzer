
import sqlite3
from db import DATABASE_DIRECTORY

def insert_account(account_name):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute('SELECT account_id FROM account')
        new_account_id = cur.fetchall()[-1][0] + 1  # grab latest addition (should be highest value) and add 1
        cur.execute(
            """INSERT INTO account (account_id, name) 
            VALUES(?, ?)""", 
            (new_account_id, account_name))
    return new_account_id


def get_account_id_from_name(account_name):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute('SELECT account_id FROM account WHERE name=?', [account_name])
        try:
            account_id = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)
    return account_id


def get_account_name_from_id(account_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute('SELECT name FROM account WHERE account_id=?', [account_id])
        try:
            account_name = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)

    return account_name


# get_all_account_ids: return array of account ID's
def get_all_account_ids():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM account")
        ledger_data = cur.fetchall()

    account_ids = []
    for item in ledger_data:
        account_ids.append(item[0])

    return account_ids


def get_account_names():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM account")
        account_names = [x[0] for x in cur.fetchall()]
    return account_names


def get_account_names_by_type(type):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM account WHERE type=?", (type,))
        account_names = [x[0] for x in cur.fetchall()]
    return account_names


def get_account_ledger_data():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM account")
    return cur.fetchall()


def get_account_type(account_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute('SELECT type FROM account WHERE account_id=?', [account_id])
        try:
            account_type = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)
    return account_type
