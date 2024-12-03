
# import needed modules
import sqlite3

# import database BASE directory
from db import DATABASE_DIRECTORY



def insert_keyword(keyword, category_id):
    if category_id is None:
        print("Refusing to add keyword with category None")
        return

    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO keywords (category_id, keyword) VALUES(?, ?)",
            (category_id, keyword),
        )
    return True



def get_keyword_for_category_id(category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM keywords WHERE category_id=?", [category_id])
    return cur.fetchall()


def get_category_id_for_keyword(keyword):
    print("... checking keyword: ", keyword)
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT category_id FROM keywords WHERE keyword=?", [keyword])
    return cur.fetchall()



def get_keyword_ledger_data():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM keywords")
    return cur.fetchall()


def delete_keyword(sql_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()

        cur.execute("DELETE FROM keywords WHERE id=?", (sql_id,))
        print(cur.fetchall())
    return True