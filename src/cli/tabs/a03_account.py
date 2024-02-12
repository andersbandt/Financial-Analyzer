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
from account import account_helper as ah
from tools import load_helper as loadh
import db.helpers as dbh


class TabAccount(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_strings = ["Check accounts", "Add account"]
        action_funcs = [self.a01_check_accounts, self.a02_add_account]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)


    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_check_accounts(self):
        print("... checking accounts ...")
        for name in dbh.account.get_account_names():
            print("Account: " + name)
        return True


    def a02_add_account(self):
        print("... adding accounts ...")

        # get account information
        name = clih.spinput("What is the name of this account?: ", inp_type="text")

        # print out account type classification breakdown
        for j in range(1, ah.get_num_acc_type()+1):
            print("\t" + str(j) + "= " + ah.get_acc_type_mapping(j))

        type_int = clih.spinput("What is the type of this account ?? (please enter INTEGER): ", inp_type="int")
        if type_int == -1:
            print("Bad int received. Won't insert account")
            return False
        if type_int > ah.get_num_acc_type():
            print("Int greater than predetermined account types. Won't insert account.")

        # get retirement status
        # TODO: finish this to get retirement status for the account. Possibly only enter this if investment account?

        # insert the investment into the database
        account_id = dbh.account.insert_account(name, type_int)

        print("Inserted account - " + name + " with account_id of (" + str(account_id) + ")")


    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################


