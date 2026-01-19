"""
@file a05_analyze_history.py
@brief sub menu for performing ANALYSIS on financial data

"""
# TODO: make every function quittable on at least the first item with the regular escape characters (q, quit, exit)

# import needed packages
from pprint import pprint

# import user defined CLI modules
import cli.cli_helper as clih
import cli.cli_printer as clip
import utils
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

# import user defined modules
from statement_types import Ledger

# import logger
from loguru import logger


##############################################################################
####      GENERAL HELPER FUNCTIONS    ########################################
##############################################################################
# exec_summary_01: produces a graph of the top-level categories over time
def exec_summary_01(days_prev, num_slices):
    # LOAD CATEGORIES
    categories = cath.load_categories()

    # get transactions between certain "edge codes"
    date_bin_trans, edge_codes = anah.get_date_binned_transaction(days_prev,  # number of previous days
                                                                  num_slices)  # n = 12 different slices

    date_bin_dict_arr = []  # this will be an array of dictionaries
    print("Analyzing spending on top categories for date binned transactions")
    i = 0
    for trans in date_bin_trans:
        print("\n\n")
        top_cat_str, amounts = anah.create_top_category_amounts_array(trans, categories, count_NA=False)

        # do some post-processing on top-level categories and amounts
        top_cat_str, amounts = grah.strip_non_expense_categories(top_cat_str, amounts)

        # append dict to an array of all date ranges
        date_bin_dict_arr.append(
            {"date_range": edge_codes[i] + " to " + edge_codes[i + 1],
             "amounts": amounts,
             }
        )
        i += 1

    # print our created array
    pprint(date_bin_dict_arr)

    top_cat_dict = {}
    for cat_str in top_cat_str:
        top_cat_dict[cat_str] = []

    x_ax = []
    for d_bin in date_bin_dict_arr:
        x_ax.append(d_bin["date_range"])
        i = 0
        for amount in d_bin["amounts"]:
            amount = -1 * amount
            top_cat_dict[top_cat_str[i]].append(amount)
            i += 1

    pprint(top_cat_dict)

    # populate array of y axis values (needed for graphing_analyzer function)
    y_axis_arr = []
    for cat_str in top_cat_str:
        y_axis_arr.append(top_cat_dict[cat_str])

    # set up graphing stuff
    grapa.create_mul_line_chart(x_ax,
                                y_axis_arr,
                                title="ExB 01: Top categories across time",
                                labels=top_cat_str,
                                rotate_labels=True,
                                legend=True,
                                y_format='currency')


# TODO: the order of this is not intuitive (oldest appears on far right)
# TODO: this is simply the above executive summary with a different array of binned transactions. COMBINE
# exec_summary_01b: produces graph of previous month ranges
def exec_summary_01b(months_prev):
    # populate array of date-binned transaction arrays
    date_bin_trans = []
    labels = []
    [year, month, day] = dateh.get_date_int_array()
    for i in range(0, months_prev):
        date_bin_trans.append(transr.recall_transaction_month_bin(year, month))
        labels.append(f"{year}-{month}")
        month -= 1
        if month < 1: # handle new year wraparound
            month = 12
            year -= 1

    # perform analysis to sum
    logger.debug("Analyzing spending on top categories for date binned transactions")
    date_bin_dict_arr = anah.gen_bin_analysis_dict(date_bin_trans) # TODO: audit that I'm reusing this function in other exec summaries

    # do even more analysis?
    top_cat_str = date_bin_dict_arr[0]["categories"]
    top_cat_dict = {}
    for cat_str in top_cat_str:
        top_cat_dict[cat_str] = []
    for d_bin in date_bin_dict_arr:
        i = 0
        for amount in d_bin["amounts"]:
            amount = -1 * amount
            top_cat_dict[top_cat_str[i]].append(amount)
            i += 1

    # SET UP Y-AXIS
    y_axis_arr = []
    for cat_str in top_cat_str:
        y_axis_arr.append(top_cat_dict[cat_str])

    # set up graphing stuff
    grapa.create_mul_line_chart(labels,
                                y_axis_arr,
                                title=f"ExS 01b: Top categories across previous {months_prev} months",
                                labels=top_cat_str,
                                rotate_labels=True,
                                legend=True,
                                y_format='currency')


