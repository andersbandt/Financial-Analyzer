"""
@file    transaction_helper.pu
@brief   module will focus on retrieving Transactions from SQL .db file

"""


# TODO: can add some functions from analyzer_helper.py into here when that gets too big


def sum_transaction_total(transactions):
    sum_t = 0
    for transaction in transactions:
        sum_t += transaction.amount
    return sum_t