import sqlite3

from db import DATABASE_DIRECTORY


# insert_bcat: inserts information for a BudgetCategory into the SQL database
def insert_bcat(category_id, amount, applies_to_children):
    print(
        "Attempting to insert a BudgetCategory "
        + str(category_id)
        + " with limit (amount): "
        + str(amount)
    )
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        # check to see if category has already been added
        cur.execute("SELECT * FROM budget WHERE category_id=?;", category_id)
        if len(cur.fetchall()) > 0:
            print("Uh oh, the same budget for the category might already be added")
            return False

        cur.execute(
            """INSERT INTO budget (category_id, amount, applies_to_children) 
            VALUES(?, ?, ?)""",
            (category_id, amount, applies_to_children),
        )

    return True


def get_bcat_cd(category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT cd from budget WHERE category_id=?", [category_id])
    return True
