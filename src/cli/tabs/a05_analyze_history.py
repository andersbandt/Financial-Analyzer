"""
@file a05_analyze_history.py
@brief sub menu for performing ANALYSIS on financial data

"""

# import needed packages
from pprint import pprint
import utils

# import user defined CLI modules
import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.cli_class import SubMenu
from cli.cli_class import Action

# import user defined HELPER modules
import db.helpers as dbh
import categories.categories_helper as cath
from analysis import analyzer_helper as anah
from analysis.graphing import graphing_analyzer as grapa
from analysis.graphing import graphing_helper as grah
from analysis.data_recall import transaction_recall as transr
from tools import date_helper as dateh
from utils import log_helper as logh
import utils

# import user defined modules
from statement_types import Ledger

# import logger
from loguru import logger


##############################################################################
####      GENERAL HELPER FUNCTIONS    ########################################
##############################################################################
# exec_summary_01: produces a graph of the top-level categories over time
def exec_summary_01(time_param, method='date', num_slices=6):
    """
    Produces a graph of top-level categories over time.

    Args:
        time_param: If method='date', this is days_prev (int). If method='month', this is months_prev (int).
        method: 'date' for date-based binning, 'month' for month-based retrieval
        num_slices: Number of time slices (only used when method='date')

    Returns:
        True on success
    """
    # LOAD CATEGORIES
    categories = cath.load_categories()

    # Get transactions based on chosen method
    if method == 'date':
        # METHOD 1: Date-based binning
        days_prev = time_param
        date_bin_trans, edge_codes = anah.get_date_binned_transaction(days_prev, num_slices)

        # Create labels from edge codes
        labels = []
        for i in range(len(edge_codes) - 1):
            labels.append(edge_codes[i] + " to " + edge_codes[i + 1])

        title = "ExS 01: Top categories across time (date-based)"

    elif method == 'month':
        # METHOD 2: Month-based retrieval
        months_prev = time_param
        [current_year, current_month, day] = dateh.get_date_int_array()

        # Calculate oldest month first
        oldest_month = current_month - months_prev + 1
        oldest_year = current_year
        while oldest_month < 1:
            oldest_month += 12
            oldest_year -= 1

        # Build arrays from oldest to newest (left to right on graph)
        date_bin_trans = []
        labels = []
        year = oldest_year
        month = oldest_month

        for i in range(months_prev):
            date_bin_trans.append(transr.recall_transaction_month_bin(year, month))
            labels.append(f"{year}-{month:02d}")  # Zero-padded month for better sorting
            month += 1
            if month > 12:  # handle year wraparound
                month = 1
                year += 1

        title = f"ExS 01: Top categories across previous {months_prev} months"
    else:
        raise ValueError(f"Invalid method '{method}'. Must be 'date' or 'month'")

    # Perform analysis to sum categories
    logger.debug("Analyzing spending on top categories for date binned transactions")
    date_bin_dict_arr = anah.gen_bin_analysis_dict(date_bin_trans)

    # Extract category strings from first bin
    top_cat_str = date_bin_dict_arr[0]["categories"]

    # Build dictionary to organize amounts by category
    top_cat_dict = {}
    for cat_str in top_cat_str:
        top_cat_dict[cat_str] = []

    # Populate amounts for each category across all bins
    for d_bin in date_bin_dict_arr:
        i = 0
        for amount in d_bin["amounts"]:
            amount = -1 * amount  # Flip sign for expenses
            top_cat_dict[top_cat_str[i]].append(amount)
            i += 1

    # Set up y-axis array for graphing
    y_axis_arr = []
    for cat_str in top_cat_str:
        y_axis_arr.append(top_cat_dict[cat_str])

    # Create the graph
    grapa.create_mul_line_chart(labels,
                                y_axis_arr,
                                title=title,
                                labels=top_cat_str,
                                rotate_labels=True,
                                legend=True,
                                y_format='currency')
    return True


