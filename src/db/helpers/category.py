
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
            category_name = cur.fetchall()[0][0]  # have to get the first tuple element in array of results
            return category_name
        except IndexError as e:
            print("ERROR SQL:", e)
            print(f"Can't get category name for id: {category_id}")
            return None


def get_category_parent_id(category_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT parent_id FROM category WHERE category_id=?", (category_id,))
        try:
            category_parent_id = cur.fetchall()[0][
                0
            ]  # have to get the first tuple element in array of results
            return category_parent_id
        except IndexError as e:
            print("ERROR SQL:", e)
            print("probably no results found for SQL query): ", e)
            print("Can't get category parent_id for id: " + str(category_id))
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


def update_category_name(category_id, new_name: str) -> bool:
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE category SET name=? WHERE category_id=?",
            (new_name, category_id),
        )
    return True


def merge_categories(source_id, target_id, tag_note=True) -> dict:
    """Move all transactions, keywords, and child categories from source to target, then delete source.
    If tag_note (default), each reassigned transaction's note gets a short audit tag appended
    (e.g. "category_merge: EYECARE -> VISION"), preserving whatever note was already there --
    same append-don't-clobber convention as the ml_classified/recurring_transaction/BACKFILL note tags
    elsewhere in this app -- so the merge is traceable later without a separate audit table.
    Returns a dict with counts of affected rows."""
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()

        if tag_note:
            cur.execute("SELECT name FROM category WHERE category_id=?", (source_id,))
            row = cur.fetchone()
            source_name = row[0] if row else str(source_id)
            cur.execute("SELECT name FROM category WHERE category_id=?", (target_id,))
            row = cur.fetchone()
            target_name = row[0] if row else str(target_id)
            tag = f"category_merge: {source_name} -> {target_name}"

            cur.execute("SELECT id, note FROM transactions WHERE category_id=?", (source_id,))
            affected = cur.fetchall()
            for sql_key, note in affected:
                new_note = f"{note}; {tag}" if note else tag
                cur.execute("UPDATE transactions SET category_id=?, note=? WHERE id=?",
                            (target_id, new_note, sql_key))
            txn_count = len(affected)
        else:
            cur.execute("UPDATE transactions SET category_id=? WHERE category_id=?", (target_id, source_id))
            txn_count = cur.rowcount

        cur.execute("UPDATE keywords SET category_id=? WHERE category_id=?", (target_id, source_id))
        kw_count = cur.rowcount

        cur.execute("UPDATE category SET parent_id=? WHERE parent_id=?", (target_id, source_id))
        child_count = cur.rowcount

        cur.execute("DELETE FROM category WHERE category_id=?", (source_id,))

    return {"transactions": txn_count, "keywords": kw_count, "children": child_count}


def safe_delete_category(category_id, reassign_to=0, tag_note=True) -> dict:
    """Deletes a category without the silent data-loss the plain DELETE has (see
    categories_helper.create_Tree(): a child whose parent was deleted never attaches to any
    tree node again, so its transactions vanish from every report with no error). Instead:
      1. Transactions in this category -> reassigned to `reassign_to` (default 0 = NA), each with
         a short audit note tag appended (e.g. "category_delete: HOBBIES -> NA"), same
         append-don't-clobber convention as merge_categories.
      2. Child categories -> reparented to THIS category's own parent, so a subtree survives
         (just promoted up one level) instead of being silently orphaned.
      3. Keywords tied to this category -> deleted (pointless once the category is gone).
      4. The category row itself -> deleted.
    Returns a dict with counts plus `affected_sql_keys` (the transactions moved to `reassign_to`),
    so the caller can offer manual re-categorization on exactly those rows."""
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()

        cur.execute("SELECT parent_id, name FROM category WHERE category_id=?", (category_id,))
        row = cur.fetchone()
        own_parent_id, category_name = (row[0], row[1]) if row else (1, str(category_id))

        cur.execute("SELECT id, note FROM transactions WHERE category_id=?", (category_id,))
        affected = cur.fetchall()
        affected_sql_keys = [sql_key for sql_key, _ in affected]

        if tag_note:
            tag = f"category_delete: {category_name} -> NA" if reassign_to == 0 \
                else f"category_delete: {category_name} -> {reassign_to}"
            for sql_key, note in affected:
                new_note = f"{note}; {tag}" if note else tag
                cur.execute("UPDATE transactions SET category_id=?, note=? WHERE id=?",
                            (reassign_to, new_note, sql_key))
        else:
            cur.execute("UPDATE transactions SET category_id=? WHERE category_id=?",
                        (reassign_to, category_id))
        txn_count = len(affected)

        cur.execute("UPDATE category SET parent_id=? WHERE parent_id=?", (own_parent_id, category_id))
        children_reparented = cur.rowcount

        cur.execute("DELETE FROM keywords WHERE category_id=?", (category_id,))
        keywords_deleted = cur.rowcount

        cur.execute("DELETE FROM category WHERE category_id=?", (category_id,))

    return {
        "transactions": txn_count,
        "affected_sql_keys": affected_sql_keys,
        "children_reparented": children_reparented,
        "keywords_deleted": keywords_deleted,
    }





