

# import needed modules
from datetime import datetime
from pprint import pprint
from collections import defaultdict

# import user defined modules
import db.helpers as dbh
from categories import categories_helper as cath
import analysis.transaction_helper as transh
import analysis.data_recall.transaction_recall as transaction_recall
import analysis.graphing.graphing_helper as grah
import tools.date_helper as dateh

# import logger
from loguru import logger


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
def return_ledger_exec_dict(transactions):
    expenses = 0
    incomes = 0

    not_counted = ["BALANCE", "SHARES", "TRANSFER", "VALUE", "INTERNAL"]  # tag:hardcode
    print("\n\nCreating expenses/income summary for transactions without the following counted")
    pprint(not_counted)

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
                    "incomes": incomes,
                    "delta (incomes-expenses): ": (incomes+expenses)}

    return exec_summary


# month_bin_transaction_total: takes in a list of transactions and counts total for each month
def month_bin_transaction_total(transactions, months_prev):
    """
    Bins transactions by month and returns totals for each month.

    Args:
        transactions: List of Transaction objects to analyze
        months_prev: Number of previous months to analyze (including current month)

    Returns:
        [labels, month_totals]: Labels (e.g., "2025-08") and corresponding totals
    """
    # Get current date
    [current_year, current_month, _] = dateh.get_date_int_array()

    # Calculate oldest month (go back months_prev - 1 because we include current month)
    oldest_month = current_month - months_prev + 1
    oldest_year = current_year
    while oldest_month < 1:
        oldest_month += 12
        oldest_year -= 1

    # Build arrays from oldest to newest (left to right on graph)
    month_totals = []
    labels = []
    year = oldest_year
    month = oldest_month

    for _ in range(months_prev):
        # Get date range for this month
        date_range = dateh.month_year_to_date_range(year, month)

        # Filter transactions by this month's range and sum
        month_transactions = filter_transactions_date(transactions, date_range[0], date_range[1])
        month_totals.append(transh.sum_transaction_total(month_transactions))
        labels.append(f"{year}-{month:02d}")

        # Move to next month
        month += 1
        if month > 12:
            month = 1
            year += 1

    return [labels, month_totals]


# sum_individual_category: returns the dollar ($) total of a certain category in an array of transactions
#   @param   transactions    list of Transaction objects, category_id- category_id of interest
#   @return  total_amount    $ dollar total of category
def sum_individual_category(transactions, category_id):
    total_amount = 0
    for transaction in transactions:  # for every transaction in the statement
        if transaction.category_id == category_id:
            try:
                total_amount += transaction.value
            except TypeError as e:
                error = f"Uh oh, wrong type in transaction: {transaction.description}"
                logger.exception(error)
    return total_amount


# create_category_amounts_array: returns the dollar ($) total of all categories in a statement
# @param categories               this is a Category object
def create_category_amounts_array(transactions, categories):
    category_amounts = []  # form 1D array of amounts to return
    for category in categories:
        category_amounts.append(sum_individual_category(transactions, category.id))
    return category_amounts


# creates a summation of the top level categories (top root categories)
#   the summation will be of all children node below the root
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


def generate_sankey_data(transactions, categories, view_mode="top_level"):
    """
    Processes transactions and categories into spending_data format for Sankey.

    Args:
        transactions: List of transaction objects
        categories: List of category objects to include
        view_mode: "top_level" or "hierarchical"
            - "top_level": Shows income flowing to top-level expense categories
            - "hierarchical": Shows parent -> child category relationships

    Returns:
        List of dicts with 'category', 'subcategory', 'amount' keys
    """
    # Map categories by ID for quick access
    category_map = {cat.id: cat for cat in categories}

    # Prepare data structure to aggregate amounts
    spending_dict = defaultdict(float)

    if view_mode == "top_level":
        # TOP-LEVEL VIEW: Roll up all transactions to their top-level categories
        for transaction in transactions:
            # Get the top-level category for this transaction
            top_level_id = cath.get_category_parent(transaction.category_id, printmode=False)
            top_level_cat = category_map.get(top_level_id)

            if not top_level_cat:
                continue

            # Create self-referencing flow (income source will be added in process_sankey_data)
            parent_name = top_level_cat.name
            child_name = top_level_cat.name

            spending_dict[(parent_name, child_name)] += transaction.value

    elif view_mode == "hierarchical":
        # HIERARCHICAL VIEW: Show parent -> child category relationships
        # Load all categories for lookup
        all_categories = cath.load_categories()
        all_cat_map = {cat.id: cat for cat in all_categories}

        for transaction in transactions:
            trans_cat = all_cat_map.get(transaction.category_id)

            if not trans_cat:
                continue

            # Determine parent-child relationship
            if trans_cat.parent == 1:
                # Top-level category - self-reference (will flow from income)
                parent_name = trans_cat.name
                child_name = trans_cat.name
            else:
                # Child category - find parent and create parent -> child flow
                parent_cat = all_cat_map.get(trans_cat.parent)

                if parent_cat:
                    parent_name = parent_cat.name
                    child_name = trans_cat.name
                else:
                    # Parent not found, skip
                    continue

            spending_dict[(parent_name, child_name)] += transaction.value

    else:
        raise ValueError(f"Invalid view_mode '{view_mode}'. Must be 'top_level' or 'hierarchical'")

    # Convert aggregated data to spending_data format
    spending_data = [
        {"category": parent, "subcategory": child, "amount": amount}
        for (parent, child), amount in spending_dict.items()
    ]

    return spending_data


