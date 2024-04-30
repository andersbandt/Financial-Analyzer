"""
@file    transaction_recall.py
@brief   module will focus on retrieving Transactions from SQL .db file

"""


# import user defined modules
import db.helpers as dbh
from statement_types import Transaction
from tools import date_helper as dateh

# import logger
from loguru import logger
from utils import logfn




# import logger
from loguru import logger
from utils import logfn


@logfn
class TransactionRecallError(Exception):
    """Transaction Recall Error"""
    def __init__(self, origin="TransactionRecall", msg="Error encountered"):
        self.msg = f"{origin} error encountered: {msg}"
        # return self.msg

    def __str__(self):
        return self.msg


# @logfn
def get_transaction(sql_key):
    ledge_transaction = dbh.transactions.get_transaction_by_sql_key(sql_key)
    transaction = convert_ledge_to_transactions(ledge_transaction)
    if len(transaction) == 1:
        # transaction[0].printTransaction(include_sql_key=True)
        return transaction[0]
    else:
        print("Can't get transaction by sql_key: more than 1 result!")
        raise Exception

# convert_ledge_to_transactions: converts raw SQL ledger data into Transaction objects
# @logfn
def convert_ledge_to_transactions(ledger_data):
    transactions = []  # clear transactions
    for item in ledger_data:
        transactions.append(
            Transaction.Transaction(
                item[1], # date
                item[2], # account ID
                item[3], # category ID
                item[4], # amount
                item[5], # description
                note=item[7], # note
                sql_key=item[0] # SQL key
            )
        )
    return transactions


##############################################################################
####      "SIMPLER" RECALL FUNCTIONS    ######################################
##############################################################################

# recall_transaction_data: loads up an array of Transaction objects based on date range and accounts
#     @param date_start - the starting date for search
#     @param date_end - the ending date for search
# @logfn
def recall_transaction_data(date_start=-1, date_end=-1):
    if date_start != -1 and date_end != -1:
        print("Recalling transactions between " + date_start + " and " + date_end)
        ledger_data = dbh.ledger.get_transactions_between_date(date_start, date_end)
    else:
        print("getting ALL transactions")
        ledger_data = dbh.ledger.get_transactions_ledge_data()

    transactions = convert_ledge_to_transactions(ledger_data)

    if len(transactions) == 0:
        logger.exception(
            "Uh oh, transaction_recall produced no results."
        )
        raise TransactionRecallError(
            "Uh oh, transaction_recall produced no results."
        )
    return transactions


def recall_transaction_month_bin(year, month):
    month_range = dateh.month_year_to_date_range(
        year,
        month
    )
    month_trans = recall_transaction_data(
        month_range[0],
        month_range[1],
    )
    return month_trans


def recall_transaction_desc_keyword(desc_keyword):
    ledger_data = dbh.transactions.get_transactions_description_keyword(desc_keyword)
    transactions = convert_ledge_to_transactions(ledger_data)
    return transactions


def recall_transaction_category(category_id):
    ledger_data = dbh.transactions.get_transactions_by_category_id(category_id)
    transactions = convert_ledge_to_transactions(ledger_data)
    return transactions
