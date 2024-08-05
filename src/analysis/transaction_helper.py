"""
@file    transaction_helper.py
@brief   module will focus on functions assisting Transaction objects

"""

# import user defined helper modules
import db.helpers as dbh
from analysis.data_recall import transaction_recall
from cli import cli_helper as clih
from categories import categories_helper as cath


# import logger
from loguru import logger
from utils import logfn


# TODO: can add some functions from analyzer_helper.py into here when that gets too big


def sum_transaction_total(transactions):
    sum_t = 0
    for transaction in transactions:
        sum += transaction.amount
    return sum



# get_category_input: this function should display a transaction to the user and prompt them through categorization
#   with the end result being returning the associated category_id with the transaction in question
def get_trans_category_cli(transaction, mode=2):
    # create initial category tree and print it
    categories = cath.load_categories()
    tree = cath.create_Tree(categories)
    print(tree)
    tree_ascii = tree.get_ascii()
    print(tree_ascii)

    # print transaction and prompt
    print("\n\n")
    trans_prompt = transaction.printTransaction()

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
    transaction.printTransaction()

    # return newly associated Category ID so upper layer can properly change Transaction data
    return cat_id
