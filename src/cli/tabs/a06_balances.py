
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
        action_strings = ["Show executive wealth summary",
                          "Add balance",
                          "Show ALL wealth trends"]

        action_funcs = [self.a01_show_wealth,
                        self.a02_add_balance,
                        self.a03_show_stacked_liquid_investment]


        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    # a01_show_wealth
    def a01_show_wealth(self):
        balance_by_type = []

        # iterate across account types
        for acc_type in range(1, 4+1):
            acc_sum = 0
            acc_id_by_type = dbh.account.get_account_id_by_type(acc_type)

            for acc_id in acc_id_by_type:
                print("Checking acc_id: " + str(acc_id))
                bal = dbh.balance.get_recent_balance(acc_id)
                print("Got balance of " + str(bal))
                acc_sum += bal

            balance_by_type.append(acc_sum)

        print("Here is your recent balance history by account type")
        print(balance_by_type)


    # a02_add_balance: inserts data for an account balance record into the SQL database
    # TODO: add error checking for multiple balances per account on SAME day - on second thought is this needed?
    def a02_add_balance(self):
        print("... adding a balance entry ...")

        # prompt user for account ID
        account_id = clih.account_prompt_all("What account do you want to add balance to?")

        # prompt for balance amount
        bal_amount = clih.spinput("\nWhat is the amount for balance entry? (no $): ",
                                  inp_type="float")

        # prompt user for date
        bal_date = clih.get_date_input("\nand what date is this balance record for?")
        if bal_date is False:
            print("Ok, quitting add balance")
            return False

        # insert_category: inserts a category into the SQL database
        dbh.balance.insert_account_balance(account_id,
                                           bal_amount,
                                           bal_date)

        # print out balance addition confirmation
        print(f"Great, inserted a balance of {bal_amount} for account {account_id} on date {bal_date}")

        return True


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



