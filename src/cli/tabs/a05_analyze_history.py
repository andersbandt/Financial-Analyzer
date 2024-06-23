"""
@file a05_analyze_history.py
@brief sub menu for performing ANALYSIS on financial data

"""


# import needed packages
from datetime import datetime, timedelta
from pprint import pprint

# import user defined helper modules
import db.helpers as dbh
import categories.categories_helper as cath
from analysis import analyzer_helper as anah
from analysis import graphing_analyzer as grapa
from analysis import graphing_helper as grah
from analysis.data_recall import transaction_recall as transr
from tools import date_helper as dateh

# import user defined modules
from cli.tabs import SubMenu
import cli.cli_helper as clih
from statement_types import Ledger



class TabSpendingHistory(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):

        self.basefilepath = basefilepath  # had to add this in, at some point maybe delete?

        # initialize information about sub menu options
        action_strings = ["Executive summary",
                          "Print database transactions",
                          "Search transactions",
                          "Graph category data",
                          "Generate sankey (not working)",
                          "Review specific month transactions",
                          "Add note to transaction",
                          "Update transaction category"]

        action_funcs = [self.a01_exec_summary,
                        self.a02_print_db_trans,
                        self.a03_search_trans,
                        self.a04_graph_category,
                        self.a05_make_sankey,
                        self.a06_review_month,
                        self.a07_add_note,
                        self.a08_update_transaction_category]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)

    # a01_exec_summary: creates a list of "executive summary items" about spending data
    def a01_exec_summary(self):
        print(" ... showing executive summary ...")

        # EXEC 1: plot data from previous timeframe
        self.exec_summary_01(
            800,  # number of days previous
            6)  # number of bins (N)

        # EXEC 1b: plot data from previous N months
        self.exec_summary_01b(12)

        # EXEC 2: current categories with a big delta to past averages
        self.exec_summary_02(6)

        # EXEC 3: get gross stats
        today = datetime.today()
        one_year_ago = today - timedelta(days=365)

        # LOAD IN TRANSACTIONS FROM 12 MONTHS AGO
        transactions = transr.recall_transaction_data(
            one_year_ago.strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d'))

        ledger_stats = anah.return_ledger_exec_dict(transactions)
        print("Got this for ledger statistics for past 12 months")
        print(ledger_stats)

    #    a02_print_db_trans: prints EVERY transaction in ledger .db
    def a02_print_db_trans(self):
        transactions = transr.recall_transaction_data()
        tmp_ledger = Ledger.Ledger("All Statement Data")
        tmp_ledger.set_statement_data(transactions)
        tmp_ledger.sort_date_desc()
        tmp_ledger.print_statement(include_sql_key=True)


    # TODO: cleanup on this function (quite unruly)
    # TODO: add some options to do some things like running my Ledger sort functions on the output of search
    # TODO: add filtering of multiple options at once (description and amount amount < M, etc)
    # a03_search_trans: performs a search of transaction database
    def a03_search_trans(self):
        print("... searching transactions ...")

        # get input on what type of search to do
        search_options = ["DESCRIPTION", "CATEGORY", "DATE"]
        search_type = clih.prompt_num_options("What type of search do you want to perform?: ",
                                              search_options)
        if search_type is False:
            print("Ok, quitting transaction search.\n")
            return False

        # get transaction description keyword
        if search_type == 1:
            search_str = clih.spinput("\nWhat is the keyword you want to search for in transaction description? : ",
                                      "text")
            transactions = transr.recall_transaction_desc_keyword(search_str)
        elif search_type == 2:
            # determine user choice of type of category search
            cat_search_type = clih.prompt_num_options("What type of category search?: ",
                                                      ["recursive (children)", "individual"])
            if cat_search_type == 1:
                search_str = clih.category_tree_prompt()
                children_id = cath.get_category_children(search_str)
                transactions = transr.recall_transaction_category(search_str)
                for child_id in children_id:
                    transactions.extend(transr.recall_transaction_category(child_id))
            elif cat_search_type == 2:
                search_str = clih.category_prompt_all("What is the category to search for?: ", False)
                transactions = transr.recall_transaction_category(search_str)
            elif cat_search_type is False:
                print("Ok, quitting transaction search.\n")
                return False
            else:
                print(f"Uh oh, bad category search type of: {cat_search_type}")
                return False
        elif search_type == 3:
            start_date = clih.get_date_input("What is the start date of search range?")
            end_date = clih.get_date_input("What is the end date of search range?")
            if start_date is False or end_date is False:
                print("Ok, quitting transaction search.\n")
                return False
            transactions = transr.recall_transaction_data(start_date, end_date)
        else:
            print(f"Can't perform search with search type of: {search_type}")
            return False

        # form Ledger, print, and return executive summary
        tmp_ledger = Ledger.Ledger(f"Transactions with for search type {search_type}")
        tmp_ledger.set_statement_data(transactions)
        tmp_ledger.print_statement(include_sql_key=True)

        ledger_exec = anah.return_ledger_exec_dict(transactions)
        print("\n")
        pprint(ledger_exec)
        return True

    # a04_graph_category: walks user through producing a graph of a certain category
    def a04_graph_category(self):
        # determine user choice of type of category graph
        cat_graph_type = clih.prompt_num_options("What type of category graph?",
                                                 ["recursive (children)", "individual"])

        if cat_graph_type == 1:
            pass
        if cat_graph_type == 2:
            category_id = clih.category_prompt_all("What is the category to graph?", False)
            transactions = transr.recall_transaction_category(category_id)

        months_prev = 12
        month_totals = anah.month_bin_transaction_total(transactions, months_prev)
        months = [i for i in range(0, months_prev + 1)]
        months.reverse()
        grapa.create_bar_chart(months,
                               month_totals,
                               xlabel="Months previous",
                               title=f"Graph of category {cath.category_id_to_name(category_id)}")

    # TODO: Large task. Work on generating sankey diagram
    def a05_make_sankey(self):
        pass

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

        # TODO: add one last user check - print transaction and note and prompt yes no
        print(f"Confirming transaction update for item with sql_key={sql_key}")
        trans.note = note_str
        trans.printTransaction()

        print(f"\nNew note ---> {note_str}\n")

        res = clih.promptYesNo("Are you sure you want to change the transaction listed above?: ")
        if not res:
            print(f"Ok, not adding note to transaction with sql_key={sql_key}")
            return False
        else:
            # update note in database
            dbh.transactions.update_transaction_note_k(sql_key, note_str)
            return True

    def a08_update_transaction_category(self):
        print(" ... updating transaction categories ...")
        print("Commencing a03_search_trans !!!")

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

            for transaction in found_transactions:
                found_sql_key.append(transaction.sql_key)
        elif search_type == 2:
            found_sql_key.append(clih.spinput("Please enter sql key to update: ", inp_type="int"))

        # TODO: add some printing of transaction with sql_key in `found_sql_key`

        # prompt user to eliminate any transactions
        print(found_sql_key)
        status = True
        while status:
            sql_to_remove = clih.spinput(
                "\nPlease enter sql key of transaction to remove from update list (q to continue without removal): ", "int")
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

        # TODO: add final printout of transactions to be updated

        # iterate through final list of keys and update their category ID
        for key in found_sql_key:
            dbh.transactions.update_transaction_category_k(
                key,
                new_category_id)

    ##############################################################################
    ####      GENERAL HELPER FUNCTIONS    ########################################
    ##############################################################################

    # exec_summary_01: produces a graph of the top-level categories over time
    def exec_summary_01(self, days_prev, num_slices):
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
                                    title="Top categories across time",
                                    labels=top_cat_str,
                                    legend=True,
                                    y_format='currency')


