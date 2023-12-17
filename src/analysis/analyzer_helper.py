

# import needed modules
from datetime import datetime
import numpy as np


# import user defined modules
import db.helpers as dbh
from categories import categories_helper as cath
from statement_types import Transaction
from tools import date_helper

# import logger
from loguru import logger
from utils import logfn


@logfn
class AnalyzerHelperError(Exception):
    """Analyzer Helper Error"""
    def __init__(self, origin="AnalyzerHelper", msg="Error encountered"):
        self.msg = f"{origin} error encountered: {msg}"
        return self.msg

    def __str__(self):
        return self.msg



##############################################################################
####      DATA ANALYSIS FUNCTIONS       ######################################
##############################################################################


# @param   N is the number of bins to form across dates
def sum_date_binned_transaction(accounts, days_prev, N):
    # create the DATETIME objects from the previous days in N groups
    edge_code_date = date_helper.get_edge_code_dates(
        datetime.today(),
        days_prev,
        N) # have to add +2 here because we want N to be the number of bins not indices

    print("Got this for transactions edge codes")
    for edge in edge_code_date:
        print(edge)

    date_binned_transactions = []

    for i in range(0, N):
        cur_trans = recall_transaction_data(edge_code_date[i], edge_code_date[i+1], accounts=accounts)
        date_binned_transactions.append(cur_trans)

    return date_binned_transactions, edge_code_date


# sum_individual_category: returns the dollar ($) total of a certain category in a statement
# inputs: transactions- list of Transaction objects, category_id- category_id of interest
# output: dollar total
# @logfn
def sum_individual_category(transactions, category_id):
    total_amount = 0
    for transaction in transactions:  # for every transaction in the statement
        if transaction.category_id == category_id:
            try:
                total_amount += transaction.amount
            except TypeError as e:
                error = f"Uh oh, wrong type in transaction: {transaction.description}"
                logger.exception(error)
    return total_amount


# create_category_amounts_array: returns the dollar ($) total of all categories in a statement
# @logfn
def create_category_amounts_array(transactions, categories):
    category_amounts = []  # form 1D array of amounts to return
    for category in categories:
        category_amounts.append(sum_individual_category(transactions, category.id))
    return categories, category_amounts


# creates a summation of the top level categories (top root categories)
#   the summation will be of all children node below the root
# TODO: add NA (cat ID of 0) as an option to add to the array
# @logfn
def create_top_category_amounts_array(transactions, categories, count_NA=True):
    tree = cath.create_Tree(categories, cat_type="id")
    top_cat_id = cath.get_top_level_categories(cat_type="id")
    top_cat_str = cath.get_top_level_categories(cat_type="name")

    category_amounts = []
    for i in range(0, len(top_cat_id)):
        category_amounts.append(0)
        # node = tree.search_nodes(name=category)[0]
        node = tree.search_nodes(name=top_cat_id[i])[0]
        # for node in tree.search_nodes(name=category)
        #     for descendant in node.traverse():
        #         print(descendant.name)
        # print("Checking node\n")
        # print(node)
        # print("\n\n")
        for leaf in node:
            category_amounts[i] += sum_individual_category(
                transactions, leaf.name
            )
        i += 1

    if count_NA:
        top_cat_str.append("NA (uncategorized)")
        category_amounts.append(
            sum_individual_category(transactions, 0)
        )

    return top_cat_str, category_amounts


##############################################################################
####      DATA GETTER FUNCTIONS       ########################################
##############################################################################

# return_ledger_exec_summary: returns a dictionary containing a summary of critical information about an array of Transactions
# @logfn
def return_ledger_exec_dict(transactions):
    expenses = 0
    incomes = 0

    not_counted = ["BALANCE", "SHARES", "TRANSFER", "VALUE", "INTERNAL"]

    for transaction in transactions:
        trans_category = cath.category_id_to_name(transaction.category_id)

        if trans_category not in not_counted:
            trans_amount = transaction.getAmount()

            # if the transaction was an expense
            if trans_amount < 0:
                expenses += trans_amount
            # if the transaction was an income
            elif trans_amount > 0:
                incomes += trans_amount

    exec_summary = {"expenses": expenses, "incomes": incomes}

    return exec_summary


