# import needed modules
from datetime import *
from datetime import timedelta

# import user defined modules
import db.helpers as dbh
from account import account_helper as acch
import analysis.investment_helper as invh
from analysis import graphing_analyzer as grapa
from analysis.data_recall import transaction_recall as transr
from tools import date_helper as dateh


def get_account_balance(account_id):
    # get account type
    acc_type = dbh.account.get_account_type(account_id)

    # if account is an investment account
    if acc_type == 4:
        bal = invh.summarize_account(account_id, printmode=True)
        bal_date = dateh.get_cur_str_date()
    else:
        # leverage database 'balance' helper to get most recent balance entry by DATE
        bal, bal_date = dbh.balance.get_recent_balance(account_id, add_date=True)

    return bal, bal_date


def get_account_balance_on_date(account_id, date):
    balance_data = dbh.balance.get_balance_on_date(account_id, date)
    if len(balance_data) == 0:
        return False
    else:
        return balance_data[0][2]  # NOTE: this used to return the full `balance_data`


def add_account_balance(account_id, bal_amount, bal_date):
    # do some checking on double add per date
    bal_added = get_account_balance_on_date(account_id, bal_date)
    if bal_added is not False:
        print(f"\nCan't add balance! Already have an entry for date!!:  {bal_added}")
        return False

    # insert_category: inserts a category into the SQL database
    dbh.balance.insert_account_balance(account_id,
                                       bal_amount,
                                       bal_date)

    # print out balance addition confirmation
    print(f"Great, inserted a balance of {bal_amount} for account {account_id} on date {bal_date}")
    return True


def get_retirement_balances():
    acc_balances = []
    acc_id_arr = dbh.account.get_retirement_accounts(1)

    for acc_id in acc_id_arr:
        bal_amount, bal_date = get_account_balance(acc_id)
        acc_balances.append(bal_amount)

    return acc_id_arr, acc_balances


def model_balance(starting_balance, transactions):
    # Sort transactions by date
    transactions.sort(key=lambda x: x.date)

    # Initialize the balance array and the current balance
    balance_list = []
    current_balance = starting_balance

    # Find the start and end dates
    if transactions:
        start_date = datetime.strptime(transactions[0].date, "%Y-%m-%d")
        end_date = datetime.strptime(transactions[-1].date, "%Y-%m-%d")
    else:
        return balance_list  # No transactions, return empty list

    # Iterate over each day in the range
    current_date = start_date
    while current_date <= end_date:
        # Add balance at the start of the day
        balance_list.append((current_date, current_balance))

        # Apply transactions for the current date
        for transaction in transactions:
            if transaction.date == datetime.strftime(current_date, "%Y-%m-%d"):
                current_balance += transaction.amount

        # Move to the next day
        current_date += timedelta(days=1)

    return balance_list


def model_account_balance(account_id):
    # get starting balance
    start_date = "1999-10-02"
    end_date = dateh.get_cur_str_date()
    for date in dateh.iterate_dates(start_date, end_date):
        tmp = get_account_balance_on_date(account_id, date)
        if tmp is not False:
            start_date = date
            starting_balance = tmp
            break

    print(f"Starting balance found for account: {starting_balance}")
    # get transaction list
    balance_list = model_balance(
        starting_balance,
        transr.recall_transaction_data(start_date, account_id=account_id))
    return balance_list


# GRAPH TYPE 1: by account ID
def graph_balance_1(edge_code_date, values_array, account_names_array):
    # TODO: add sort by account size
    grapa.create_stackline_chart(edge_code_date[1:],
                                 values_array,
                                 title=f"Balances per account since {edge_code_date[0]}",
                                 label=account_names_array,
                                 y_format='currency')


# GRAPH TYPE 2: by account type
def graph_balance_2(edge_code_date, values_array, account_id_array):
    n = len(values_array[0])
    m = acch.get_num_acc_type()
    type_values_array = [[0 for _ in range(n)] for _ in range(m)]

    for j in range(0, len(account_id_array)):
        acc_type = dbh.account.get_account_type(account_id_array[j])
        # if acc_type not in [1, 2, 3, 4]:
        #     raise Exception(f"Uh oh account type is not valid for {account_id_array[j]}")
        for i in range(0, len(values_array[0])):
            type_values_array[acc_type - 1][i] += values_array[j][i]

    grapa.create_stackline_chart(edge_code_date[1:],
                                 type_values_array,
                                 title=f"Balances by account type",
                                 label=acch.get_acc_type_arr(),
                                 y_format='currency')


# GRAPH TYPE 3: day by day (to be used with `model_balance`
def graph_balance_3(dates, balances):
    grapa.create_line_chart(dates, balances, "Account Balance Over Time")
