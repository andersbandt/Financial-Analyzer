
# import needed modules
import sqlite3
import datetime

# set up database path
database_path = "db/financials.db"


# init_connection: creates a sqlite3 connection object with the database path and returns it
def init_connection():
    try:
        conn = sqlite3.connect(database_path)
    except sqlite3.Error as er:
        print("Uh oh, something went wrong with connecting to sqlite database:", er)
    return conn


# close_connection: takes in an sqlite3 connection object as an argument and closes the connection
def close_connection(conn):
    try:
        conn.close()
    except sqlite3.Error as er:
        print("Uh oh, something went wrong with connecting to sqlite", er)
        return False
    return True


##############################################################################
####      LEDGER TABLE FUNCTIONS    ##########################################
##############################################################################


# insert_transaction: inserts a Transaction object into the SQL database
def insert_transaction(transaction):
    # init connection
    conn = init_connection()
    cur = conn.cursor()

    # get current datetime
    cur_datetime = datetime.datetime.now()

    # attempt to add Transaction data
    try:
        with conn:
            conn.set_trace_callback(print)
            cur.execute(
                "INSERT INTO ledger_new (trans_date, account_id, category_id, amount, description, date_added) VALUES(?, ?, ?, ?, ?)",
                (transaction.date,
                 transaction.account_id,
                 transaction.category_id,
                 transaction.amount,
                 transaction.description,
                 cur_datetime))
            conn.set_trace_callback(None)
    except sqlite3.Error as e:
        print("Uh oh, something went wrong with inserting into the ledger:", e)
        close_connection(conn)
        return False
    close_connection(conn)
    return True


# updates Transaction objects (must have sql key)
def update_transaction(transaction):
    conn = init_connection()
    cur = conn.cursor()
    # print("Updating a transaction")
    try:
        with conn:
            # conn.set_trace_callback(print)
            cur.execute("UPDATE ledger SET category_id=? WHERE key=?", (transaction.category_id, transaction.sql_key))
            # conn.set_trace_callback(None)
    except sqlite3.Error as e:
        print("Uh oh, something went wrong with updating the ledger: ", e)
        close_connection(conn)
        return False
    close_connection(conn)
    return True


# delete_transaction: deletes a Transaction
def delete_transaction(sql_key):
    conn = init_connection()
    cur = conn.cursor()
    try:
        with conn:
            cur.execute("DELETE FROM ledger WHERE key=?", (sql_key,))
    except sqlite3.Error as e:
        print("Uh oh, something went wrong deleting from ledger: ", e)
        close_connection(conn)
        return False
    close_connection(conn)
    return True


# gets ledger data for ALL the transactions in a certain date range
#   note: date must be in the format of year-month-date
def get_transactions_between_date(date_start, date_end):
    conn = init_connection()
    cur = conn.cursor()
    try:
        conn.set_trace_callback(print)
        cur.execute("SELECT * FROM ledger WHERE trans_date BETWEEN ? AND ? ORDER BY trans_date ASC",
                    (date_start, date_end))
        ledger_data = cur.fetchall()
        conn.set_trace_callback(None)
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling transaction data:", e)
        close_connection(conn)
        return None

    close_connection(conn)
    return ledger_data


# get_uncategorized_transactions:
def get_uncategorized_transactions():
    conn = init_connection()
    cur = conn.cursor()
    try:
        conn.set_trace_callback(print)
        cur.execute("SELECT * FROM ledger WHERE category_id=0")
        ledger_data = cur.fetchall()
        conn.set_trace_callback(None)
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling transaction data:", e)
        close_connection(conn)
        return None

    close_connection(conn)
    return ledger_data


# gets ledger data for a certain account's transactions in a certain date range
def get_account_transactions_between_date(account_id, date_start, date_end, printmode=None):
    conn = init_connection()
    cur = conn.cursor()
    try:
        if printmode is not None:
            if printmode == "debug":
                conn.set_trace_callback(print)
        cur.execute("SELECT * FROM ledger WHERE account_id=? AND trans_date BETWEEN ? AND ? ORDER BY trans_date ASC",
                    (account_id, date_start, date_end))
        ledger_data = cur.fetchall()
        conn.set_trace_callback(None)
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling transaction data:", e)
        close_connection(conn)
        return None

    close_connection(conn)
    return ledger_data


