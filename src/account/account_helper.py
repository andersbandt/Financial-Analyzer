


# import user defined modules
import db.helpers as dbh

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



