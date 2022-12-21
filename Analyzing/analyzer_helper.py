
# import needed modules
import numpy as np
from datetime import date
import datetime

# import user defined modules
from Statement_Classes import Transaction
from Finance_GUI import gui_helper
from categories import category_helper
from Finance_GUI import gui_helper
from db import db_helper
from tools import date_helper


# sum_individual_category: returns the dollar ($) total of a certain category in a statement
# inputs: transactions- list of Transaction objects, category_id- category_id of interest
# output: dollar total
def sum_individual_category(transactions, category_id):
    total_amount = 0
    for transaction in transactions:  # for every transaction in the statement
        if transaction.category_id == category_id:
            try:
                total_amount += transaction.amount
            except TypeError as e:
                print("Uh oh, wrong type in transaction:", transaction.description)

    return total_amount


# create_category_amounts_array: returns the dollar ($) total of all categories in a statement
def create_category_amounts_array(transactions, categories):
    category_amounts = []  # form 1D array of amounts to return
    for category in categories:
        category_amounts.append(sum_individual_category(transactions, category.id))
    return categories, category_amounts


# creates a summation of the top level categories (top root categories)
#   the summation will be of all children node below the root
def create_top_category_amounts_array(transactions, categories):
    tree = category_helper.create_Tree(categories)
    top_categories = category_helper.get_top_level_category_names(categories)

    category_names = []
    print("\nGot this for length of top categories: ", len(top_categories))
    category_amounts = np.zeros(len(top_categories))

    i = 0
    for category in top_categories:
        node = tree.search_nodes(name=category)[0]
        for leaf in node:
            category_amounts[i] += sum_individual_category(transactions, category_helper.category_name_to_id(leaf.name))
        i += 1
    return top_categories, category_amounts


##############################################################################
####      DATA GETTER FUNCTIONS       ########################################
##############################################################################

# return_ledger_exec_summary: returns a dictionary containing a summary of critical information about an array of Transactions
def return_ledger_exec_dict(transactions):
    expenses = 0
    incomes = 0

    not_counted = ["BALANCE", "SHARES", "TRANSFER", "VALUE", "INTERNAL"]

    for transaction in transactions:
        trans_category = category_helper.category_id_to_name(transaction.category_id)

        if trans_category not in not_counted:
            trans_amount = transaction.getAmount()

            # if the transaction was an expense
            if trans_amount < 0:
                expenses += trans_amount
            # if the transaction was an income
            elif trans_amount > 0:
                incomes += trans_amount

    exec_summary = {"expenses": expenses,
                    "incomes": incomes}

    return exec_summary


# recall_transaction_data: loads up an array of Transaction objects based on date range and accounts
#     @param date_start - the starting date for search
#     @param date_end - the ending date for search
#     @param accounts - array of which accounts to search
def recall_transaction_data(date_start, date_end, accounts):
    ledger_data = db_helper.get_transactions_between_date(date_start, date_end)

    # create an array of Transaction objects with the database data
    transactions = []  # clear transactions
    for item in ledger_data:
        if item[2] in accounts:  # only add transactions that are in the supplied accounts list
            transactions.append(Transaction.Transaction(item[1], item[2], item[3], item[4], item[5], item[0]))

    if len(transactions) == 0:
        gui_helper.alert_user("No results found", "Uh oh, search for data produced no results", "error")
        raise Exception("Uh oh, analyzer_helper.recall_transaction_data produced no results.")
        return None

    return transactions


##############################################################################
####      DATA MANIPULATION FUNCTIONS    #####################################
##############################################################################