# exec_summary_02:
# TODO: to allow for 'comp_month_prev' to be > 12 I can use the mod % operator on it and then subtract from year
# TODO: this function really does not work. The percents are always like equal to 100%
# @brief 02 of my analysis spending history
# @desc this function will compare the previous month to some predetermined date range of previous month spending
# @param    comp_month_prev    this variable will determine how many months back to use as comparison "baseline"
def exec_summary_02(comp_month_prev):
    logger.info("\n\n\n... comparing previous month spending to running averages ...")

    # STEP 1: get transactions from previous month
    cur_date_arr = dateh.get_date_int_array()
    prev_year = cur_date_arr[0]  # index 0 dateh.get_date_int_array() is YEAR
    prev_month = cur_date_arr[1] - 1  # index 1 of dateh.get_date_int_array() is MONTH then less 1 for PREV MONTH
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    prev_month_trans = transr.recall_transaction_month_bin(prev_year, prev_month)
    logger.info(f"Done retrieving transactions from previous month\n\t {prev_year}-{prev_month}")

    # STEP 2: get transactions from baseline data (before previous month)
    # TODO: step 2 logic could really be simplified. I need some nice date functions to handle this logic
    baseline_month_start = prev_month - comp_month_prev
    baseline_month_end = prev_month - 1
    prev_year_start = prev_year
    prev_year_end = cur_date_arr[0]
    if baseline_month_start < 1:
        baseline_month_start += 12
        prev_year_start -= 1
    if baseline_month_end < 1:
        baseline_month_end = 12
        prev_year_end -= 1
    baseline_range_start = dateh.month_year_to_date_range(
        prev_year_start,
        baseline_month_start
    )
    baseline_range_end = dateh.month_year_to_date_range(
        prev_year_end,
        baseline_month_end
    )
    baseline_trans = transr.recall_transaction_data(
        baseline_range_start[0],
        baseline_range_end[1],
    )
    logger.info(f"Done retrieving transactions from baseline\n\t {baseline_range_start[0]} TO {baseline_range_end[1]}")

    # STEP 3: extract totals and make comparison
    top_cat_str, prev_amounts = anah.create_top_category_amounts_array(prev_month_trans,
                                                                       cath.load_categories(),
                                                                       count_NA=False)
    top_cat_str, baseline_amounts = anah.create_top_category_amounts_array(baseline_trans,
                                                                           cath.load_categories(),
                                                                           count_NA=False)

    # do some division on baseline to "normalize" it
    baseline_amounts = [x / comp_month_prev for x in baseline_amounts]
    percent_diffs = []
    for i in range(0, len(prev_amounts)):
        if baseline_amounts[i] == 0:
            delta = -1
        else:
            delta = prev_amounts[i] / baseline_amounts[i]
            delta = delta - 1
            delta = delta * 100
        percent_diffs.append(delta)

        # do some printout
        print(f"\t{top_cat_str[i]}\n\t\tDelta: {delta} %\n\t\t{baseline_amounts[i]} vs. {prev_amounts[i]}")

    title = f"ExS 02: Delta from past {comp_month_prev} months"
    grapa.create_bar_chart(
        top_cat_str,
        percent_diffs,
        xlabel="% difference",
        title=title)


def search_01():
    search_str = clih.spinput("\nWhat is the keyword you want to search for in transaction description?",
                              "text")
    transactions = transr.recall_transaction_desc_keyword(search_str)
    return transactions


def search_02():
    # determine user choice of type of category search
    cat_search_type = clih.prompt_num_options("What type of category search?",
                                              ["recursive (children)", "individual"])
    cat_search_type = 2 # tag:HARDCODE

    if cat_search_type == 1:
        search_str = clih.category_tree_prompt()
        children_id = cath.get_category_children(search_str)
        transactions = transr.recall_transaction_category(search_str)
        for child_id in children_id:
            transactions.extend(transr.recall_transaction_category(child_id))
    elif cat_search_type == 2:
        search_str = clih.category_prompt_all("What is the category to search for?", False)
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


