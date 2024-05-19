"""
@file account_helper.py
@brief helper functions for account related things


"""

# import needed modules
import numpy as np

# import user defined modules
import db.helpers as dbh
from cli import cli_printer as clip

# THIS IS THE PLACE WHERE ACCOUNT TYPES ARE HARD CODED IN
# tag:hardcode
types = [
    "Saving", # ID (1)
    "Checking",
    "Credit Card",
    "Investment" # ID (4)
]


# indexing starts at (1)
def get_acc_type_mapping(account_int):
    return types[account_int-1]

def get_acc_type_arr():
    return types


def get_num_acc_type():
    return len(types)


# TODO: add some function for account_id->name and name->account_id and refactor them into here



def print_account_status(acc_id_compare):
    all_account_id = dbh.account.get_all_account_ids()

    all_account_name = []
    status_arr = []

    for acc_id in all_account_id:
        if acc_id in acc_id_compare:
            status_arr.append(True)
        else:
            status_arr.append(False)
        all_account_name.append(dbh.account.get_account_name_from_id(acc_id))

    # print out final status list and return
    concat_table_arr = np.vstack((all_account_id, all_account_name, status_arr)).T
    clip.print_variable_table(["Account ID", "Account Name", "Status"], concat_table_arr)
    return True