##############################################################################
####      CATEGORY TABLE FUNCTIONS    ########################################
##############################################################################

def get_category_info(category_id):
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM category WHERE category_id=?", [category_id])
    except sqlite3.Error as e:
        print("Uh oh, something went wrong with recalling info for category_id=", category_id)
        print("\t", e)
    return cur.fetchall()


def get_category_ledger_data():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM category")
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling accounts", e)
        return None
    return cur.fetchall()


def get_all_category_id():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT category_id FROM category")
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling category IDs", e)
        return None
    return cur.fetchall()


def get_category_names():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM category")
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling category names", e)
        return None
    return cur.fetchall()


def get_category_id_from_name(category_name):
    conn = init_connection()
    cur = conn.cursor()
    with conn:
        try:
            cur.execute('SELECT category_id FROM category WHERE name=?', (category_name,))
        except sqlite3.Error as e:
            print("Uh oh, something went wrong finding category ID from name: ", e)
        try:
            category_id = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)

    close_connection(conn)
    return category_id


def get_category_name_from_id(category_id):
    conn = init_connection()
    cur = conn.cursor()
    with conn:
        try:
            cur.execute('SELECT name FROM category WHERE category_id=?', (category_id,))
        except sqlite3.Error as e:
            print("Uh oh, something went wrong finding category name from ID: ", e)
            return False
        try:
            category_name = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)

    close_connection(conn)
    return category_name


# insert_category: inserts a category into the SQL database
def insert_category(parent, category_name):
    conn = init_connection()
    cur = conn.cursor()
    print("Attempting to insert category " + str(category_name) + " with parent: " + str(parent))
    with conn:
        # check to see if category has already been added
        cur.execute('SELECT category_id FROM category WHERE name=?', (category_name,))
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
####      BUDGET CATEGORY  FUNCTIONS    ######################################
##############################################################################

# insert_bcat: inserts information for a BudgetCategory into the SQL database
def insert_bcat(category_id, limit, cd):
    conn = init_connection()
    cur = conn.cursor()
    print("Attempting to insert a BudgetCategory " + str(category_id) + " with limit: " + str(limit))
    with conn:
        # check to see if category has already been added
        cur.execute('SELECT * FROM budget WHERE category_id=?;', category_id)
        if len(cur.fetchall()) > 0:
            print("Uh oh, the same budget for the category might already be added")
            return False

        try:
            cur.execute('INSERT INTO budget (category_id, lim, cd) \
            VALUES(?, ?, ?)', (category_id, limit, cd))
        except sqlite3.Error as e:
            print("Uh oh, something went wrong with adding to budget table: ", e)
            return False
        else:
            return True


def get_bcat_cd(category_id):
    conn = init_connection()
    cur = conn.cursor()
    with conn:
        try:
            cur.execute('SELECT cd from budget WHERE category_id=?', [category_id])
        except sqlite3.Error as e:
            print("Uh oh, something went wrong recalling cd status: ", e)
            return False
        else:
            return True


##############################################################################
####      ACCOUNT TABLE FUNCTIONS    #########################################
##############################################################################

def insert_account(account_name):
    conn = init_connection()
    cur = conn.cursor()

    with conn:
        cur.execute('SELECT account_id FROM account')
        new_account_id = cur.fetchall()[-1][0] + 1  # grab latest addition (should be highest value) and add 1
        try:
            cur.execute('INSERT INTO account (account_id, name) \
            VALUES(?, ?)', (new_account_id, account_name))
        except sqlite3.Error as e:
            print("Uh oh, something went wrong with adding to category table: ", e)
            raise Exception("Couldn't properly insert account into database")
    return new_account_id


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


