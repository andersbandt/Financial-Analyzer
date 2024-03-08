


"""
@file    transaction_recall.py
@brief   module will focus on retrieving Transactions from SQL .db file

"""


# import user defined helper modules
import db.helpers as dbh
from analysis.data_recall import transaction_recall


# import logger
from utils import logfn


# TODO: can add some functions from analyzer_helper.py into here when that gets too big

def sum_transaction_total(transactions):
    sum = 0
    for transaction in transactions:
        sum += transaction.amount
    return sum