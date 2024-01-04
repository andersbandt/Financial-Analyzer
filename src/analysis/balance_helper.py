

# import user defined modules
import db.helpers as dbh
import analysis.investment_helper as invh


# import logger
from loguru import logger
from utils import logfn


def get_account_balance(account_id):
    # get account type
    acc_type = dbh.account.get_account_type(account_id)

    # if account is an investment account
    if acc_type == 4:
        bal = invh.summarize_account(account_id)
        bal_date = 0 # TODO: add current date if account is investment account
    else:
        # leverage database 'balance' helper to get most recent balance entry by DATE
        bal, bal_date = dbh.balance.get_recent_balance(account_id, add_date=True)

    return bal, bal_date


def get_account_balance_on_date(account_id, date):
    balance_data = dbh.balance.get_balance_on_date(account_id, date)
    if len(balance_data) == 0:
        return False
    else:
        return balance_data


# TODO: migrate any "manual additions" of balance adding into this function
def add_account_balance(account_id, bal_amount, bal_date):
    # do some checking on double add per date
    bal_added = get_account_balance_on_date(account_id, bal_date)
    if bal_added is not False:
        print(f"\nCan't add balance! Already have an entry for date!!:  {bal_added}")
        return

    # insert_category: inserts a category into the SQL database
    dbh.balance.insert_account_balance(account_id,
                                       bal_amount,
                                       bal_date)

    # print out balance addition confirmation
    print(f"Great, inserted a balance of {bal_amount} for account {account_id} on date {bal_date}")




# a01_show_wealth
def produce_retirement_balances():
    acc_balances = []
    acc_id_arr = dbh.account.get_retirement_accounts(1)

    for acc_id in acc_id_arr:
        bal_amount, bal_date = get_account_balance(acc_id)
        acc_balances.append(bal_amount)

    return acc_id_arr, acc_balances