# TODO: finish this function to produce a summary of per-month transactions. Try to be smart about code reuse with the function above and the one below
    # exec_summary_01b: produces graph of previous month ranges
    def exec_summary_01b(self, months_prev):
        # LOAD CATEGORIES
        categories = cath.load_categories()

        date_bin_trans = []
        [year, month, day] = dateh.get_date_int_array()
        for i in range(0, months_prev):
            date_bin_trans.append(transr.recall_transaction_month_bin(year, month))
            month -= 1
            if month < 1:
                month = 12
                year -= 1


        # TODO: I this this below for loop can become a helper function that can be reused
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
                # {"date_range": "m_start" + " to " + "m_end",
                {"date_range": i,
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
                                    title="Top categories across time",
                                    labels=top_cat_str,
                                    legend=True,
                                    y_format='currency')


    # exec_summary_02:
    # TODO: to allow for 'comp_month_prev' to be > 12 I can use the mod % operator on it and then subtract from year
    # @brief 02 of my analysis spending history
    # @desc this function will compare the previous month to some predetermined date range of previous month spending
    # @param    comp_month_prev    this variable will determine how many months back to use as comparison "baseline"
    def exec_summary_02(self, comp_month_prev):
        print("\n\n\n... comparing previous month spending to running averages ...")

        # STEP 1: get transactions from previous month
        # TODO: this date logic doesn't make sense
        cur_date_arr = dateh.get_date_int_array()
        prev_year = cur_date_arr[0]  # index 0 dateh.get_date_int_array() is YEAR
        prev_month = cur_date_arr[1] - 1  # index 1 of dateh.get_date_int_array() is MONTH then less 1 for PREV MONTH
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1

        prev_month_trans = transr.recall_transaction_month_bin(prev_year, prev_month)

        # STEP 2: get transactions from baseline data (before previous month)
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

        print(f"Done retrieving transactions from previous month\n\t {prev_year}-{prev_month}")
        print(f"Done retrieving transactions from baseline\n\t {baseline_range_start[0]} TO {baseline_range_end[1]}")

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

        title = f"Delta from past {comp_month_prev} months"
        grapa.create_bar_chart(
            top_cat_str,
            percent_diffs,
            xlabel="% difference",
            title=title)