# gen_Bx_matrix: generate 'Bx_matrix'
#     this function split vectors of B --> N parts. Each part is called a Bx, which is a collection of balance ledger data
#     B is an array of balance data between now and a previous day
def gen_Bx_matrix(days_prev, N, printmode="None"):
    # init today date object
    today = date.today()

    # init date object 'days_prev' less
    d = datetime.timedelta(days=days_prev)  # this variable can only be named d. No exceptions. Ever.
    a = today - d  # compute the date (today - timedelta)

    # get balance data
    B = db_helper.get_balances_between_date(a, today)

    # populate arrays for displaying data. All of length N
    spl_Bx = []  # this is also the length of N

    # init date edge limits
    edge_code_date = date_helper.get_edge_code_dates(today, days_prev, N)

    # init A vector
    a_A = {}
    for account_id in db_helper.get_all_account_ids():
        a_A[account_id] = 0

    # search through edge code limits to add first (N-1) bin A vectors
    for i in range(0, N-1):
        # add T/F checker for if value has been updated
        bal_added = {}
        for account_id in db_helper.get_all_account_ids():
            bal_added[account_id] = False

        # iterate through all balances data
        # TODO: could figure out a way to optimize this binning of balance data into date bins
        #     current method of deleting doesn't seem optimal (searches past edge code do nothing)
        for bx in B:
            # bx outline
            # bx[0] = sql key
            # bx[1] = account_id
            # bx[2] = total
            # bx[3] = bal_date

            # grab date of balance 'bx' item and error handle
            try:
                bx_datetime = datetime.datetime.strptime(bx[3], "%Y-%m-%d")
                bx_date = bx_datetime.date()
            except ValueError as e:
                print("Error converting string to datetime object: ", bx[3])
                print(e)
                raise Exception("Can't proceed with populating Bx A vector")

            # if date is less than edge code (in the date bin)
            if bx_date < edge_code_date[i]:
                B.remove(bx)  # remove so it doesn't appear in next searches
                # NOTE: took out below code so the current code is just adding latest ones
                # if the balance is higher than what we currently have than replace Bx in spl_Bx
                #    in this way we get the 'dominant' vector (high value)
                #if bx[2] > a_A[bx[1]]:
                #    a_A[bx[1]] = bx[2]

        # set Bx to dominant A vector after search is complete
        if printmode == "debug":
            print("Dominant A vector appears to be")
            print(a_A)
        # append vector to spl_Bx after search for 'dominant' vector is complete
        spl_Bx.append(a_A)

    # go through last bin (past final edge code)
    for bx in B:  # iterate through all balances data - probably not the most efficient?
        # if the balance is higher than what we currently have than replace Bx in spl_Bx
        if bx[2] > a_A[bx[1]]:
            a_A[bx[1]] = bx[2]
    spl_Bx.append(a_A)

    return spl_Bx


def gen_bin_A_matrix(spl_Bx, *args):
    # set which type number corresponds to which type of account
    inv_acc = [3]
    liquid_acc = [0, 1, 2, 4]

    # create containers for final totals
    investment = []
    liquid = []

    acc_cont = {}

    for i in range(0, len(args)):
        acc_cont[i] = 0

    # iterate through our collection of subset Bx balances
    for Bx in spl_Bx:
        invest_total = 0
        liquid_total = 0
        for account_id in db_helper.get_all_account_ids():
            acc_type = get_account_type(account_id)

            i = 0
            for acc_type_bin in args:
                if acc_type in acc_type_bin:
                    acc_cont[i] += Bx[account_id]

            if acc_type in inv_acc:
                invest_total += Bx[account_id]

            if acc_type in liquid_acc:
                liquid_total += (Bx[account_id])

        # cont = []
        # for i in range(0, len(args)):
        #     cont[i] = []
        #
        # for i in range(0, len(args)):
        #     cont[i].append(acc_cont[i])

        investment.append(invest_total)
        liquid.append(liquid_total)

    return [investment, liquid]


##############################################################################
####      GENERAL HELPER FUNCTIONS       #####################################
##############################################################################




##############################################################################
####      ACCOUNT INFO FUNCTIONS    ##########################################
##############################################################################


def get_account_type(account_id):
    acc_type = db_helper.get_account_type(account_id)
    return acc_type



##############################################################################
####      BUDGET ANALYSIS FUNCTIONS    #######################################
##############################################################################

def compare_trans_vs_budget(transactions, budget_filename):
    pass





