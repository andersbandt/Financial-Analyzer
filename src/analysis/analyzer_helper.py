

# import needed modules
from datetime import datetime
from pprint import pprint

# import user defined modules
import db.helpers as dbh
from categories import categories_helper as cath
import analysis.transaction_helper as transh
import analysis.data_recall.transaction_recall as transaction_recall
import tools.date_helper as dateh

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

    exec_summary = {"expenses": expenses,
                    "incomes": incomes}

    return exec_summary


# month_bin_transaction_total: takes in a list of transactions and counts total for each month
@logfn
def month_bin_transaction_total(transactions, months_prev):
    # get current month
    [cur_year, cur_month, cur_day] = dateh.get_date_int_array()

    # iterate through previous months
    if cur_month - months_prev < 1:
        start_year = cur_year - int(months_prev/12)
        if months_prev % 12 > 0:
            start_year = cur_year - (months_prev % 12) # TODO: finish this calculation of year change <--- what did I mean by this?
        start_month = cur_month - months_prev + 12
    else:
        start_year = cur_year

    end_month = cur_month + 12*int(months_prev / 12)
    logger.debug(f"\nStarting month bin of transaction from {start_month} to {end_month}")
    logger.debug(f"\tyear to begin at is {start_year}")
    month_totals = []
    for month in range(start_month, end_month + 1):
        if month > 12:
            date_range = dateh.month_year_to_date_range(start_year + int((months_prev+month)/12) - 1,
                                                        month % 12)
        else:
            date_range = dateh.month_year_to_date_range(start_year,
                                                        month)

        # filter transactions by range and sum and add to running array total
        month_transactions = filter_transactions_date(transactions, date_range[0], date_range[1])
        month_totals.append(
            transh.sum_transaction_total(month_transactions)
        )
    return month_totals


# sum_individual_category: returns the dollar ($) total of a certain category in an array of transactions
#   @param   transactions    list of Transaction objects, category_id- category_id of interest
#   @return  total_amount    $ dollar total of category
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
# @param categories               this is a Category object
# @logfn
def create_category_amounts_array(transactions, categories):
    category_amounts = []  # form 1D array of amounts to return
    for category in categories:
        category_amounts.append(sum_individual_category(transactions, category.id))
    return categories, category_amounts


# creates a summation of the top level categories (top root categories)
#   the summation will be of all children node below the root
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

# @param   N is the number of bins to form across dates
def get_date_binned_transaction(days_prev, N):
    # create the DATETIME objects from the previous days in N groups
    edge_code_date = dateh.get_edge_code_dates(
        datetime.today(),
        days_prev,
        N) # have to add +2 here because we want N to be the number of bins not indices

    print("Got this for transactions edge codes")
    for edge in edge_code_date:
        print(edge)

    date_binned_transactions = []

    for i in range(0, N):
        cur_trans = transaction_recall.recall_transaction_data(edge_code_date[i], edge_code_date[i+1])
        date_binned_transactions.append(cur_trans)

    return date_binned_transactions, edge_code_date


# @logfn
def filter_transactions_date(transactions, date_start, date_end):
    logger.debug(f"Filtering transactions between {date_start} TO {date_end}")
    filtered_transactions = []
    for transaction in transactions:
        if dateh.date_between(date_start, date_end, transaction.date):
            filtered_transactions.append(transaction)
    return filtered_transactions


##############################################################################
####      DATA MANIPULATION FUNCTIONS    #####################################
##############################################################################

# gen_Bx_matrix: generate 'Bx_matrix'
#       this function split vectors of B --> N parts. Each part is called a Bx, which is a collection of balance ledger data
#       @return    spl_Bx             an array of dictionary entries with entry[account_id] = balance amount
#       @return    edge_code_date     date edge codes (string format YYYY-MM-DD)
@logfn
# TODO: I could change my "get_balances" function to already date bin balance data. Similiar to way I handle transactions
def gen_Bx_matrix(date_range_end, days_prev, N):
    # init date object 'days_prev' less
    date_range_start = dateh.get_date_days_prev(date_range_end, days_prev)

    # get balance data
    balance_data = dbh.balance.get_balances_between_date(date_range_start, date_range_end)

    # populate arrays for displaying data. All of length N
    spl_Bx = []  # this is also the length of N

    # init date edge limits
    edge_code_date = dateh.get_edge_code_dates(date_range_end, days_prev, N)

    added_sql_key = []
    # search through edge code limits to add N bin A vectors
    for i in range(0, N):

        a_A = {}
        # init A vector
        for account_id in dbh.account.get_all_account_ids():
            a_A[account_id] = 0

        # iterate through all balances data
        for bx in balance_data:
            # bx outline
            # bx[0] = sql key
            # bx[1] = account_id
            # bx[2] = total
            # bx[3] = bal_date

            # grab date of balance 'bx' item and error handle
            try:
                bx_datetime = datetime.strptime(bx[3], "%Y-%m-%d")
                bx_date = bx_datetime.date()
            except ValueError as e:
                logger.exception(
                    f"Error converting string to datetime object: {bx[3]} with exception details {e}"
                )
                raise AnalyzerHelperError("Can't proceed with populating Bx A vector")

            # if date is less than edge code (in the date bin)
            if bx_date < datetime.strptime(edge_code_date[i+1], "%Y-%m-%d").date():
                if bx[0] not in added_sql_key:
                    a_A[bx[1]] = bx[2]
                    added_sql_key.append(bx[0])
                # NOTE: took out below code so the current code is just adding latest ones
                # if the balance is higher than what we currently have than replace Bx in spl_Bx
                #    in this way we get the 'dominant' vector (high value)
                # if bx[2] > a_A[bx[1]]:

        # append vector to spl_Bx after search for 'dominant' vector is complete
        spl_Bx.append(a_A)

    return spl_Bx, edge_code_date


@logfn
def gen_bin_A_matrix(spl_Bx):
    # set which type number corresponds to which type of account
    inv_acc = [4]
    liquid_acc = [0, 1, 2, 3]

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

