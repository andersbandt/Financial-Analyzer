
# import needed packages
from datetime import datetime, timedelta
from pprint import pprint

# import user defined helper modules
import db.helpers as dbh
import categories.categories_helper as cath
from analysis import analyzer_helper as anah
from analysis import graphing_analyzer as grapa
from analysis import graphing_helper as grah
from analysis.data_recall import transaction_recall
from tools import date_helper as dateh

# import user defined modules
from cli.tabs import SubMenu
import cli.cli_helper as clih
from statement_types import Ledger


# TODO: lots
# this should be the main focus of my program. The other stuff is cool but I have the data in place now where I can really focus
# on the analysis. Ultimate customization.

# things like
# - % increase/decrease over selected date range vs previous period of x days
# - clickable categories to view list of transactions in categories for period of days
# - budgeting can easily be started now


class TabSpendingHistory(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):

        self.basefilepath = basefilepath  # had to add this in, at some point maybe delete?

        # initialize information about sub menu options
        action_strings = ["Executive summary",
                          "Print database transactions",
                          "Search transactions",
                          "Graph category data"]

        action_funcs = [self.a01_exec_summary,
                        self.a02_print_db_trans,
                        self.a03_search_trans,
                        self.a04_graph_category]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)

    # a01_exec_summary: creates a list of "executive summary items" about spending data
    def a01_exec_summary(self):
        print(" ... showing executive summary ...")

        # EXEC 1: plot data from previous timeframe
        self.exec_summary_01(
            800,  # number of days previous
            6)  # number of bins (N)

        # EXEC 2: current categories with a big delta to past averages
        self.exec_summary_02(6)

        # EXEC 3: get gross stats
        today = datetime.today()
        one_year_ago = today - timedelta(days=365)

        # LOAD IN TRANSACTIONS FROM 12 MONTHS AGO
        transactions = anah.recall_transaction_data(
            one_year_ago.strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d'))

        ledger_stats = anah.return_ledger_exec_dict(transactions)
        print("Got this for ledger statistics for past 12 months")
        print(ledger_stats)


#    a02_print_db_trans: prints EVERY transaction in ledger .db
    def a02_print_db_trans(self):
        transactions = anah.recall_transaction_data()
        tmp_ledger = Ledger.Ledger("All Statement Data")
        tmp_ledger.set_statement_data(transactions)
        tmp_ledger.print_statement()


    # a03_search_trans: performs a search of transaction database
    def a03_search_trans(self):
        print("... searching transactions ...")

        # get input on what type of search to do
        search_options = ["DESCRIPTION", "CATEGORY"]
        search_type = clih.prompt_num_options("What type of search do you want to perform?: ",
                                              search_options)
        if search_type is False:
            print("Ok, quitting transaction search.\n")
            return False

        # get transaction description keyword
        if search_type == 1:
            search_str = clih.spinput("\nWhat is the keyword you want to search for in transaction description? : ",
                                            "text")
            transactions = anah.recall_transaction_desc_keyword(search_str)
        elif search_type == 2:
            # determine user choice of type of category search
            cat_search_type = clih.prompt_num_options("What type of category search?: ",
                                                      ["recursive (children)", "individual"])
            if cat_search_type == 1:
                search_str = clih.category_prompt_all("What is the category to search for?: ", False)
                children_id = cath.get_category_children(search_str)
                transactions = transaction_recall.recall_transaction_category(search_str)
                for child_id in children_id:
                    transactions.extend(transaction_recall.recall_transaction_category(child_id))
            elif cat_search_type == 2:
                search_str = clih.category_prompt_all("What is the category to search for?: ", False)
                transactions = transaction_recall.recall_transaction_category(search_str)
            elif cat_search_type is False:
                print("Ok, quitting transaction search.\n")
                return False
            else:
                print(f"Uh oh, bad category search type of: {cat_search_type}")
                return False
        else:
            print(f"Can't perform search with search type of: {search_type}")
            return False

        # form Ledger, print, and return executive summary
        tmp_ledger = Ledger.Ledger(f"Transactions with for search type {search_type} with parameter {search_str}")
        tmp_ledger.set_statement_data(transactions)
        tmp_ledger.print_statement()

        ledger_exec = anah.return_ledger_exec_dict(transactions)
        print("\n")
        pprint(ledger_exec)


    # a04_graph_category: walks user through producing a graph of a certain category
    def a04_graph_category(self):
        # determine user choice of type of category graph
        cat_graph_type = clih.prompt_num_options("What type of category graph?",
                                                  ["recursive (children)", "individual"])

        if cat_graph_type == 1:
            pass
        if cat_graph_type == 2:
            category_id = clih.category_prompt_all("What is the category to graph?", False)
            transactions = transaction_recall.recall_transaction_category(category_id)

        months_prev = 12
        month_totals = anah.month_bin_transaction_total(transactions, months_prev)
        months = [i for i in range(0, months_prev+1)]
        months.reverse()
        grapa.create_bar_chart(months,
                               month_totals,
                               xlabel="Months previous",
                               title=f"Graph of category {cath.category_id_to_name(category_id)}")


    def a05_make_sankey(self):
        pass


    ##############################################################################
    ####      GENERAL HELPER FUNCTIONS    ########################################
    ##############################################################################

    # exec_summary_01: produces a graph of the top-level categories over time
    def exec_summary_01(self, days_prev, num_slices):
        # LOAD CATEGORIES
        categories = cath.load_categories()

        # get transactions between certain "edge codes"
        date_bin_trans, edge_codes = anah.sum_date_binned_transaction(days_prev,  # number of previous days
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
                {"date_range": edge_codes[i] + " to " + edge_codes[ i +1],
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
        print("... comparing previous month spending to running averages ...")

        # STEP 1: get transactions from previous month
        cur_date_arr = dateh.get_date_int_array()
        prev_year = cur_date_arr[0] # index 0 dateh.get_date_int_array() is YEAR
        prev_month = cur_date_arr[1] - 1  # index 1 of dateh.get_date_int_array() is MONTH then less 1 for PREV MONTH
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1
        prev_month_range = dateh.month_year_to_date_range(
            prev_year,
            prev_month
        )

        prev_month_trans = anah.recall_transaction_data(
            prev_month_range[0],
            prev_month_range[1],
        )

        # STEP 2: get transactions from baseline data (before previous month)
        baseline_month_start = prev_month - comp_month_prev
        baseline_month_end = prev_month - 1
        if baseline_month_start < 1:
            baseline_month_start += 13
            prev_year -= 1
        if baseline_month_end < 1:
            baseline_month_end = 12
            prev_year -= 1
        baseline_range_start = dateh.month_year_to_date_range(
            prev_year,
            baseline_month_start
        )
        baseline_range_end = dateh.month_year_to_date_range(
            prev_year,
            baseline_month_end
        )

        baseline_trans = anah.recall_transaction_data(
            baseline_range_start[0],
            baseline_range_end[1],
        )

        print(f"Done retrieving transactions from previous month\n\t {prev_month_range[0]} TO {prev_month_range[1]}")
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
            print(f"\t{top_cat_str[i]}\n\t\t{delta}\n\t\t{baseline_amounts[i]} vs. {prev_amounts[i]}")

        title = f"Delta from past {comp_month_prev} months"
        grapa.create_bar_chart(
            top_cat_str,
            percent_diffs,
            xlabel="% difference",
            title=title)

