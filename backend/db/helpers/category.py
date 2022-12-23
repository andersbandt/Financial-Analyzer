import sqlite3
from db import DATABASE_DIRECTORY

def get_category_info(category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        print(category_id)
        cur.execute("SELECT * FROM category WHERE category_id=?", (category_id,))
    return cur.fetchall()


def get_category_ledger_data():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM category")
    return cur.fetchall()


def get_all_category_id():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT category_id FROM category")
    return cur.fetchall()


def get_category_names():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM category")
    return cur.fetchall()


def get_category_id_from_name(category_name):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute('SELECT category_id FROM category WHERE name=?', (category_name,))
        try:
            category_id = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
            return category_id
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)
            return None


def get_category_name_from_id(category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute('SELECT name FROM category WHERE category_id=?', (category_id,))
        try:
            category_name = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
            return category_name
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)
            return None


# insert_category: inserts a category into the SQL database
def insert_category(parent, category_name):
    print("Attempting to insert category " + str(category_name) + " with parent: " + str(parent))
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
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
            return True
        except sqlite3.Error as e:
            print("Uh oh, something went wrong with adding to category table: ", e)
            return False