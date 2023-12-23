# import needed packages
from functools import partial
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pprint import pprint

# import user defined helper modules
import categories.categories_helper as cath
from analysis import analyzer_helper as anah
from analysis import graphing_analyzer as grapa
from analysis import graphing_helper as grah
from tools import date_helper
from account import account_helper

# import user defined modules
import cli.cli_helper as clih
from cli.tabs import SubMenu
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
                          "Print database transactions"]

        action_funcs = [self.a01_exec_summary,
                        self.a02_print_db_trans]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)

    # a01_exec_summary:
    #   in order to speed up debug this function should just do a bunch of key careabouts
    def a01_exec_summary(self):
        print(" ... showing executive summary ...")

        # form Ledger with data from the past 12 months
        today = datetime.today()
        one_year_ago = today - timedelta(days=365)

        # error handle no accounts
        accounts = account_helper.get_all_account_ids()
        print("Got below for accounts")
        print(accounts)

        if len(accounts) == 0:
            print("Error with recalling data", "No accounts selected.", "error")

        # LOAD IN TRANSACTIONS FROM 12 MONTHS AGO
        transactions = anah.recall_transaction_data(
            one_year_ago.strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d'),
            accounts)

        if transactions is None:
            print("ERROR: analyze_history: Recalled 0 transactions. Exiting")
            raise Exception("Can't analyze history. Invalid transaction data recalled.")

        # EXEC 1: plot data from previous timeframe
        self.exec_summary_01(accounts,
                             800,  # number of days previous
                             6)  # number of bins (N)

        # EXEC 2: current categories with a big delta to past averages

        # get gross statistics
        ledger_stats = anah.return_ledger_exec_dict(transactions)
        print("Got this for ledger statistics")
        print(ledger_stats)

    def a02_print_db_trans(self):
        transactions = anah.recall_transaction_data()
        tmp_ledger = Ledger.Ledger("All StatementData")
        tmp_ledger.set_statement_data(transactions)
        tmp_ledger.print_statement()


    ##############################################################################
    ####      GENERAL HELPER FUNCTIONS    ########################################
    ##############################################################################

    def exec_summary_01(self, accounts, days_prev, num_slices):
        # LOAD CATEGORIES
        categories = cath.load_categories()

        # EXEC 1: total spending trend month to month for the last 12 months
        date_bin_trans, edge_codes = anah.sum_date_binned_transaction(accounts,  # a list of Transaction objects
                                                                      days_prev,  # number of previous days
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
                {"date_range": edge_codes[i] + " to " + edge_codes[i+1],
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