# recall_transaction_data: loads up an array of Transaction objects based on date range and accounts
#     @param date_start - the starting date for search
#     @param date_end - the ending date for search
#     @param accounts - array of which accounts to search
# @logfn
def recall_transaction_data(date_start=-1, date_end=-1, accounts=None):
    if date_start != -1 and date_end != -1:
        print("Recalling transactions between " + date_start + " and " + date_end)
        ledger_data = dbh.ledger.get_transactions_between_date(date_start, date_end)
    else:
        print("getting ALL transactions")
        ledger_data = dbh.ledger.get_transactions_ledge_data()

    # create an array of Transaction objects with the database data
    transactions = []  # clear transactions
    for item in ledger_data:
        if accounts is not None: # only add transactions that are in the supplied accounts list
            if item[2] in accounts:
                add_flag = 1
        else:
            add_flag = 1

        if add_flag:
            transactions.append(
                Transaction.Transaction(
                    item[1], # date
                    item[2], # account ID
                    item[3], # category ID
                    item[4], # amount
                    item[5], # description
                    note=item[7], # note
                    sql_key=item[0] # SQL key
                )
            )

    if len(transactions) == 0:
        logger.exception(
            "Uh oh, analyzer_helper.recall_transaction_data produced no results."
        )
        raise AnalyzerHelperError(
            "Uh oh, analyzer_helper.recall_transaction_data produced no results."
        )

    return transactions


##############################################################################
####      DATA MANIPULATION FUNCTIONS    #####################################
##############################################################################

# gen_Bx_matrix: generate 'Bx_matrix'
#     this function split vectors of B --> N parts. Each part is called a Bx, which is a collection of balance ledger data
#     B is an array of balance data between now and a previous day
# @logfn
def gen_Bx_matrix(days_prev, N, printmode="None"):
    # init today date object
    today = date.today()

    # init date object 'days_prev' less
    d = datetime.timedelta(
        days=days_prev
    )  # this variable can only be named d. No exceptions. Ever.
    a = today - d  # compute the date (today - timedelta)

    # get balance data
    B = dbh.balances.get_balances_between_date(a, today)

    # populate arrays for displaying data. All of length N
    spl_Bx = []  # this is also the length of N

    # init date edge limits
    edge_code_date = date_helper.get_edge_code_dates(today, days_prev, N)

    # init A vector
    a_A = {}
    for account_id in dbh.account.get_all_account_ids():
        a_A[account_id] = 0

    # search through edge code limits to add first (N-1) bin A vectors
    for i in range(0, N - 1):
        # add T/F checker for if value has been updated
        bal_added = {}
        for account_id in dbh.account.get_all_account_ids():
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
                logger.exception(
                    f"Error converting string to datetime object: {bx[3]} with exception details {e}"
                )
                raise AnalyzerHelperError("Can't proceed with populating Bx A vector")

            # if date is less than edge code (in the date bin)
            if bx_date < edge_code_date[i]:
                B.remove(bx)  # remove so it doesn't appear in next searches
                # NOTE: took out below code so the current code is just adding latest ones
                # if the balance is higher than what we currently have than replace Bx in spl_Bx
                #    in this way we get the 'dominant' vector (high value)
                # if bx[2] > a_A[bx[1]]:
                #    a_A[bx[1]] = bx[2]

        # set Bx to dominant A vector after search is complete
        logger.debug("Dominant A vector appears to be {a_A}")
        # append vector to spl_Bx after search for 'dominant' vector is complete
        spl_Bx.append(a_A)

    # go through last bin (past final edge code)
    for bx in B:  # iterate through all balances data - probably not the most efficient?
        # if the balance is higher than what we currently have than replace Bx in spl_Bx
        if bx[2] > a_A[bx[1]]:
            a_A[bx[1]] = bx[2]
    spl_Bx.append(a_A)

    return spl_Bx


@logfn
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
        for account_id in dbh.account.get_all_account_ids():
            acc_type = dbh.account.get_account_type(account_id)

            i = 0
            for acc_type_bin in args:
                if acc_type in acc_type_bin:
                    acc_cont[i] += Bx[account_id]

            if acc_type in inv_acc:
                invest_total += Bx[account_id]

            if acc_type in liquid_acc:
                liquid_total += Bx[account_id]

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
####      BUDGET ANALYSIS FUNCTIONS    #######################################
##############################################################################


@logfn
def compare_trans_vs_budget(transactions, budget_filename):
    pass