# exec_summary_02: compares previous month spending to baseline average
# TODO: this function does not work (all percents are 100%)
def exec_summary_02(comp_month_prev):
    """
    Compares the previous month's spending to an average of the months before it.

    Args:
        comp_month_prev: Number of months to use as baseline for comparison
    """
    logger.info("\n\n\n... comparing previous month spending to running averages ...")

    # Get current date
    [current_year, current_month, _] = dateh.get_date_int_array()

    # Get previous month transactions (until we find a month loaded)
    prev_year, prev_month = dateh.get_previous_month(current_year, current_month)
    status = True
    while status:
        prev_month_trans = transr.recall_transaction_month_bin(prev_year, prev_month)
        if len(prev_month_trans) > 0:
            status = False
        prev_year, prev_month = dateh.get_previous_month(prev_year, prev_month)

    logger.info(f"Previous month: {prev_year}-{prev_month:02d}")

    # STEP 2: Calculate baseline period (comp_month_prev months BEFORE previous month)
    # Example: If prev_month is Dec 2025 and comp_month_prev=3
    # Baseline should be: Sep 2025, Oct 2025, Nov 2025
    baseline_end_month = prev_month - 1
    baseline_end_year = prev_year
    while baseline_end_month < 1:
        baseline_end_month += 12
        baseline_end_year -= 1

    baseline_start_month = baseline_end_month - comp_month_prev + 1
    baseline_start_year = baseline_end_year
    while baseline_start_month < 1:
        baseline_start_month += 12
        baseline_start_year -= 1

    # Get date ranges for baseline period
    baseline_range_start = dateh.month_year_to_date_range(baseline_start_year, baseline_start_month)
    baseline_range_end = dateh.month_year_to_date_range(baseline_end_year, baseline_end_month)

    # Get baseline transactions
    baseline_trans = transr.recall_transaction_data(
        baseline_range_start[0],
        baseline_range_end[1]
    )
    logger.info(f"Baseline period: {baseline_range_start[0]} to {baseline_range_end[1]} ({comp_month_prev} months)")

    # STEP 3: Load categories and calculate amounts (only once to ensure consistency)
    categories = cath.load_categories()
    top_cat_str, prev_amounts = anah.create_top_category_amounts_array(
        prev_month_trans, categories, count_NA=False
    )
    _, baseline_amounts = anah.create_top_category_amounts_array(
        baseline_trans, categories, count_NA=False
    )

    # Strip non-expense categories for cleaner comparison
    top_cat_str, prev_amounts = grah.strip_non_expense_categories(top_cat_str, prev_amounts)
    _, baseline_amounts = grah.strip_non_expense_categories(top_cat_str, baseline_amounts)

    # STEP 4: Calculate percentage differences
    # Normalize baseline to monthly average (divide by number of comparison months)
    baseline_avg = [abs(x) / comp_month_prev for x in baseline_amounts]
    prev_abs = [abs(x) for x in prev_amounts]

    percent_diffs = []
    for i in range(len(prev_abs)):
        if baseline_avg[i] == 0:
            # No baseline spending - can't calculate percentage
            if prev_abs[i] == 0:
                delta = 0  # No change (both zero)
            else:
                delta = 100  # New spending appeared
        else:
            # Calculate percentage change: ((new - old) / old) * 100
            delta = ((prev_abs[i] - baseline_avg[i]) / baseline_avg[i]) * 100

        percent_diffs.append(delta)

        # Print detailed comparison
        print(f"\t{top_cat_str[i]}")
        print(f"\t\tPrevious month: ${prev_abs[i]:.2f}")
        print(f"\t\tBaseline avg:   ${baseline_avg[i]:.2f}")
        print(f"\t\tDelta:          {delta:+.1f}%\n")

    # STEP 5: Create bar chart
    title = f"ExS 02: % Change from {comp_month_prev}-month average"
    grapa.create_bar_chart(
        top_cat_str,
        percent_diffs,
        xlabel="% change (positive = spent more than average)",
        title=title
    )
    return True


def search_01():
    search_str = clih.spinput("\nWhat is the keyword you want to search for in transaction description?",
                              "text")
    if search_str is False:
        print("Ok, quitting transaction search.\n")
        return False
    transactions = transr.recall_transaction_desc_keyword(search_str)
    return transactions


