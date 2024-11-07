"""
@file a04_load_data.py
@brief sub menu for loading in raw financial data and storing in database

"""

# import needed packages
import csv
import time

# import user defined CLI modules
import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.cli_class import SubMenu
from cli.cli_class import Action

# import user defined helper modules
from statement_types.Transaction import Transaction
from categories import categories_helper
from account import account_helper as acch
from tools import load_helper as loadh
import db.helpers as dbh
from tools import date_helper as dateh


# TODO: I need to add a function to parse ALL folders and conduct an analysis on potential months with missing data

class TabLoadData(SubMenu):
    def __init__(self, title, basefilepath):

        self.statement = None
        self.basefilepath = basefilepath  # had to add this in, at some point maybe delete?
        self.updated = False

        # initialize information about sub menu options
        action_arr = [
            Action("Load data", self.a01_load_data),
            Action("Load ALL data", self.a02_load_all_data),
            Action("Add manual transaction", self.a03_add_manual_transaction),
            Action("Check data status", self.a04_check_status)
        ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)


    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_load_data(self):
        print("... loading in financial data for certain year/month ...")

        # I was feeling pretty high and weird writing below code so maybe give it an audit on efficacy
        try:
            [year, month] = clih.prompt_year_month()
        except TypeError:
            res = clih.promptYesNo("Bad date input. Try again?")
            if res:
                [year, month] = clih.prompt_year_month()
            else:
                return False

        # create list of Statement objects for each file for the particular month/year combination
        statement_list = loadh.get_month_year_statement_list(
            self.basefilepath,
            year,
            month,
            printmode=False)

        print(f"\nCreating master Statement object for all files in date bin {year}-{month}")
        self.statement = loadh.join_statement(statement_list)
        self.statement.print_statement()

        print("Statement loaded successfully, can continue with load process")
        self.update_listing()
        return True


    def a02_load_all_data(self):
        print("... loading in ALL financial data")
        statement_list = []
        year_range = dateh.get_valid_years()

        for year in year_range:
            for month in range(1, 12 + 1):
                tmp_list = loadh.get_month_year_statement_list(self.basefilepath, year, month)
                statement_list.extend(tmp_list)

        print("\t... finished creating all Statement objects in range")
        print("\nCreating master Ledger object")
        self.statement = loadh.join_statement(statement_list)

        print("\t... done creating Ledger object.\n Updating listings and exiting.")
        self.update_listing()


    def a03_add_manual_transaction(self):
        print("... attempting to manually load in a transaction. Kinda scary. Don't mess up.")

        # get account information
        account_id = clih.account_prompt_all("What is the account for this one-time transaction?")
        time.sleep(0.2)
        if account_id is False or account_id is None:
            return False

        # get description
        description = clih.spinput("What is the transaction description?: ", "text")
        time.sleep(0.2)

        # get amount
        amount = clih.spinput("What is the transaction amount?: ", "float")
        time.sleep(0.2)
        if amount is False or amount is None:
            return False

        # get category information
        category_id = clih.category_prompt_all("What is the category to search for?: ", False)
        time.sleep(0.2)
        if category_id is False or category_id is None:
            return False

        # prompt user for date
        trans_date = clih.get_date_input("\nand what date is this balance record for?: ")
        time.sleep(0.2)
        if trans_date is False or trans_date is None:
            return False

        # create transaction
        transaction = Transaction(trans_date, account_id, category_id, amount, description, note="MANUALLY ADDED")

        # INSERT TRANSACTION
        success = dbh.ledger.insert_transaction(transaction)
        return success


    # TODO: don't have this function parse investment accounts. Lots of bloat in the final table
    def a04_check_status(self):
        print("... checking data status ...")

        # set up information on which account(s) we are interested in
        # account_id = clih.get_account_id_manual() # METHOD 1: individual account
        acc_id_arr = acch.get_all_acc_id()

        # loop through month/year combos
        acc_data_status = []
        for year in dateh.get_valid_years():
            for month in range(1, 12+1):
                statement_arr = loadh.get_month_year_statement_list(
                    self.basefilepath,
                    year,
                    month,
                    printmode=False)
                if len(statement_arr) > 0:
                    for statement in statement_arr:
                        tmp_month_status = [f"{year}-{month}"]
                        for acc_id in acc_id_arr:
                            if statement.account_id == acc_id:
                                tmp_month_status.append("1")
                            else:
                                tmp_month_status.append("0")
                        acc_data_status.append(tmp_month_status)

        field_names = ["Month"]
        for acc_id in acc_id_arr:
            field_names.append(dbh.account.get_account_name_from_id(acc_id))
        clip.print_variable_table(field_names, acc_data_status, min_width=5, max_width=5, max_width_column=5)

        # TODO: add other checking mechanism for checking loaded files against actual data in .db

