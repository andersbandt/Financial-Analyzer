
# import needed modules
import sqlite3
from db import DATABASE_DIRECTORY


TABLE_NAME = "file_mapping"


def insert_account_search_str(account_id, search_str):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO {TABLE_NAME} (account_id, file_search_str) \
            VALUES(?, ?)",
            (account_id, search_str),
        )
        # get account ID that we just inserted
        cur.execute("SELECT id FROM file_mapping")
        data_id = (cur.fetchall()[-1][0])
        return data_id


# TODO: this function does not work
def get_account_id_from_string(search_str):
    print(f"... dbh.file_mapping: trying to find match with {search_str}")
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        # cur.execute(
        #     f"SELECT account_id FROM {TABLE_NAME} WHERE file_search_str LIKE ?",
        #     ('%'+search_str+'%', ),
        #             )
        # cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE file_search_str LIKE?", ["%" + search_str + "%"])
        cur.execute(f"SELECT account_id FROM {TABLE_NAME} WHERE ? LIKE '%' || file_search_str || '%'", (search_str,))
        res = cur.fetchall()
        try:
            account_id = res[0][0]
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)
            print("Can't produce account_id match from string")
            print(f"Got this for results: {res}")
            return False
    return account_id


def get_file_mapping_ledge_data():
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM {TABLE_NAME}",
        )
        ledger_data = cur.fetchall()
    return ledger_data


