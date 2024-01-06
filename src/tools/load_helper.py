"""
@file load_helper.py
@brief tool for helping load in RAW financial data from saved statements on filesystem

"""

# import needed modules
import os

# import user created modules
import db.helpers as dbh
from tools import date_helper
from statement_types import Statement
import statement_types as st

# import logger
from loguru import logger
from utils import logfn



##############################################################################
####      STATEMENT FILE FUNCTIONS    ########################################
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



# get_statement_folder: returns formatted folder of where the statement is. year and month are ints
@logfn
def get_statement_folder(base_filepath, year, month):
    # TODO: I am not sure what this is checking really?
    # if month not in range(0, 12+1):
    #     month = date_helper.month2Int(month)

    if month == 1:
        month_string = "01-January/"
    elif month == 2:
        month_string = "02-February/"
    elif month == 3:
        month_string = "03-March/"
    elif month == 4:
        month_string = "04-April/"
    elif month == 5:
        month_string = "05-May/"
    elif month == 6:
        month_string = "06-June/"
    elif month == 7:
        month_string = "07-July/"
    elif month == 8:
        month_string = "08-August/"
    elif month == 9:
        month_string = "09-September/"
    elif month == 10:
        month_string = "10-October/"
    elif month == 11:
        month_string = "11-November/"
    elif month == 12:
        month_string = "12-December/"
    else:
        print("Bad month int stored in statement: " + str(month))
        return

    statement_folder = (
        base_filepath + "/" + str(year) + "/monthly_statements/" + month_string # tag:HARDCODE
    )
    return statement_folder


# TODO: get this basefilepath out of there
@logfn
def get_year_month_files(basefilepath, year, month):
    # look in the folder to determine loaded files
    dir_path = get_statement_folder(basefilepath, year, month)
    print("Looking at path: " + dir_path)
    dir_list = os.listdir(dir_path)
    if len(dir_list) == 0:
        print("Yikes! No files found")

    # add back the search base to get full filepaths\
    for i in range(0, len(dir_list)):
        dir_list[i] = dir_path + dir_list[i]

    return dir_list

# attempts to take in a raw financial data file and return what account number it is tied to
# IDEA (captured in Obsidian as well): store what files I use and match them to accounts in order to
#   create some algorithm that predicts based on things like file name, extension, size, etc
#   to make the decision to match to account
# tag:HARDCODE for this whole function
def match_file_to_account(filepath):
    print("\t\t... Attempting to match file to account ...")


    # MARCUS
    if False:
        return 2000000007


    # WELLS CHECKING
    if "Checking1" in filepath:
        return 2000000002

    # WELLS SAVING
    if "Savings2" in filepath:
        return 2000000003

    # WELLS CREDIT
    if "CreditCard3" in filepath:
        return 2000000004

    # VENMO
    if "venmo" in filepath.lower() or 'transaction_history' in filepath.lower():
        print("contains 'venmo' or 'transaction_history'")
        return 2000000007

    # APPLE CARD
    if "apple" in filepath.lower():
        print("contains 'apple'")
        return 2000000009

    # CHASE
    if "chase" in filepath.lower():
        print("Contains 'chase'")
        return 2000000012

    # return None if we didn't match anything
    return None


# TODO: I think this should be moved to clih
def get_account_id_manual():
    accounts = dbh.account.get_account_ledger_data()

    i = 1
    for account in accounts:
        print(str(i) +": " + account[1])
        i += 1

    acc_num = int(input("\t\tPlease enter what account you want: "))
    acc = accounts[acc_num-1][0]
    return acc



##############################################################################
####      FINANCIAL CLASS FUNCTIONS    #######################################
##############################################################################

# check_transaction_load_status: checks whether or not a Transaction object is loaded up
# TODO: could improve this function potentially. Like checking the actual raw filesystem data?
def check_transaction_load_status(transaction):
    transaction_status = dbh.transactions.get_transaction(transaction)
    if transaction_status is None:
        return False
    else:
        return True


def create_master_statement(statement_list):
    cum_trans_list = []
    for statement in statement_list:
        if statement is not None:
            if statement.transactions is not None:
                cum_trans_list.extend(statement.transactions)
    statement = Statement.Statement("dummy account_id",
                                    "dummy year",
                                    "dummy month",
                                    "dummy filepath",
                                    transactions=cum_trans_list)
    return statement


def create_statement(year, month, filepath, account_id_prompt=False):
    # determine account_id
    print("\nCreating statement at: " + filepath)

    ### GRAB ACCOUNT_ID either automatic or based on filepath
    account_id = match_file_to_account(filepath)

    if account_id == None:
        if account_id_prompt:
            print("\tCouldn't automatically match account_id, manually loading in")
            account_id = get_account_id_manual()
        else:
            return None
    else:
        print("\tFound account ID: ", account_id)


    # TODO: can I figure out a way to not hard code this in?
    # tag:HARDCODE
    if account_id == 2000000001:  # Marcus
        stat = st.Marcus.Marcus(account_id, year, month, filepath)
        return stat
    elif (account_id == 2000000002) or (account_id == 2000000003) or (account_id == 2000000004):
        stat = st.csvStatement.csvStatement(account_id, year, month, filepath,
                                            0,
                                            1,
                                            4,
                                            -1) # date_col, amount_col, description_col, category_col
        return stat

    elif account_id == 2000000005:  # Vanguard Brokerage
        stat = st.VanguardBrokerage.VanguardBrokerage(account_id, year, month, filepath)
        return stat
    elif account_id == 2000000006:  # Vanguard Roth
        stat = st.VanguardRoth.VanguardRoth(account_id, year, month, filepath)
        return stat
    elif account_id == 2000000007:  # Venmo
        stat = st.Venmo.Venmo(account_id, year, month, filepath, -1, -1, -1, -1) # Venmo inherits from csvStatement
        return stat
    elif account_id == 2000000008:  # Robinhood
        stat = st.Robinhood.Robinhood(account_id, year, month, filepath)
        return stat
    elif account_id == 2000000009:  # Apple Card
        stat = st.AppleCard.AppleCard(account_id, year, month, filepath, -1, -1, -1, -1)
        return stat
    elif account_id == 2000000012:  # Chase Card
        stat = st.ChaseCard.ChaseCard(account_id, year, month, filepath)
        return stat
    # if no valid account_id was found
    else:
        raise Exception("No valid account selected in tools-load_helper-create_statement()")

        # print out user error message
        print("Error in code account binding: " + "No valid Statement Class exists for the selected account ID")

    return None


def get_month_year_statement_list(basefilepath, year, month):
    file_list = get_year_month_files(basefilepath, year, month)

    statement_list = []
    for file in file_list:
        statement_list.append(create_statement(year, month, file))

        if statement_list[-1] is not None:
            print("... statement created, going to load in data")

            try:
                statement_list[-1].load_statement_data()
            except Exception as e:
                print("Something went wrong loading statement from filepath but the show MUST GO ON!!!")
                print("\terror is: ", e)
                raise (e)
            statement_list[-1].print_statement()

    return statement_list
