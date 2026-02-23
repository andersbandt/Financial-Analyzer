"""
@file a05_analyze_history.py
@brief sub menu for performing ANALYSIS on financial data

"""

# import needed packages
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
from analysis import transaction_helper as transh
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
    # Save original cat_str before stripping so baseline uses the same unmodified index order
    original_top_cat_str = top_cat_str
    top_cat_str, prev_amounts = grah.strip_non_expense_categories(original_top_cat_str, prev_amounts)
    _, baseline_amounts = grah.strip_non_expense_categories(original_top_cat_str, baseline_amounts)

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


class TabSpendingHistory(SubMenu):
    def __init__(self, title, basefilepath):

        self.basefilepath = basefilepath  # had to add this in, at some point maybe delete?

        # initialize information about sub menu options
        action_arr = [
              Action("Executive summary", self.a01_exec_summary),
              Action("Print database transactions", self.a02_print_db_trans),
              Action("Search transactions", self.a03_search_trans),
              Action("Graph category data", self.a04_graph_category),
              Action("Generate sankey diagram", self.a05_make_sankey),
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
        # Call the search helper function
        return transh.search_trans()


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
        all_levels = clih.promptYesNo("Include all subcategory levels? (No = direct children only)")
        if all_levels:
            sub_categories = cath.get_all_category_descendants(category_id)
        else:
            sub_categories = cath.get_category_children(category_id)
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


# TODO: would be interesting to have an option where it averages the months (from the same chosen date range) and displays that instead
    def a05_make_sankey(self):
        # Ask user which view they want
        print("\nSankey Diagram Options:")
        print("  1. Top-level categories (Income → Food, Housing, etc.)")
        print("  2. Hierarchical view (show subcategory relationships)")
        view_choice = clih.spinput("Which view would you like? (1 or 2): ", inp_type="int")

        if view_choice == 1:
            view_mode = "top_level"
            categories = cath.get_top_level_categories()
        elif view_choice == 2:
            view_mode = "hierarchical"
            categories = cath.load_categories()
        else:
            print("Invalid choice. Defaulting to top-level view.")
            view_mode = "top_level"
            categories = cath.get_top_level_categories()

        # Ask user for date range
        print("\nDate Range Options:")
        print("  1. Calendar year (e.g., 2024)")
        print("  2. Last X days")
        print("  3. Custom date range")
        date_choice = clih.spinput("How would you like to select dates? (1-3): ", inp_type="int")

        if date_choice == 1:
            # Calendar year
            year = clih.get_year_input()
            if year is False:
                print("Invalid year. Cancelling.")
                return False
            date_start = f"{year}-01-01"
            date_end = f"{year}-12-31"
            print(f"Selected: {year} ({date_start} to {date_end})")

        elif date_choice == 2:
            # Last X days
            days = clih.spinput("How many days back?: ", inp_type="int")
            if days is False:
                print("Invalid input. Cancelling.")
                return False
            date_start = dateh.get_date_previous(days)
            date_end = dateh.get_cur_str_date()
            print(f"Selected: Last {days} days ({date_start} to {date_end})")

        elif date_choice == 3:
            # Custom date range
            print("Enter start date (YYYY-MM-DD):")
            date_start = clih.spinput("Start date: ", inp_type="text")
            if date_start is False:
                print("Invalid input. Cancelling.")
                return False
            print("Enter end date (YYYY-MM-DD):")
            date_end = clih.spinput("End date: ", inp_type="text")
            if date_end is False:
                print("Invalid input. Cancelling.")
                return False
            print(f"Selected: {date_start} to {date_end}")

        else:
            print("Invalid choice. Defaulting to last 365 days.")
            date_start = dateh.get_date_previous(365)
            date_end = dateh.get_cur_str_date()

        # Get transactions for selected date range
        transactions = transr.recall_transaction_data(date_start=date_start, date_end=date_end)

        if not transactions:
            print(f"No transactions found for date range {date_start} to {date_end}")
            return False

        spending_data = anah.generate_sankey_data(transactions, categories, view_mode=view_mode)

        # Create source and target indices
        labels, sources, targets, values = anah.process_sankey_data(spending_data)

        # Build intuitive title
        view_name = "Top-Level" if view_mode == "top_level" else "Hierarchical"
        title = f"Spending Flow - {view_name} View ({date_start} to {date_end})"

        # Generate the Sankey diagram
        grapa.generate_sankey(labels, sources, targets, values, title=title)
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


