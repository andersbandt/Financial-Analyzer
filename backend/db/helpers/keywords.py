import sqlite3
from db import DATABASE_DIRECTORY

def insert_keyword(keyword, category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO keywords (category_id, keyword) VALUES(?, ?)', (category_id, keyword))
    return True


def get_keyword_ledger_data():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM keywords")
    return cur.fetchall()


def get_keyword_for_category_id(category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM keywords WHERE category_id=?", [category_id])
    return cur.fetchall()

