
# import needed modules
import re

# import user created modules
from db import db_helper

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
    if not month_year_to_date_range(month, year):
        raise Exception("Uh oh, something went wrong getting date range for status indicators")
    else:
        date_start, date_end = month_year_to_date_range(month, year)

    account_ledger_data = db_helper.get_account_transactions_between_date(account_id, date_start, date_end, printmode)

    if printmode is not None:
        print("\nExamining account:", db_helper.get_account_name_from_id(account_id))
        print("Got this many transactions for account in date range: ", len(account_ledger_data))

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

