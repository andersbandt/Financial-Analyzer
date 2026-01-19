"""
@file    transaction_helper.py
@brief   module will focus on functions assisting Transaction objects

"""

# import user defined helper modules
import db.helpers as dbh
from analysis.data_recall import transaction_recall as transr
from statement_types import Ledger
from cli import cli_helper as clih
from categories import categories_helper as cath

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

