# import needed modules


import db.helpers as dbh
# import user created modules
from tools import date_helper

##############################################################################
####      VARIOUS FUNCTIONS    ###############################################
##############################################################################

# returns array of accounts with their statuses
# status
# 1 = hard yes
# 2 = maybe loaded in
# 0 = hard NO - not loaded in
#   for example: [[200000001, 1], 2000000002, 0]]
def check_account_load_status(account_id, month, year, printmode=None):
    # first check if any transaction data exists at all
    if not date_helper.month_year_to_date_range(month, year):
        raise Exception(
            "Uh oh, something went wrong getting date range for status indicators"
        )
    else:
        date_start, date_end = date_helper.month_year_to_date_range(month, year)

    account_ledger_data = dbh.ledger.get_account_transactions_between_date(
        account_id, date_start, date_end, printmode
    )

    if printmode is not None:
        print("\nExamining account:", dbh.account.get_account_name_from_id(account_id))
        print(
            "Got this many transactions for account in date range: ",
            len(account_ledger_data),
        )

        print("Transactions below: ")
        print(account_ledger_data)

    # figure out if this is a hard yes situation
    hard_yes_stat = False

    if len(account_ledger_data) == 0:
        return 0
    elif hard_yes_stat:
        return 1
    elif len(account_ledger_data) > 0:
        return 2
    else:
        return 0


def check_transaction_load_status(transaction):
    pass
