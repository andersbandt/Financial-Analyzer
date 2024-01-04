
# import needed modules
from datetime import datetime

# import user defined modules
import db.helpers as dbh
from statement_types import Transaction



# @logfn
def convert_ledge_to_transactions(ledger_data):
    # create an array of Transaction objects with the database data
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
    # TODO: delete following lines post audit. I highly doubt I am using it?
    if date_start != -1 and date_end != -1:
        print("Recalling transactions between " + date_start + " and " + date_end)
        ledger_data = dbh.ledger.get_transactions_between_date(date_start, date_end)
    else:
        print("getting ALL transactions")
        ledger_data = dbh.ledger.get_transactions_ledge_data()

    transactions = convert_ledge_to_transactions(ledger_data)

    if len(transactions) == 0:
        logger.exception(
            "Uh oh, analyzer_helper.recall_transaction_data produced no results."
        )
        raise AnalyzerHelperError(
            "Uh oh, analyzer_helper.recall_transaction_data produced no results."
        )

    return transactions


def recall_transaction_desc_keyword(desc_keyword):
    ledger_data = dbh.transactions.get_transactions_description_keyword(desc_keyword)
    transactions = convert_ledge_to_transactions(ledger_data)
    return transactions


def recall_transaction_category(category_id):
    ledger_data = dbh.transactions.get_transactions_by_category_id(category_id)
    transactions = convert_ledge_to_transactions(ledger_data)
    return transactions