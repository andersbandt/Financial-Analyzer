"""
    @file recurring_transaction.py
    @brief SQL database helper for the 'recurring_transaction' table

    Recurring transactions are user-defined templates for money that moves the same way
    every pay period but never shows up as its own line on a bank statement -- paycheck
    deductions like health insurance, HSA/401k contributions, or tax withholding.

    Applying a preset (see TabLoadData.apply_recurring_transactions() in
    cli/tabs/a04_load_data.py) writes a normal row to `transactions` for the deduction
    itself, plus -- if `add_complementary` is set -- a second, opposite-sign row on the
    same account under `complementary_category_id`. That "grosses up" income/spending
    category reporting to reflect the true pre-deduction paycheck, while netting to zero
    against the account balance (which already reflects the net direct deposit amount).
"""

# import needed modules
import datetime
import sqlite3

# import database directory
from db import DATABASE_DIRECTORY


_COLUMNS = (
    "id", "name", "account_id", "category_id", "amount", "description",
    "add_complementary", "complementary_category_id", "active", "note",
)

_SELECT = f"SELECT {', '.join(_COLUMNS)} FROM recurring_transaction"


##############################################################################
####      DATABASE MODIFICATION FUNCTIONS    #################################
##############################################################################

def insert_recurring_transaction(name, account_id, category_id, amount, description,
                                  add_complementary=True, complementary_category_id=None,
                                  note=None):
    now = datetime.datetime.now()
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO recurring_transaction
               (name, account_id, category_id, amount, description, add_complementary,
                complementary_category_id, active, note, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)""",
            (name, account_id, category_id, amount, description, add_complementary,
             complementary_category_id, note, now, now),
        )
        return cur.lastrowid


# update_recurring_transaction: generic field update. `fields` keys must be real
# recurring_transaction columns (this module's own callers only -- not exposed to raw user input).
def update_recurring_transaction(recurring_id, **fields) -> bool:
    if not fields:
        return False
    fields["updated_at"] = datetime.datetime.now()
    set_clause = ", ".join(f"{col}=?" for col in fields)
    values = list(fields.values()) + [recurring_id]
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE recurring_transaction SET {set_clause} WHERE id=?", values)
    return True


def set_recurring_transaction_active(recurring_id, active: bool) -> bool:
    return update_recurring_transaction(recurring_id, active=active)


def delete_recurring_transaction(recurring_id) -> bool:
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM recurring_transaction WHERE id=?", (recurring_id,))
    return True


##############################################################################
####      GETTER FUNCTIONS           #########################################
##############################################################################

def get_all_recurring_transactions(active_only=False):
    query = _SELECT
    if active_only:
        query += " WHERE active=1"
    query += " ORDER BY sort_order IS NULL, sort_order, id"
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(query)
        return cur.fetchall()


def get_recurring_transaction(recurring_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(f"{_SELECT} WHERE id=?", (recurring_id,))
        return cur.fetchone()


# get_applied_dates: dates a preset has already been posted on, for the double-apply guard.
#   Applying a preset tags its transaction(s) with note 'recurring_transaction id=<recurring_id>'
#   (the complementary leg adds a ' (complementary)' suffix, still matched by the LIKE below).
#   Used by TabLoadData.apply_recurring_transactions() to warn before re-applying a preset for a
#   month it's already been posted in.
def get_applied_dates(recurring_id):
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT date FROM transactions WHERE note LIKE ? ORDER BY date",
            (f"recurring_transaction id={recurring_id}%",),
        )
        return [row[0] for row in cur.fetchall()]
