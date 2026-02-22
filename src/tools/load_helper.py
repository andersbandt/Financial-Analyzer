"""
@file load_helper.py
@brief tool for helping load in RAW financial data from saved statements on filesystem

"""

# import needed modules
import os
import numpy as np

# import user created modules
import db.helpers as dbh
from tools import date_helper
from account import account_helper as acch
from statement_types import Statement
import statement_types as st
from cli import cli_printer as clip
from cli import cli_helper as clih


# import logger
from loguru import logger


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
        raise Exception("Uh oh, something went wrong getting date range for status indicators")
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
def get_statement_folder(base_filepath, year, month):
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
            base_filepath + "/" + str(year) + "/monthly_statements/" + month_string  # tag:HARDCODE
    )
    return statement_folder


# get_year_month_files: simply takes in a base path, year, and month and returns a list of all the files
def get_year_month_files(base_filepath, year, month):
    # look in the folder to determine loaded files
    dir_path = get_statement_folder(base_filepath, year, month)
    print(f"Looking at path: {dir_path} for statement files")
    dir_list = os.listdir(dir_path)

    # handle empty directory case
    if len(dir_list) == 0:
        print("Yikes! No files found")

    # add back the search base to get full filepaths
    for i in range(0, len(dir_list)):
        dir_list[i] = dir_path + dir_list[i]

    return dir_list


# match_file_to_account: takes in a filepath and returns account_id
def match_file_to_account(filepath):
    account_id = dbh.file_mapping.get_account_id_from_string(filepath)

    # return None if we didn't match anything
    if account_id is False:
        return None
    else:
        return account_id


##############################################################################
####      FINANCIAL CLASS FUNCTIONS    #######################################
##############################################################################

# check_transaction_load_status: checks whether or not a Transaction object is loaded up
def check_transaction_load_status(transaction):
    # call function to get transaction in .db file based matching [date, account_id, amount, description]
    transaction_status = dbh.transactions.get_transaction(transaction)
    if transaction_status is None:
        return False
    else:
        return True


# join_statement: takes in a Statement list and outputs
def join_statement(statement_list):
    # create list of all Transaction from each Statement
    cum_trans_list = []
    for statement in statement_list:
        if (statement is not None) and (statement is not False):
            cum_trans_list.extend(statement.transactions)

    # create "dummy" statement with manually added transaction list
    statement = Statement.Statement("dummy account_id",
                                    "dummy year",
                                    "dummy month",
                                    "dummy filepath",
                                    transactions=cum_trans_list)
    return statement


def create_statement(year, month, filepath, account_id_prompt=False):
    # Defined inside the function to avoid circular import:
    # Statement.py imports load_helper, so module-level st.X references would
    # be evaluated while statement_types is still being initialized.
    statement_class_registry = {
        "csvStatement":      st.csvStatement.csvStatement,
        "Marcus":            st.Marcus.Marcus,
        "VanguardBrokerage": st.VanguardBrokerage.VanguardBrokerage,
        "VanguardRoth":      st.VanguardRoth.VanguardRoth,
        "Venmo":             st.Venmo.Venmo,
        "Robinhood":         st.Robinhood.Robinhood,
        "CitiMastercard":    st.CitiMasterCard.CitiMastercard,
    }
    csv_kwarg_classes = {"csvStatement", "Venmo"}

    logger.debug("\nCreating statement at: " + filepath)

    account_id = match_file_to_account(filepath)

    if account_id is None:
        if account_id_prompt:
            account_id = clih.get_account_id_manual()
        else:
            return None

    config = dbh.statement_parser.get_parser_config(account_id)

    if config is None:
        print("\n\n#################### CRITICAL PROGRAM SOURCE ERROR   ###################################")
        print("No valid account selected in tools-load_helper-create_statement()")
        print(f"No statement_parser entry found for account_id: {account_id}")
        print("Add a row to the statement_parser table for this account.")
        raise Exception()

    class_name = config["class_name"]
    cls = statement_class_registry.get(class_name)

    if cls is None:
        print("\n\n#################### CRITICAL PROGRAM SOURCE ERROR   ###################################")
        print("No valid account selected in tools-load_helper-create_statement()")
        print(f"Unknown class_name '{class_name}' in statement_parser for account_id: {account_id}")
        print("Add the class to statement_class_registry in src/tools/load_helper.py.")
        raise Exception()

    if class_name in csv_kwarg_classes:
        stat = cls(account_id, year, month, filepath,
                   config["date_col"],
                   config["amount_col"],
                   config["description_col"],
                   config["category_col"],
                   exclude_header=bool(config["exclude_header"]),
                   inverse_amount=bool(config["inverse_amount"]))
    elif class_name == "CitiMastercard":
        stat = cls(account_id, year, month, filepath,
                   config["date_col"],
                   config["amount_col"],   # debit_col
                   config["credit_col"],
                   config["description_col"],
                   config["category_col"],
                   exclude_header=bool(config["exclude_header"]))
    else:
        # PDF-based or fully self-contained parsers
        stat = cls(account_id, year, month, filepath)

    return stat


# get_month_year_statement_list:
#   @brief      MAIN FUNCTION THAT IS DOING THE SHIT WHEN LOADING !!!!
def get_month_year_statement_list(basefilepath, year, month, printmode=False):
    file_list = get_year_month_files(basefilepath, year, month)

    statement_list = []
    status_list = []
    account_list = []
    for file in file_list:
        statement = create_statement(year, month, file, account_id_prompt=False)
        if statement is not None:  # NOTE: added this check to prevent returned statement list from having None in there
            statement_list.append(statement)
            status_list.append(True)
            account_list.append(statement_list[-1].account_id)

            try:
                statement.load_statement_data()
                if printmode:
                    statement.print_statement()
            except Exception as e:
                print("Something went wrong loading statement from filepath!!!\n\terror is: ", e)
                raise e

        else:
            print(f"... seems like no statement could be created for {file}")
            status_list.append(False)
            account_list.append(None)

    # print out STATUS per FILE
    concat_table_arr = np.vstack((status_list, account_list, file_list)).T
    concat_table_arr = concat_table_arr.tolist()
    clip.print_variable_table(["Status", "Account", "Filepath"], concat_table_arr)

    # print out STATUS per ACCOUNT
    account_id = acch.get_all_acc_id()
    status_list = [acc_id in account_list for acc_id in account_id]

    concat_table_arr = np.vstack(
        ([acch.account_id_to_name(acc_id) for acc_id in account_id],
         status_list)
    ).T
    concat_table_arr = concat_table_arr.tolist()
    clip.print_variable_table(["Account", "Status"], concat_table_arr)

    return statement_list

