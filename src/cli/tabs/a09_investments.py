"""
@file a04_load_data.py
@brief sub menu for loading in raw financial data and storing in database



"""

# import needed packages
import os

# import user defined modules
from categories import categories_helper as cath
import cli.cli_helper as clih
from cli.tabs import SubMenu
from tools import load_helper as loadh
import db.helpers as dbh


class TabInvestment(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_strings = ["Check investments", "Add investment transaction"]
        action_funcs = [self.a01_check_investments, self.a02_add_investment]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)


    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_check_investments(self):
        print("... checking investment data ...")

        return True


    def a02_add_investment(self):
        print("... adding investment transaction ...")

        # get investment information
        account_id = clih.account_prompt_all("What is the corresponding account for this investment?")
        ticker = clih.spinput("What is the ticker of this investment?", type="text")
        shares = clih.spinput("What is the number of shares of this investment?", type="float")
        value = clih.spinput("What was the value of this investment for this transaction?")
        date = clih.get_date_input("What is the date of this investment transaction?")
        note = clih.spinput("Do you want to add a note to this transaction?", type="text")

        # insert the investment into the database
        dbh.investments.insert_investment(date, account_id, ticker, shares, inv_type, value, note=note)


    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################


