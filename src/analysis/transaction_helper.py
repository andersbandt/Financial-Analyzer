


# import user defined helper modules
import db.helpers as dbh
from analysis.data_recall import transaction_recall


# import logger
from utils import logfn

# TODO: do I possibly want to merge this with `transaction_recall.py' ???

# @logfn
def get_transaction(sql_key):
    ledge_transaction = dbh.transactions.get_transaction_by_sql_key(sql_key)
    transaction = transaction_recall.convert_ledge_to_transactions(ledge_transaction)
    if len(transaction) == 1:
        # transaction[0].printTransaction(include_sql_key=True)
        return transaction[0]
    else:
        print("Can't get transaction by sql_key: more than 1 result!")
        raise Exception


def sum_transaction_total(transactions):
    sum = 0
    for transaction in transactions:
        sum += transaction.amount
    return sum