

# import user defined modules
import db.helpers as dbh
import analysis.investment_helper as invh


# TODO: improve this function
#   2-add updated date to be returned
def get_account_balance(account_id):
    # get account type
    acc_type = dbh.account.get_account_type(account_id)

    # if account is an investment account
    if acc_type == 4:
        bal = invh.summarize_account(account_id)
        bal_date = 0
    else:
        # leverage database 'balance' helper to get most recent balance entry by DATE
        bal, bal_date = dbh.balance.get_recent_balance(account_id, add_date=True)

    return bal, bal_date


