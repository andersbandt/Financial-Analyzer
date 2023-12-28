

# import user defined modules
import db.helpers as dbh


# TODO: improve this function
#   1-add investment accounts
#   2-add updated date to be returned
def get_account_balance(account_id):
    # leverage database 'balance' helper to get most recent balance entry by DATE
    bal = dbh.balance.get_recent_balance(account_id)

    return bal