def search_02():
    # determine user choice of type of category search
    cat_search_type = clih.prompt_num_options("What type of category search?",
                                              ["recursive (children)", "individual"])
    cat_search_type = 2 # tag:HARDCODE

    if cat_search_type == 1:
        search_str = clih.category_tree_prompt()
        if search_str is False or search_str == -1:
            print("Ok, quitting transaction search.\n")
            return False
        children_id = cath.get_category_children(search_str)
        transactions = transr.recall_transaction_category(search_str)
        for child_id in children_id:
            transactions.extend(transr.recall_transaction_category(child_id))
    elif cat_search_type == 2:
        search_str = clih.category_prompt_all("What is the category to search for?", False)
        if search_str is False:
            print("Ok, quitting transaction search.\n")
            return False
        transactions = transr.recall_transaction_category(search_str)
    elif cat_search_type is False:
        print("Ok, quitting transaction search.\n")
        return False
    else:
        print(f"Uh oh, bad category search type of: {cat_search_type}")
        return False
    return transactions


def search_03():
    start_date = clih.get_date_input("What is the start date of search range?")
    end_date = clih.get_date_input("What is the end date of search range?")
    if start_date is False or end_date is False:
        print("Ok, quitting transaction search.\n")
        return False
    transactions = transr.recall_transaction_data(start_date, end_date)
    return transactions


def search_04():
    account_id = clih.account_prompt_all("What is the account you want to search?")
    if account_id is False:
        print("Ok, quitting transaction search.\n")
        return False
    transactions = transr.recall_transaction_account(account_id)
    return transactions


def search_05_multi_filter():
    """Multi-filter search - allows filtering by multiple criteria at once"""
    print("\n... setting up multi-filter search ...")
    print("You can apply multiple filters. Select filters one by one, then apply all at once.\n")

    # Dictionary to store active filters
    active_filters = {
        'description': None,
        'category': None,
        'date_range': None,
        'account': None,
        'amount_min': None,
        'amount_max': None
    }

    # Let user select which filters to apply
    while True:
        print("\n=== Current Active Filters ===")
        for filter_name, filter_value in active_filters.items():
            if filter_value is not None:
                print(f"  {filter_name}: {filter_value}")

        filter_options = [
            "Add DESCRIPTION filter",
            "Add CATEGORY filter",
            "Add DATE RANGE filter",
            "Add ACCOUNT filter",
            "Add AMOUNT filter (min/max)",
            "DONE - Apply filters and search"
        ]

        choice = clih.prompt_num_options("\nWhat filter would you like to add?: ", filter_options)

        if choice is False:
            print("Ok, quitting multi-filter search.\n")
            return False
        elif choice == 1:  # Description
            search_str = clih.spinput("Enter keyword to search in description", "text")
            if search_str is not False:
                active_filters['description'] = search_str
        elif choice == 2:  # Category
            category_id = clih.category_prompt_all("What is the category to filter by?", False)
            if category_id is not False:
                active_filters['category'] = category_id
        elif choice == 3:  # Date range
            start_date = clih.get_date_input("What is the start date of search range?")
            if start_date is not False:
                end_date = clih.get_date_input("What is the end date of search range?")
                if end_date is not False:
                    active_filters['date_range'] = (start_date, end_date)
        elif choice == 4:  # Account
            account_id = clih.account_prompt_all("What is the account to filter by?")
            if account_id is not False:
                active_filters['account'] = account_id
        elif choice == 5:  # Amount
            print("\nAmount filter (leave blank to skip min or max)")
            amount_min = clih.spinput("Enter minimum amount (or q to skip)", "float")
            if amount_min is not False:
                active_filters['amount_min'] = amount_min
            amount_max = clih.spinput("Enter maximum amount (or q to skip)", "float")
            if amount_max is not False:
                active_filters['amount_max'] = amount_max
        elif choice == 6:  # Done
            break

    # Check if any filters were set
    if all(v is None for v in active_filters.values()):
        print("No filters applied. Returning all transactions.")
        return transr.recall_transaction_data()

    # Start with all transactions or use date range as base
    if active_filters['date_range'] is not None:
        start_date, end_date = active_filters['date_range']
        transactions = transr.recall_transaction_data(start_date, end_date)
    else:
        transactions = transr.recall_transaction_data()

    print(f"\nStarting with {len(transactions)} transactions")

    # Apply each filter progressively
    if active_filters['description'] is not None:
        keyword = active_filters['description'].lower()
        transactions = [t for t in transactions if keyword in t.description.lower()]
        print(f"After description filter: {len(transactions)} transactions")

    if active_filters['category'] is not None:
        cat_id = active_filters['category']
        transactions = [t for t in transactions if t.category_id == cat_id]
        print(f"After category filter: {len(transactions)} transactions")

    if active_filters['account'] is not None:
        acc_id = active_filters['account']
        transactions = [t for t in transactions if t.account_id == acc_id]
        print(f"After account filter: {len(transactions)} transactions")

    if active_filters['amount_min'] is not None:
        min_val = active_filters['amount_min']
        transactions = [t for t in transactions if t.value >= min_val]
        print(f"After minimum amount filter: {len(transactions)} transactions")

    if active_filters['amount_max'] is not None:
        max_val = active_filters['amount_max']
        transactions = [t for t in transactions if t.value <= max_val]
        print(f"After maximum amount filter: {len(transactions)} transactions")

    print(f"\n=== Final result: {len(transactions)} transactions ===\n")
    return transactions


