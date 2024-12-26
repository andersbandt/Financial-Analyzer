"""
@file a03_account.py
@brief sub menu for managing accounts


"""

# import user defined CLI modules
import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.cli_class import SubMenu
from cli.cli_class import Action

# impot user defined modules
from account import account_helper as acch
import db.helpers as dbh


class TabAccount(SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_arr = [
            Action("Print accounts", self.a01_print_accounts),
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

    def a01_print_accounts(self):
        print("... printing accounts ...")
        for name in dbh.account.get_account_names():
            print("Account: " + name)

        # print out raw SQl table
        accounts = dbh.account.get_account_ledger_data()
        clip.print_variable_table(["Account ID",
                                   "Name",
                                   "Institution name",
                                   "Type",
                                   "Balance",
                                   "Balance update date",
                                   "Savings goal",
                                   "Retirement ?"],
                                  accounts)

        return True

    def a02_add_account(self):
        print("... adding accounts ...")

        # get account information
        name = clih.spinput("What is the name of this account?: ", inp_type="text")

        # print out account type classification breakdown
        print("Account types below")
        for j in range(1, acch.get_num_acc_type() + 1):
            print(f"\t{j}= {acch.get_acc_type_mapping(j)}")

        type_int = clih.spinput("What is the type of this account ?? (please enter INTEGER): ", inp_type="int")
        if type_int == -1:
            print("Bad int received. Won't insert account")
            return False
        if type_int > acch.get_num_acc_type():
            print("Int greater than predetermined account types. Won't insert account.")

        # get retirement status
        if type_int == acch.types.INVESTMENT:
            retirement = clih.promptYesNo("Is this a retirement account?")
        else:
            retirement = False

        # insert the investment into the database
        account_id = acch.insert_account(name, type_int, retirement)

        print("Inserted account - " + name + " with account_id of (" + str(account_id) + ")")


    def a03_rename_account(self):
        account_id = clih.account_prompt_all("What account do you want to change the name for?")
        if account_id is False or account_id is None:
            return False

        # get new string
        new_name = clih.spinput("Please enter new name", inp_type="text")

        # set new name
        status = dbh.account.change_account_name(account_id, new_name)
        if not status:
            return False
        return True

    def a04_add_file_search_str(self):
        print("... adding accounts ...")

        # get account information
        account_id = clih.account_prompt_all("What account do you want to add a search string for?")
        if account_id is False or account_id is None:
            return False

        # what is the search string?
        search_str = clih.spinput("What is the search string required?", inp_type="text")

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
