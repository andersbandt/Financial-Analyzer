
# import needed packages
from functools import partial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

# import user defined helper modules
import categories.categories_helper as category_helper
from analysis import analyzer_helper, graphing_analyzer
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
                          "Print database transactions",
                          "Show top level pie"]

        action_funcs = [self.a01_exec_summary,
                        self.a02_print_db_trans,
                        self.show_top_pie_chart]


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
        transactions = analyzer_helper.recall_transaction_data(
            one_year_ago.strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d'),
            accounts)

        if transactions is None:
            print("ERROR: analyze_history: Recalled 0 transactions. Exiting")
            raise Exception("Can't analyze history. Invalid transaction data recalled.")


        # EXEC 1: total spending trend month to month for the last 12 months
        sum_trans_data = analyzer_helper.sum_date_binned_transaction(transactions, 365, 12)

        # EXEC 2: current categories with a big delta to past averages

        # get gross statistics
        ledger_stats = analyzer_helper.return_ledger_exec_dict(transactions)
        print("Got this for ledger statistics")
        print(ledger_stats)



    def a02_print_db_trans(self):
        transactions = analyzer_helper.recall_transaction_data()

        tmp_ledger = Ledger.Ledger("All StatementData")
        tmp_ledger.set_statement_data(transactions)

        tmp_ledger.print_statement()


    # show_pie_chart: shows a pie chart of all category and amount data in current loaded Ledger
    def show_pie_chart(self):
        # check for data load status and error handle
        self.check_data_load_status()
        # get pyplot figure, patches, and texts
        figure, categories, amounts = graphing_analyzer.create_pie_chart(
            self.transactions, category_helper.load_categories(), printmode="debug"
        )
        figure.show()


    # TODO: normalize and report as percent
    def show_top_pie_chart(self):
        # check for data load status and error handle
        self.check_data_load_status()
        # get pyplot figure
        figure = graphing_analyzer.create_top_pie_chart(
            self.ledger.transactions, category_helper.load_categories()
        )
        figure.show()



    def show_budget_diff_chart(self):
        # check for data load status and error handle
        self.check_data_load_status()

        # get pyplot figure
        figure = graphing_analyzer.create_top_pie_chart(
            self.transactions, category_helper.load_categories()
        )
        canvas = FigureCanvasTkAgg(figure, self.fr_graph_proc)
        canvas.get_tk_widget().grid(row=2, column=0)



    ##############################################################################
    ####      GENERAL HELPER FUNCTIONS    ########################################
    ##############################################################################


