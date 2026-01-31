"""
@file    transaction_helper.py
@brief   module will focus on functions assisting Transaction objects

"""

# import needed packages
from pprint import pprint

# import user defined helper modules
import db.helpers as dbh
from analysis.data_recall import transaction_recall as transr
from statement_types import Ledger
from cli import cli_helper as clih
from categories import categories_helper as cath
from analysis import analyzer_helper as anah

# import logger


def sum_transaction_total(transactions):
    sum_t = 0
    for transaction in transactions:
        sum_t += transaction.value
    return sum_t


# get_category_input: this function should display a transaction to the user and prompt them through categorization
#   with the end result being returning the associated category_id with the transaction in question
def get_trans_category_cli(transaction, mode=2):
    # print transaction and prompt
    print("\n\n")
    trans_prompt = transaction.print_trans(print_mode=False)

    # MODE1: descend into tree
    if mode == 1:
        cat_id = clih.category_tree_prompt(cath.load_top_level_categories(), trans_prompt)
    # MODE2: list all prompts in DB
    elif mode == 2:
        cat_id = clih.category_prompt_all(trans_prompt,
                                          False)  # second param controls if I print all the categories each transaction or not
    else:
        print("Uh oh, invalid category selection mode!")
        return None

    # do some error handling on category
    if cat_id == -1:
        print("category input (-1) return reached.")
        return -1  # NOTE: can't return 0 (or False ?) because 0 is valid category_id (NA)

    # set new Category to Transaction and print for lolz
    print(f"Setting category {cath.category_id_to_name(cat_id)} for transaction.")
    transaction.setCategory(cat_id)
    print("\nNewly categorized transaction below")
    transaction.print_trans()

    # return newly associated Category ID so upper layer can properly change Transaction data
    return cat_id


def print_transaction_list(sql_key_arr):
    transaction_arr = []
    for key in sql_key_arr:
        transaction_arr.append(transr.get_transaction(key))
    tmp_ledger = Ledger.Ledger("Transaction List")
    tmp_ledger.set_statement_data(transaction_arr)
    tmp_ledger.print_statement(include_sql_key=True)


def delete_transaction_list(sql_key_arr):
    for key in sql_key_arr:
        dbh.transactions.delete_transaction(key)


##############################################################################
####      TRANSACTION SEARCH FUNCTIONS    ####################################
##############################################################################

def search_01():
    """Search by description keyword"""
    search_str = clih.spinput("\nWhat is the keyword you want to search for in transaction description?",
                              "text")
    if search_str is False:
        print("Ok, quitting transaction search.\n")
        return False
    transactions = transr.recall_transaction_desc_keyword(search_str)
    return transactions


def search_02():
    """Search by category"""
    # determine user choice of type of category search
    cat_search_type = clih.prompt_num_options("What type of category search?",
                                              ["recursive (children)", "individual"])
    cat_search_type = 2 # tag:HARDCODE

    if cat_search_type == 1:
        search_str = clih.category_tree_prompt()
        if search_str is False or search_str == -1:
            print("Ok, quitting transaction search.\n")
            return False
        children_id = cath.get_category_children(search_str)
        transactions = transr.recall_transaction_category(search_str)
        for child_id in children_id:
            transactions.extend(transr.recall_transaction_category(child_id))
    elif cat_search_type == 2:
        search_str = clih.category_prompt_all("What is the category to search for?", False)
        if search_str is False:
            print("Ok, quitting transaction search.\n")
            return False
        transactions = transr.recall_transaction_category(search_str)
    elif cat_search_type is False:
        print("Ok, quitting transaction search.\n")
        return False
    else:
        print(f"Uh oh, bad category search type of: {cat_search_type}")
        return False
    return transactions


def search_03():
    """Search by date range"""
    start_date = clih.get_date_input("What is the start date of search range?")
    end_date = clih.get_date_input("What is the end date of search range?")
    if start_date is False or end_date is False:
        print("Ok, quitting transaction search.\n")
        return False
    transactions = transr.recall_transaction_data(start_date, end_date)
    return transactions


def search_04():
    """Search by account"""
    account_id = clih.account_prompt_all("What is the account you want to search?")
    if account_id is False:
        print("Ok, quitting transaction search.\n")
        return False
    transactions = transr.recall_transaction_account(account_id)
    return transactions


