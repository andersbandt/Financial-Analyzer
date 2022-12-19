
import sqlite3


database_path = "databases/financials.db"

def init_connection():
    try:
        conn = sqlite3.connect(database_path)
    except sqlite3.Error as er:
        print("Uh oh, something went wrong with connecting to sqlite database:", er)
    return conn


def close_connection(conn):
    try:
        conn.close()
    except sqlite3.Error as er:
        print("Uh oh, something went wrong with connecting to sqlite", er)
        return False
    return True


##############################################################################
####      CATEGORY TABLE FUNCTIONS    ########################################
##############################################################################

def get_category_ledger_data():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM category")
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling accounts", e)
        return None
    return cur.fetchall()


def get_category_id_from_name(category_name):
    conn = init_connection()
    cur = conn.cursor()
    with conn:
        try:
            cur.execute('SELECT category_id FROM category WHERE name=?', [category_name])
        except sqlite3.Error as e:
            print("Uh oh, something went wrong finding category ID from name: ", e)
            return False
        try:
            category_id = cur.fetchall()[0][0] # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)

    close_connection(conn)
    return category_id


def get_category_name_from_id(category_id):
    conn = init_connection()
    cur = conn.cursor()
    with conn:
        try:
            cur.execute('SELECT name FROM category WHERE category_id=?', [category_id])
        except sqlite3.Error as e:
            print("Uh oh, something went wrong finding category name from ID: ", e)
            return False
        try:
            category_name = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)

    close_connection(conn)
    return category_name


def insert_category(parent, category_name):
    conn = init_connection()
    cur = conn.cursor()
    with conn:
        # check to see if category has already been added
        cur.execute('SELECT category_id FROm category WHERE name=?', category_name)
        if len(cur.fetchall()) > 0:
            print("Uh oh, the same category might already be added")
            return False

        # grab category_id for new addition
        cur.execute('SELECT category_id FROM category')
        category_id = cur.fetchall()[-1][0] + 1  # grab latest addition (should be highest value) and add 1
        try:
            cur.execute('INSERT INTO category (category_id, parent, name) \
            VALUES(?, ?, ?)', (category_id, parent, category_name))
        except sqlite3.Error as e:
            print("Uh oh, something went wrong with adding to category table: ", e)
            return False
        else:
            return True



##############################################################################
####      ACCOUNT TABLE FUNCTIONS    #########################################
##############################################################################

def get_account_id_from_name(account_name):
    conn = init_connection()
    cur = conn.cursor()
    with conn:
        try:
            cur.execute('SELECT account_id FROM account WHERE name=?', [account_name])
        except sqlite3.Error as e:
            print("Uh oh, something went wrong finding account ID from name: ", e)
            return False
        try:
            account_id = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)

    close_connection(conn)
    return account_id


def get_account_name_from_id(account_id):
    conn = init_connection()
    cur = conn.cursor()
    with conn:
        try:
            cur.execute('SELECT name FROM account WHERE account_id=?', [account_id])
        except sqlite3.Error as e:
            print("Uh oh, something went wrong finding account name from ID: ", e)
            return False
        try:
            account_name = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)

    close_connection(conn)
    return account_name


def get_all_account_ids():
    conn = init_connection()
    cur = conn.cursor()
    try:
        #conn.set_trace_callback(print)
        cur.execute("SELECT * FROM account")
        ledger_data = cur.fetchall()
        #conn.set_trace_callback(None)
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling accounts", e)
        return False

    account_ids = []
    for item in ledger_data:
        account_ids.append(item[0])

    close_connection(conn)
    return account_ids


def get_account_ledger_data():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM account")
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling accounts", e)
        return False
    return cur.fetchall()



##############################################################################
####      KEYWORDS TABLE FUNCTIONS    ########################################
##############################################################################

def get_keyword_ledger_data():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM keywords")
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling keywords", e)
        return False
    return cur.fetchall()