def process_sankey_data(data):
    """
    Processes input data into labels and links for a Sankey diagram.
    """

    # Helper function to flatten nested subcategories
    def extract_subcategories(data):
        subcategories = set()
        for item in data:
            if isinstance(item, dict) and "subcategory" in item:
                subcat = item["subcategory"]
                if isinstance(subcat, list):
                    # Recursively extract subcategories from the list
                    subcategories.update(extract_subcategories(subcat))
                else:
                    subcategories.add(subcat)
        return subcategories

    # Extract unique subcategories
    subcategories = extract_subcategories(data)

    # Extract unique categories
    categories = {item["category"] for item in data}

    # Combine categories and subcategories, ensuring no duplicates
    labels = list(categories | subcategories)  # Set union to ensure uniqueness

    # Find income source category (positive amounts) - prefer one that exists in data
    income_source = None
    for item in data:
        if item["amount"] > 0:
            income_source = item["category"]
            break

    # If no income found in data, check if "PAYCHECK" category exists, otherwise use first category
    if income_source is None:
        if "PAYCHECK" in labels:
            income_source = "PAYCHECK"
        elif labels:
            income_source = labels[0]
        else:
            income_source = "Income"  # Fallback if no labels at all

    # Ensure income source is in labels
    if income_source not in labels:
        labels.append(income_source)

    sources = []
    targets = []
    values = []

    def process_item(item):
        """
        Recursively process each item, adding links and labels.
        """
        if item["amount"] < 0:
            if item["category"] == item["subcategory"]:  # handle top-level categories
                source_idx = labels.index(income_source)
            else:
                source_idx = labels.index(item["category"])
        else:
            source_idx = labels.index(item["category"])

        sources.append(source_idx)

        # Determine the target based on subcategories (assuming a structure with 'subcategory')
        target_idx = labels.index(item["subcategory"])
        targets.append(target_idx)
        values.append(abs(item["amount"])) # NOTE: unsure if this is required or not, but couldn't get anything to show up when they are negative

    for item in data:
        process_item(item)

    return labels, sources, targets, values


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
def gen_Bx_matrix(date_range_end, days_prev, N):
    # init date object 'days_prev' less
    date_range_start = dateh.get_date_days_prev(date_range_end, days_prev)

    # get balance data
    balance_data = dbh.balance.get_balances_between_date(date_range_start, date_range_end)

    # populate arrays for displaying data. All of length N
    spl_Bx = []  # this is also the length of N

    # init date edge limits
    edge_code_date = dateh.get_edge_code_dates(date_range_end, days_prev, N)

    added_sql_key = [] # TODO (low priority): figure out if this thing is actually needed or we can restructure the flow
    # search through edge code limits to add N bin A vectors
    for i in range(0, N):
        # init A vector (dict)
        a_A = {}
        for account_id in dbh.account.get_all_account_ids():
            a_A[account_id] = 0

        # iterate through all balances data
        for bx in balance_data:
            # TODO: possible could create a Balance class.... could be parent of Transaction honestly?
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
                logger.exception(f"Error converting string to datetime object: {bx[3]} with exception details {e}")
                raise AnalyzerHelperError("Can't proceed with populating Bx A vector")

            # if date is less than edge code (in the date bin)
            if bx_date < datetime.strptime(edge_code_date[i+1], "%Y-%m-%d").date():
                if bx[0] not in added_sql_key:
                    # set balance value for account_id (bx[1]) in the a_A vector
                    a_A[bx[1]] = bx[2]
                    added_sql_key.append(bx[0])

        # NOTE: added check for 0 valued balances when we have a balance registered in previous vector
        for account_id in dbh.account.get_all_account_ids():
            if a_A[account_id] == 0:
                try:
                    a_A[account_id] = spl_Bx[-1][account_id]
                except IndexError:  # had to add this check for first-pass
                    pass

        # append vector to spl_Bx after search for 'dominant' vector is complete
        spl_Bx.append(a_A)

    return spl_Bx, edge_code_date


# gen_bin_analysis_dict: takes in an array of binned transactions and returns an array of dictionaries with a summary
#   param[in]   binned transactions   an array of arrays. [bin1, bin2, bin3, ..... binN] where bin1 is an array
#   param[out]  bin_dict_array        an array of dictionary objects with summary information
def gen_bin_analysis_dict(binned_transactions):
    # LOAD CATEGORIES
    categories = cath.load_categories()

    bin_dict_arr = []
    i = 0
    for trans_arr in binned_transactions:
        top_cat_str, amounts = create_top_category_amounts_array(trans_arr, categories, count_NA=False)

        # do some post-processing on top-level categories and amounts
        top_cat_str, amounts = grah.strip_non_expense_categories(top_cat_str, amounts)

        # append dict to an array of all date ranges
        bin_dict_arr.append(
            {"number": i,
             "categories": top_cat_str,
             "amounts": amounts,
             }
        )
        i += 1
    return bin_dict_arr