class TabSpendingHistory(SubMenu):
    def __init__(self, title, basefilepath):

        self.basefilepath = basefilepath  # had to add this in, at some point maybe delete?

        # initialize information about sub menu options
        action_arr = [Action("Executive summary", self.a01_exec_summary),
                      Action("Print database transactions", self.a02_print_db_trans),
                      Action("Search transactions", self.a03_search_trans),
                      Action("Graph category data", self.a04_graph_category),
                      Action("Generate sankey (not working)", self.a05_make_sankey),
                      Action("Review specific month transactions", self.a06_review_month),
                      Action("Add note to transaction", self.a07_add_note),
                      Action("Update transaction category", self.a08_update_transaction_category),
                      Action("Examine specific category", self.a09_examine_category)
                      ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

    # a01_exec_summary: creates a list of "executive summary items" about spending data
    def a01_exec_summary(self):
        months_prev = clih.spinput("How many months previous would you like to examine?", inp_type="int")

        # clear tmp folder
        logh.clear_tmp_folder()

        # EXEC 1: plot data from previous timeframe
        exec_summary_01(
            months_prev * 30,  # number of days previous
            6)  # number of bins (N)

        # EXEC 1b: plot data from previous N months
        exec_summary_01b(months_prev)

        # EXEC 2: current categories with a big delta to past averages
        exec_summary_02(months_prev)

        # EXEC 3: get gross stats
        today = dateh.get_cur_str_date()
        days_ago = dateh.get_date_previous(months_prev * 30)
        transactions = transr.recall_transaction_data(days_ago, today)
        ledger_stats = anah.return_ledger_exec_dict(transactions)
        print(
            f"\nGot this for ledger statistics for past {months_prev} months\n\tor {days_ago.strftime('%d')} days ago\n")
        clip.print_dict(ledger_stats)

        # generate pdf file AND open
        print("\nGenerating .pdf ...")
        image_folder = "tmp"
        output_pdf = "tmp/spending_document.pdf"
        logh.generate_summary_pdf(image_folder, output_pdf)

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


    # TODO: add filtering of multiple options at once (description and amount amount < M, date would be super nice, etc)
    # a03_search_trans: performs a search of transaction database
    def a03_search_trans(self):
        print("... searching transactions ...")

        # get input on what type of search to do
        search_options = ["DESCRIPTION", "CATEGORY", "DATE", "ACCOUNT"]
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
        else:
            print(f"Can't perform search with search type of: {search_type}")
            return False

        # form Ledger, print, and return executive summary
        tmp_ledger = Ledger.Ledger(f"Transactions with for search type {search_type}")
        tmp_ledger.set_statement_data(transactions)
        tmp_ledger.print_statement(include_sql_key=True)

        # TODO: add some "enter statement" CLI hook here where I can perform my normal search functions.

        ledger_exec = anah.return_ledger_exec_dict(transactions)
        print("\n")
        pprint(ledger_exec)
        # TODO: DEVIATION from returning boolean. How to handle? Sub helper function for the actual search probably?
        return transactions


    # a04_graph_category: walks user through producing a graph of a certain category
    def a04_graph_category(self):
        # get category ID
        category_id = clih.category_prompt_all("What is the category to graph?", False)
        if category_id is None or 0:
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
        month = clih.get_month_input()

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


# TODO: these category things should move to section 7 on transaction categorization

    # TODO: this thing really needs to print out what transactions you are updating the category for
    def a08_update_transaction_category(self):
        print(" ... updating transaction categories ...")

        # get input on what type of search to do
        search_options = ["SEARCH", "MANUAL"]
        search_type = clih.prompt_num_options("How do you want to procure sql key to update?: ",
                                              search_options)
        if search_type is False:
            print("Ok, quitting transaction update\n")
            return False

        found_sql_key = []
        if search_type == 1:
            found_transactions = self.a03_search_trans()
            if found_transactions is False:
                print("... and quitting update transactions category too !")

            # TODO: handle this case where only 1 transaction from the search is found more elegantly
            if len(found_transactions) > 1:
                for transaction in found_transactions:
                    found_sql_key.append(transaction.sql_key)
        elif search_type == 2:
            found_sql_key.append(clih.spinput("Please enter sql key to update: ", inp_type="int"))

        # TODO: structure of this function scares me, why am I doing all this stuff after the SQL keys are found?
        # prompt user to eliminate any transactions
        print(found_sql_key)
        status = True
        if search_type == 1:
            while status:
                # TODO: ensure this spinput handles "no input" as quit? Think about it.
                sql_to_remove = clih.spinput(
                    "\nNow can pick to remove transactions. Quit if not needed.\nPlease enter sql key of transaction to remove from update list: ",
                    "int")
                if sql_to_remove is False:
                    status = False
                else:
                    found_sql_key.remove(sql_to_remove)
                    # reprint updated list
                    print("\n")
                    for id_key in found_sql_key:
                        transaction = transr.get_transaction(id_key)
                        transaction.printTransaction(include_sql_key=True)

        if len(found_sql_key) == 0:
            print("No transaction left to update. Quitting")
            return False

        # prompt user to get new category ID
        new_category_id = clih.category_prompt_all(
            "What is the new category for this grouping of transactions?",
            False)  # display = False

        # iterate through final list of keys and update their category ID
        for key in found_sql_key:
            dbh.transactions.update_transaction_category_k(
                key,
                new_category_id)

    def a09_examine_category(self):
        category_id = clih.category_prompt_all("What is the category to examine?", display=False)
        return False