# get_all_account_ids: return array of account ID's
def get_all_account_ids():
    conn = init_connection()
    cur = conn.cursor()
    try:
        # conn.set_trace_callback(print)
        cur.execute("SELECT * FROM account")
        ledger_data = cur.fetchall()
        # conn.set_trace_callback(None)
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling accounts", e)
        return False

    account_ids = []
    for item in ledger_data:
        account_ids.append(item[0])

    close_connection(conn)
    return account_ids


def get_account_names():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM account")
        account_names = [x[0] for x in cur.fetchall()]
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling account names", e)
        return False
    close_connection(conn)
    return account_names


def get_account_names_by_type(type):
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM account WHERE type=?", (type,))
        account_names = [x[0] for x in cur.fetchall()]
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling account names", e)
        return False
    close_connection(conn)
    return account_names


def get_account_ledger_data():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM account")
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling accounts", e)
        return False
    return cur.fetchall()


def get_account_type(account_id):
    conn = init_connection()
    cur = conn.cursor()
    with conn:
        try:
            cur.execute('SELECT type FROM account WHERE account_id=?', [account_id])
        except sqlite3.Error as e:
            print("Uh oh, something went wrong finding account name from ID: ", e)
            print("Can't get account type information")
            return False
        try:
            account_type = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)

    close_connection(conn)
    return account_type


##############################################################################
####      KEYWORDS TABLE FUNCTIONS    ########################################
##############################################################################

def insert_keyword(keyword, category_id):
    conn = init_connection()
    cur = conn.cursor()
    with conn:
        try:
            conn.set_trace_callback(print)
            cur.execute('INSERT INTO keywords (category_id, keyword) VALUES(?, ?)', (category_id, keyword))
            conn.set_trace_callback(None)
        except sqlite3.Error as e:
            print("Uh oh, something went wrong with adding to keyword table: ", e)
            close_connection(conn)
            return False
    close_connection(conn)
    return True


def get_keyword_ledger_data():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM keywords")
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling keywords", e)
        return False
    return cur.fetchall()


def get_keyword_for_category_id(category_id):
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM keywords WHERE category_id=?", [category_id])
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling keywords", e)
        return False
    return cur.fetchall()


##############################################################################
####      BALANCES TABLE FUNCTIONS    ########################################
##############################################################################

def insert_account_balance(account_id, amount, date):
    conn = init_connection()
    cur = conn.cursor()
    try:
        with conn:
            cur.execute("INSERT INTO balances (account_id, amount, bal_date) VALUES(?, ?, ?)",
                        (account_id, amount, date))
    except sqlite3.Error as e:
        print("Uh oh, something went inserting into balances: ", e)
        return False
    return True


# gets balance data for ALL the balances in a certain date range
#   note: date must be in the format of year-month-date
def get_balances_between_date(date_start, date_end):
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM balances WHERE bal_date BETWEEN ? AND ? ORDER BY bal_date ASC",
                    (date_start, date_end))
        balances_data = cur.fetchall()
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling balances data:", e)
        close_connection(conn)
        return None

    close_connection(conn)
    return balances_data


##############################################################################
####      INVESTMENT TABLE FUNCTIONS    ######################################
##############################################################################

# insert_investment: insert an investment into the database
def insert_investment(date, account_id, ticker, amount, inv_type):
    conn = init_connection()
    cur = conn.cursor()
    try:
        with conn:
            cur.execute(
                "INSERT INTO investment (trans_date, account_id, ticker, shares, inv_type, value, calc_type) VALUES(?, ?, ?, ?, ?, ?, ?)",
                (date, account_id, ticker, amount, inv_type, 0, 1))
    except sqlite3.Error as e:
        print("Uh oh, something went inserting into balances: ", e)
        return False
    return True


def get_inv_ledge_data():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM investment")
        ledger_data = cur.fetchall()
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling investment tickers:", e)
        close_connection(conn)
        return None

    close_connection(conn)
    return ledger_data


# get_all_ticker: gets all the tickers in the database
def get_all_ticker():
    conn = init_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT ticker FROM investment")
        tickers = cur.fetchall()
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling investment tickers:", e)
        close_connection(conn)
        return None

    close_connection(conn)
    return tickers
