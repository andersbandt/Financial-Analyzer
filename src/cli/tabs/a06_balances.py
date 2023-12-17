
# import needed packages


# import user defined modules
import db.helpers as dbh
from analysis import analyzer_helper, graphing_analyzer
from categories import categories_helper

import cli.cli_helper as clih
from cli.tabs import SubMenu
from tools import date_helper


# TODO: add some slots for tabular data
#   for example:
#       -latest balance record for each account along with date it was recorded on and type


class TabBalances(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):

        # initialize information about sub menu options
        action_strings = ["Add balance",
                          "Show current wealth",
                          "Show ALL wealth trends"]

        action_funcs = [self.a01_add_balance,
                        self.a02_show_wealth,
                        self.a03_show_stacked_liquid_investment]


        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    # a01_add_balance: inserts data for an account balance record into the SQL database
    # TODO: add error checking for multiple balances per account on SAME day
    def a01_add_balance(self):
        print("... adding a balance entry ...")

        # prompt user for account ID
        account_id = clih.account_prompt_all("What account do you want to add balance to?")

        # prompt for balance amount
        bal_amount = clih.spinput("What is the amount for balance entry? (no $): ", inp_type="int")

        # prompt user for date
        bal_date = clih.get_date_input("and what date is this balance record for?")

        # insert_category: inserts a category into the SQL database
        dbh.balance.insert_account_balance(account_id,
                                           bal_amount,
                                           bal_date)
        return True


    # a02_show_wealth
    def a02_show_wealth(self):


    # this function will be interesting to write.
    # I think I should keep a cumulative total of two balances - checkings/savings and investments
    # Then as I iterate across dates everytime there is a new entry I update that total and make a new record
    def a03_show_stacked_liquid_investment(self):
        print("... showing all liquid and investment assets")

        # set params
        days_previous = 180  # half a year maybe?
        N = 5

        # get pyplot figure
        figure = graphing_analyzer.create_stacked_balances(days_previous, N)

        # get data for displaying balances in tabular form
        spl_Bx = analyzer_helper.gen_Bx_matrix(days_previous, N)
        recent_Bx = spl_Bx[-1]

        print("Working with this for tabulated data conversion")
        print(recent_Bx)


    def show_liquid_over_time(self):
        print("INFO: show_liquid_over_time running")

        # set params
        days_previous = 180  # half a year maybe?
        N = 5

        # get pyplot figure
        figure = graphing_analyzer.create_liquid_over_time(days_previous, N)

        # get data for displaying balances in tabular form
        spl_Bx = analyzer_helper.gen_Bx_matrix(days_previous, N)
        recent_Bx = spl_Bx[-1]

        print("Working with this for tabulated data conversion")
        print(recent_Bx)