########              ##########################              ########
#######  BELOW FUNCTIONS AVAILABLE AFTER STATEMENT IS LOADED IN ######
######################                          ######################

    # a03_categorize_statement: helps user categorize currently loaded statement data
    def a05_categorize_statement(self):
        print("\n\na03: Automatically categorizing Statement")
        categories = categories_helper.load_categories()

        self.statement.categorizeLedgerAutomatic(categories)
        self.statement.print_statement()

        res = clih.promptYesNo("Do you want to attempt manual categorization of remaining transactions?")
        if res:

            self.statement.categorize_manual()
        else:
            print("Ok, leaving statement with just automatic categorization applied")

    # a05_save_statement_csv: saves the currently loaded statement to a .csv file
    def a06_save_statement_csv(self):
        print("... saving statement to .csv")
        try:
            # open the file
            # utf-8-sig is used as it includes a Byte Order Mark that helps programs recognize the file as UTF-8
            with open('C:/Users/ander/Downloads/test.csv', 'w', encoding='utf-8-sig', newline='') as f:
                csv_writer = csv.writer(f)
                # csv_writer = csv.writer(f, dialect='excel-tab')

                # write headers
                csv_writer.writerow(["Date", "Amount", "Description", "Category", "Source"])

                # iterate through all transactions
                if self.statement.transactions is not None:
                    for transaction in self.statement.transactions:
                        string_dict = transaction.getStringDict()

                        # write the row
                        csv_writer.writerow([
                            string_dict['date'],
                            string_dict['amount'],
                            string_dict['description'],
                            string_dict['category'],
                            string_dict['source']])
        except Exception as e:
            print("Can't save statement: ", e)

    # a06_print_ledger: prints the currently loaded ledger
    def a07_print_ledger(self):
        print(" ... printing current Ledger object")
        self.statement.sort_date_desc()
        self.statement.print_statement()

    # TODO: either split out into 1-amount or 2-date or add some user input on sorting method in here
    # a07_sort_ledger: sorts the ledger by some metric
    def a08_sort_ledger(self):
        print(" ... sorting Ledger object")
        # method = ["$ up", "$ down", "date up", "date down"]
        #  inp_auto(prompt, strings_arr, echo=True, stat=None)
        self.statement.sort_trans_asc()
        self.statement.print_statement()

    def a09_save_statement_db(self):
        print("... saving statement to .db file ...")
        status = self.statement.save_statement() # TODO: whatever is called here. I think it actually saves before prompting user
        return status

    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################

# TODO: if you load multiple statements in the same session, this list will grow arbitrarily long
    def update_listing(self):
        # append new actions to menu now that statement is loaded in
        new_actions = [
            Action("Categorize statement", self.a05_categorize_statement),
            Action("Save to .csv", self.a06_save_statement_csv),
            Action("Print new Ledger", self.a07_print_ledger),
            Action("Sort ledger", self.a08_sort_ledger),
            Action("Save to database", self.a09_save_statement_db),
        ]

        self.action_arr.extend(new_actions)
        self.updated = True
        return True