def search_05_multi_filter():
    """Multi-filter search - allows filtering by multiple criteria at once"""
    print("\n... setting up multi-filter search ...")
    print("You can apply multiple filters. Select filters one by one, then apply all at once.\n")

    # Dictionary to store active filters
    active_filters = {
        'description': None,
        'category': None,
        'date_range': None,
        'account': None,
        'amount_min': None,
        'amount_max': None
    }

    # Let user select which filters to apply
    while True:
        print("\n=== Current Active Filters ===")
        for filter_name, filter_value in active_filters.items():
            if filter_value is not None:
                print(f"  {filter_name}: {filter_value}")

        filter_options = [
            "Add DESCRIPTION filter",
            "Add CATEGORY filter",
            "Add DATE RANGE filter",
            "Add ACCOUNT filter",
            "Add AMOUNT filter (min/max)",
            "DONE - Apply filters and search"
        ]

        choice = clih.prompt_num_options("\nWhat filter would you like to add?: ", filter_options)

        if choice is False:
            print("Ok, quitting multi-filter search.\n")
            return False
        elif choice == 1:  # Description
            search_str = clih.spinput("Enter keyword to search in description", "text")
            if search_str is not False:
                active_filters['description'] = search_str
        elif choice == 2:  # Category
            category_id = clih.category_prompt_all("What is the category to filter by?", False)
            if category_id is not False:
                active_filters['category'] = category_id
        elif choice == 3:  # Date range
            start_date = clih.get_date_input("What is the start date of search range?")
            if start_date is not False:
                end_date = clih.get_date_input("What is the end date of search range?")
                if end_date is not False:
                    active_filters['date_range'] = (start_date, end_date)
        elif choice == 4:  # Account
            account_id = clih.account_prompt_all("What is the account to filter by?")
            if account_id is not False:
                active_filters['account'] = account_id
        elif choice == 5:  # Amount
            print("\nAmount filter (leave blank to skip min or max)")
            amount_min = clih.spinput("Enter minimum amount (or q to skip)", "float")
            if amount_min is not False:
                active_filters['amount_min'] = amount_min
            amount_max = clih.spinput("Enter maximum amount (or q to skip)", "float")
            if amount_max is not False:
                active_filters['amount_max'] = amount_max
        elif choice == 6:  # Done
            break

    # Check if any filters were set
    if all(v is None for v in active_filters.values()):
        print("No filters applied. Returning all transactions.")
        return transr.recall_transaction_data()

    # Start with all transactions or use date range as base
    if active_filters['date_range'] is not None:
        start_date, end_date = active_filters['date_range']
        transactions = transr.recall_transaction_data(start_date, end_date)
    else:
        transactions = transr.recall_transaction_data()

    print(f"\nStarting with {len(transactions)} transactions")

    # Apply each filter progressively
    if active_filters['description'] is not None:
        keyword = active_filters['description'].lower()
        transactions = [t for t in transactions if keyword in t.description.lower()]
        print(f"After description filter: {len(transactions)} transactions")

    if active_filters['category'] is not None:
        cat_id = active_filters['category']
        transactions = [t for t in transactions if t.category_id == cat_id]
        print(f"After category filter: {len(transactions)} transactions")

    if active_filters['account'] is not None:
        acc_id = active_filters['account']
        transactions = [t for t in transactions if t.account_id == acc_id]
        print(f"After account filter: {len(transactions)} transactions")

    if active_filters['amount_min'] is not None:
        min_val = active_filters['amount_min']
        transactions = [t for t in transactions if t.value >= min_val]
        print(f"After minimum amount filter: {len(transactions)} transactions")

    if active_filters['amount_max'] is not None:
        max_val = active_filters['amount_max']
        transactions = [t for t in transactions if t.value <= max_val]
        print(f"After maximum amount filter: {len(transactions)} transactions")

    print(f"\n=== Final result: {len(transactions)} transactions ===\n")
    return transactions


def search_trans():
    """
    Main transaction search orchestrator - allows user to select search type and returns results.
    Returns: List of Transaction objects or False if cancelled
    """
    print("... searching transactions ...")

    # get input on what type of search to do
    search_options = ["DESCRIPTION", "CATEGORY", "DATE", "ACCOUNT", "MULTI-FILTER"]
    search_type = clih.prompt_num_options("What type of search do you want to perform?: ",
                                          search_options)
    if search_type is False:
        print("Ok, quitting transaction search.\n")
        return False

    # get transaction description keyword
    if search_type == 1:
        transactions = search_01()
    elif search_type == 2:
        transactions = search_02()
    elif search_type == 3:
        transactions = search_03()
    elif search_type == 4:
        transactions = search_04()
    elif search_type == 5:
        transactions = search_05_multi_filter()
    else:
        print(f"Can't perform search with search type of: {search_type}")
        return False

    # check if search was cancelled
    if transactions is False:
        print("Search cancelled.")
        return False

    # form Ledger, print, and return executive summary
    tmp_ledger = Ledger.Ledger(f"Transactions with for search type {search_type}")
    tmp_ledger.set_statement_data(transactions)
    tmp_ledger.print_statement(include_sql_key=True)

    ledger_exec = anah.return_ledger_exec_dict(transactions)
    print("\n")
    pprint(ledger_exec)
    return transactions

