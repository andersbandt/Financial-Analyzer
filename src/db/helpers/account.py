
# import needed modules
import sqlite3

# import database directory
from db import DATABASE_DIRECTORY


def check_account_table_empty():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        # Execute the query to count entries in a table (replace 'your_table' with your table name)
        cur.execute('SELECT COUNT(*) FROM account')

    # Fetch the result
    count = cur.fetchone()[0]

    if count == 0:
        return True
    else:
        return False


def insert_account(account_name, type_int, retirement):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()

        # TODO: is there a more graceful way to handle the first account_id ?
        if check_account_table_empty():
            first_account_id = 2000000001
            # insert new account value
            cur.execute(
                """INSERT INTO account (account_id, name, type, balance, retirement) \
                VALUES(?, ?, ?, ?, ?)""",
                (first_account_id, account_name, type_int, 0.00, retirement),
            )
            return first_account_id
        else:
            # insert new account value
            cur.execute(
                """INSERT INTO account (name, type, balance, retirement) \
                VALUES(?, ?, ?, ?)""",
                (account_name, type_int, 0.00, retirement),
            )
            # get account ID that we just inserted
            cur.execute("SELECT account_id FROM account")
            new_account_id = (cur.fetchall()[-1][0])
            return new_account_id

##############################################################################
####      SETTER FUNCTIONS           #########################################
##############################################################################


def change_account_name(account_id, new_name):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()

        # Update the account name to the new name
        try:
            cur.execute("UPDATE account SET name=? WHERE account_id=?", [new_name, account_id])
            conn.commit()  # Commit the changes
        except sqlite3.Error:
            print(f"Failed to update account name from to '{new_name}'.")
            return False
    return True

##############################################################################
####      GETTER FUNCTIONS           #########################################
##############################################################################

def get_account_type(account_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT type FROM account WHERE account_id=?", [account_id])
        try:
            account_type = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)
    return account_type


def get_account_id_from_name(account_name):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT account_id FROM account WHERE name=?", [account_name])
        try:
            account_id = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)
            print("Can't convert account ID to name")
            return
    return account_id


def get_account_name_from_id(account_id):
    account_name = "NULL"
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM account WHERE account_id=?", [account_id])
        try:
            account_name = cur.fetchall()[0][
                0
            ]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)

    return account_name


# get_all_account_ids: return array of account ID's
def get_all_account_ids():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT account_id FROM account")
        account_id = [x[0] for x in cur.fetchall()]
        return account_id


# get_account_names: return a string of all account names
def get_account_names():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM account")
        account_names = [x[0] for x in cur.fetchall()]
    return account_names


def get_account_names_by_type(acc_type):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM account WHERE type=?", (acc_type,))
        account_names = [x[0] for x in cur.fetchall()]
    return account_names


def get_account_id_by_type(acc_type):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT account_id FROM account WHERE type=?", (acc_type,))
        account_names = [x[0] for x in cur.fetchall()]
    return account_names


def get_account_type_by_id(account_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT type FROM account WHERE account_id=?", (account_id,))
        acc_type = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
    return acc_type


def get_retirement_accounts(retirement_flag):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT account_id FROM account WHERE retirement=?", (retirement_flag,))
        retirement_account_id = [x[0] for x in cur.fetchall()]
    return retirement_account_id


def get_account_ledger_data():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM account")
    return cur.fetchall()




