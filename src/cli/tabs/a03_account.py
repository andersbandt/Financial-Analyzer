"""
@file a03_account.py
@brief sub menu for managing accounts


"""

# import user defined modules
import cli.cli_helper as clih
from cli.cli_class import SubMenu
from cli.cli_class import Action

from account import account_helper as ah
import db.helpers as dbh


class TabAccount(SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_arr = [
            Action("Check accounts", self.a01_check_accounts),
            Action("Add account", self.a02_add_account),
            Action("Rename account", self.a03_rename_account),
            Action("Add automatic file search string", self.a04_add_file_search_str),
            Action("Print account map", self.a05_print_account_file_map)
        ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    # TODO: this function could print out more info (account type, etc)
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
        for j in range(1, ah.get_num_acc_type() + 1):
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

    # TODO: finish this function to rename an account

    def a03_rename_account(self):
        pass

    def a04_add_file_search_str(self):
        print("... adding accounts ...")

        # get account information
        account_id = clih.account_prompt_all("What account do you want to add a search string for?")
        if account_id is False or account_id is None:
            return False

        # what is the search string?
        search_str = clih.spinput("What is the search string required?: ", inp_type="text")

        # insert the investment into the database
        data_id = dbh.file_mapping.insert_account_search_str(account_id, search_str)

        # print out success information
        print(f"Added a new file mapping with data id of : {data_id}")
        return True

    def a05_print_account_file_map(self):
        ledge_data = dbh.file_mapping.get_file_mapping_ledge_data()
        print(ledge_data)

    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################
