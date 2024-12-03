
# import needed modules
import sqlite3

from db import DATABASE_DIRECTORY



def insert_category(category_name, parent):
    print(
        "Attempting to insert category "
        + str(category_name)
        + " with parent: "
        + str(parent)
    )

    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()

        if check_category_table_empty():
            first_category_id = 1000000001
            # insert new category
            cur.execute(
                "INSERT INTO category (category_id, parent_id, name) \
            VALUES(?, ?, ?)",
                (first_category_id, parent, category_name),
            )
            return first_category_id
        else:
            # insert new account value
            cur.execute(
                """INSERT INTO category (name, parent_id) \
                VALUES(?, ?)""",
                (category_name, parent),
            )
            # get account ID that we just inserted
            cur.execute("SELECT category_id FROM category")
            category_id = (cur.fetchall()[-1][0])
            return category_id


def get_category_info(category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
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
        cur.execute("SELECT category_id FROM category WHERE name=?", (category_name,))
        try:
            category_id = cur.fetchall()[0][
                0
            ]  # have to get the first tuple element in array of results
            return category_id
        except IndexError as e:
            print("ERROR SQL:", e)
            print("probably no results found for SQL query): ", e)
            raise(e)


def get_category_name_from_id(category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM category WHERE category_id=?", (category_id,))
        try:
            category_name = cur.fetchall()[0][
                0
            ]  # have to get the first tuple element in array of results
            return category_name
        except IndexError as e:
            print("ERROR SQL:", e)
            print("probably no results found for SQL query): ", e)
            print("Can't get category name for id: " + str(category_id))
            #         return None


def check_category_table_empty():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        # Execute the query to count entries in a table (replace 'your_table' with your table name)
        cur.execute('SELECT COUNT(*) FROM category')

    # Fetch the result
    count = cur.fetchone()[0]

    if count == 0:
        return True
    else:
        return False


def delete_category(category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()

        cur.execute("DELETE FROM category WHERE category_id=?", (category_id,))
        print(cur.fetchall())
    return True


def update_parent(category_id, new_parent_id) -> bool:
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE category SET parent_id=? WHERE category_id=?",
            (new_parent_id, category_id),
        )
    return True