class TabSpendingHistory(SubMenu):
    def __init__(self, title, basefilepath):

        self.basefilepath = basefilepath  # had to add this in, at some point maybe delete?

        # initialize information about sub menu options
        action_arr = [
              Action("Executive summary", self.a01_exec_summary),
              Action("Print database transactions", self.a02_print_db_trans),
              Action("Search transactions", self.a03_search_trans),
              Action("Graph category data", self.a04_graph_category),
              Action("Generate sankey (not working)", self.a05_make_sankey),
              Action("Review specific month transactions", self.a06_review_month),
              Action("Add note to transaction", self.a07_add_note),
                      ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

    # a01_exec_summary: creates a list of "executive summary items" about spending data
    def a01_exec_summary(self):
        months_prev = clih.spinput("How many months previous would you like to examine?", inp_type="int")
        if months_prev is False:
            print("Ok, quitting executive summary")
            return False

        # clear tmp folder
        # TODO: somehow need to abstract the sequence of below (clearing tmp_folder, writing graph creation functions, and calling generate_summary_pdf)
        logh.clear_tmp_folder()
        grapa.reset_figure_counter()

        # EXEC 1: plot data using date-based binning
        exec_summary_01(
            time_param=months_prev * 30,  # days previous
            method='date',
            num_slices=6)

        # EXEC 1b: plot data using month-based retrieval
        exec_summary_01(
            time_param=months_prev,  # months previous
            method='month')

        # EXEC 2: current categories with a big delta to past averages
        exec_summary_02(months_prev)

        # EXEC 3: get gross stats
        today = dateh.get_cur_str_date()
        days_ago = dateh.get_date_previous(months_prev * 30)
        transactions = transr.recall_transaction_data(days_ago, today)
        ledger_stats = anah.return_ledger_exec_dict(transactions)
        print(
            f"\nGot this for ledger statistics for past {months_prev} months\n\tor {days_ago} days ago\n")
        clip.print_dict(ledger_stats)

        # generate pdf file AND open
        print("\nGenerating .pdf ...")

        logh.generate_summary_pdf(utils.OUTPUT_PDF_2)

        # great, we made it
        return True


    # a02_print_db_trans: prints EVERY transaction in ledger .db
    def a02_print_db_trans(self):
        transactions = transr.recall_transaction_data()
        tmp_ledger = Ledger.Ledger("All Statement Data")
        tmp_ledger.set_statement_data(transactions)
        tmp_ledger.sort_date_desc()
        tmp_ledger.print_statement(include_sql_key=True)
        return True


    # a03_search_trans: performs a search of transaction database
    def a03_search_trans(self):
        print("... searching transactions ...")

        # get input on what type of search to do
        search_options = ["DESCRIPTION", "CATEGORY", "DATE", "ACCOUNT", "MULTI-FILTER"]
        search_type = clih.prompt_num_options("What type of search do you want to perform?: ",
                                              search_options)
        if search_type is False:
            print("Ok, quitting transaction search.\n")
            return False

        # get transaction description keyword
        if search_type == 1:
            transactions = search_01()
        elif search_type == 2:
            transactions = search_02()
        elif search_type == 3:
            transactions = search_03()
        elif search_type == 4:
            transactions = search_04()
        elif search_type == 5:
            transactions = search_05_multi_filter()
        else:
            print(f"Can't perform search with search type of: {search_type}")
            return False

        # check if search was cancelled
        if transactions is False:
            print("Search cancelled.")
            return False

        # form Ledger, print, and return executive summary
        tmp_ledger = Ledger.Ledger(f"Transactions with for search type {search_type}")
        tmp_ledger.set_statement_data(transactions)
        tmp_ledger.print_statement(include_sql_key=True)

        ledger_exec = anah.return_ledger_exec_dict(transactions)
        print("\n")
        pprint(ledger_exec)
        # TODO: DEVIATION from returning boolean. How to handle? Sub helper function for the actual search probably?
        return transactions


    # a04_graph_category: walks user through producing a graph of a certain category
    def a04_graph_category(self):
        # get category ID
        category_id = clih.category_prompt_all("What is the category to graph?", False)
        if category_id is None or category_id is False or category_id == 0:
            print("Ok, quitting graph category")
            return False

        # set up month parameters
        months_prev = 12 # tag:HARDCODE
        months = []

        ### METHOD 2: all sub-children categories as well
        sub_categories = cath.get_category_children(category_id) # TODO: add a function to get ALL subcategory children (this is just one level below right now)
        sub_categories.append(category_id)
        month_totals = [] # now this should be a matrix of size MxN where N is the number of bar graph slices (number of months in this case)
        labels = []
        for sc_id in sub_categories:
            labels.append(cath.category_id_to_name(sc_id))
            transactions = transr.recall_transaction_category(sc_id)
            [months, mts] = anah.month_bin_transaction_total(transactions, months_prev)
            month_totals.append(mts)

        grapa.create_stack_bar_chart(
            months,
            month_totals,
            title=f"Graph of category {cath.category_id_to_name(category_id)} and subchildren",
                                   labels=labels,
                                   y_format="currency",
                                   sort_by_column="last")
        grapa.show_plots()
        return True

    # TODO: really to handle my incomes everything actually needs to feed into an income group, and all the expenses out of that
    # TODO: clean up the "non-graphical" transactions
    # TODO: it sucks because I put in a whole day to get this working with everything but ..... it might look better with only the top level categories
    def a05_make_sankey(self):
        # set up date information\
        # TODO: should I just have this actually enter calendar years? Or possible two options. 1- calendary year like 2024 or 2-date range
        days_ago = dateh.get_date_previous(365) # tag:HARDCODE

        # get raw transactions and categories to use from time period
        transactions = transr.recall_transaction_data(date_start=days_ago)

        #categories = cath.load_categories()
        categories = cath.get_top_level_categories()

        spending_data = anah.generate_sankey_data(transactions, categories)

        # Create source and target indices
        labels, sources, targets, values = anah.process_sankey_data(spending_data)

        # Generate the Sankey diagram
        grapa.generate_sankey(labels, sources, targets, values)
        return True


    def a06_review_month(self):
        # get month of interest
        year = clih.get_year_input()
        if year is False:
            print("Ok, quitting review month")
            return False
        month = clih.get_month_input()
        if month is False:
            print("Ok, quitting review month")
            return False

        month_transactions = transr.recall_transaction_month_bin(year, month)
        tmp_ledger = Ledger.Ledger(f"Transactions from ({year},{month})")
        tmp_ledger.set_statement_data(month_transactions)
        tmp_ledger.sort_trans_asc()
        tmp_ledger.print_statement(include_sql_key=True)
        return True


    def a07_add_note(self):
        # get sql key of transaction
        sql_key = clih.spinput("What is the SQL key of the transaction to add a note to?: ", "int")
        if sql_key is False:
            print("Ok, quitting adding note to transaction")

        trans = transr.get_transaction(sql_key)
        print(f"Found transaction with sql_key={sql_key}\n")
        trans.printTransaction()

        # get note content
        note_str = clih.spinput("What do you want the note to say?: ", "text")

        # update and print new transaction
        print(f"Confirming transaction update for item with sql_key={sql_key}")
        trans.note = note_str
        trans.printTransaction()
        print(f"\nNew note ---> {note_str}\n")

        # do one last sanity check
        res = clih.promptYesNo("Are you sure you want to change the transaction listed above?: ")
        if not res:
            print(f"Ok, not adding note to transaction with sql_key={sql_key}")
            return False
        else:
            # update note in database
            dbh.transactions.update_transaction_note_k(sql_key, note_str)
            return True


