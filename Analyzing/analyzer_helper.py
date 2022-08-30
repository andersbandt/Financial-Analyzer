import sqlite3

from Statement_Classes import Transaction
from categories import category_helper
from Finance_GUI import gui_helper


# sum_individual_category: returns the dollar ($) total of a certain category in a statement
# output: dollar total
def sum_individual_category(transactions, category):
    total_amount = 0
    for transaction in transactions:  # for every transaction in the statement
        if transaction.category_id == category.category_id:
            try:
                total_amount += transaction.amount
            except TypeError as e:
                print("Uh oh, wrong type in transaction:", transaction.description)

    return total_amount


# create_category_amounts_array: returns the dollar ($) total of all categories in a statement
# output: 1D array of category strings
# output: 1D array of amounts
def create_category_amounts_array(transactions, categories):
    category_names = []
    category_amounts = []  # form 1D array of amounts to return
    for category in categories:
        category_amounts.append(sum_individual_category(transactions, category))
        category_names.append(category.name)
        #print("Got this amount for category " + category.name + " " + str(category_amounts[-1]))

    return category_names, category_amounts


# return_transaction_exec_summary: returns a dictionary containing a summary of critical information about an array of transactions
def return_transaction_exec_summary(transactions):
    expenses = 0
    incomes = 0

    not_counted = ["BALANCE", "SHARES", "TRANSFER", "VALUE", "INTERNAL"]

    for transaction in transactions:
        trans_category = category_helper.category_id_to_name(transaction.category_id)

        if trans_category not in not_counted:
            trans_amount = transaction.getAmount()

            # if the transaction was an expense
            if trans_amount < 0:
                expenses += trans_amount
            # if the transaction was an income
            elif trans_amount > 0:
                incomes += trans_amount

    exec_summary = {"expenses": expenses,
                    "incomes": incomes}

    return exec_summary


# recall_data: loads GUI elements for analyzing a selection of transaction data
def recall_transaction_data(conn, datetime_start, datetime_end, accounts):
    cur = conn.cursor()
    try:
        conn.set_trace_callback(print)
        cur.execute("SELECT * FROM ledger WHERE trans_date BETWEEN ? AND ? ORDER BY trans_date ASC", (datetime_start, datetime_end))
        ledger_data = cur.fetchall()
        conn.set_trace_callback(None)
    except sqlite3.Error as e:
        print("Uh oh, something went wrong recalling transaction data:", e)
        return False

    print(ledger_data)

    # create an array of Transaction objects with the database data
    transactions = []  # clear transactions
    for item in ledger_data:
        if item[2] in accounts:  # only add transactions that are in the supplied accounts list
            transactions.append(Transaction.Transaction(item[1], item[2], item[3], item[4], item[5], item[0]))

    if len(transactions) == 0:
        gui_helper.alert_user("No results found", "Uh oh, search for data produced no results", "error")
        raise Exception("Uh oh, analyzer_helper.recall_transaction_data produced no results.")
        return None

    return transactions







