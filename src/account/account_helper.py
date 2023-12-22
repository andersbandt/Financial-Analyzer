


# import user defined modules
import db.helpers as dbh

types = [
    "Saving", # ID (1)
    "Checking",
    "Credit Card",
    "Investment" # ID (4)
]


# THIS IS THE PLACE WHERE ACCOUNT TYPES ARE HARD CODED IN
# indexing starts at (1)
def get_acc_type_mapping(account_int):
    return types[account_int-1]


def get_num_acc_type():
    return len(types)


def get_all_account_ids():
    account_id_ledge_data = dbh.account.get_all_account_ids()

    account_ids = []
    for item in account_id_ledge_data:
        account_ids.append(item[0])

    return account_ids


