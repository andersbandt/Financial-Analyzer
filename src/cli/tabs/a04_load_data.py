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

# import needed GUI modules
import tkinter as tk
from tkinter import filedialog

# import user defined helper modules
from statement_types.Transaction import Transaction
from categories import categories_helper
from account import account_helper as acch
from tools import load_helper as loadh
import db.helpers as dbh
from tools import date_helper as dateh


class TabLoadData(SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None
        self.basefilepath = basefilepath  # had to add this in, at some point maybe delete?
        self.updated = False

        # initialize information about sub menu options
        action_arr = [
            Action("Load data", self.a01_load_data),
            Action("Load ALL data", self.a02_load_all_data),
            Action("Load single file", self.a03_load_single_file),
            Action("Add manual transaction", self.a04_add_manual_transaction),
            Action("Check data status", self.a05_check_status)
        ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_load_data(self):
        print("... loading in financial data for certain year/month ...")

        # get month / year combination to examine in
        [year, month] = clih.prompt_year_month()

        # create list of Statement objects for each file for the particular month/year combination
        statement_list = loadh.get_month_year_statement_list(
            self.basefilepath,
            year,
            month,
            printmode=False)

        print(f"\nCreating master Statement object for all files in date bin {year}-{month}")
        self.statement = loadh.join_statement(statement_list)
        self.statement.print_statement()

        # TODO: finish fleshing out implementatino for auto-loading some preset monthly expense (like gym from income paycheck)
        # retrieve Transaction object based on preset sql
        # transaction = None
        # transaction.date = f"{year}-{month}-01"
        # create complementary income expense
        # income_trans = transaction
        # income_trans.category_id = None

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

    def a03_load_single_file(self):
        # Create a Tkinter root window and hide it
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        # Open a file dialog and prompt the user to select a file
        file_path = filedialog.askopenfilename(title="Select a file")

        # Return the selected file path
        if file_path:
            print(f"Selected file: {file_path}")
            return file_path
        else:
            print("No file selected.")
            return None

    def a04_add_manual_transaction(self):
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
    # TODO: add other checking mechanism for checking loaded files against actual data in .db
    def a05_check_status(self):
        print("... checking data status ...")

        # set up information on which account(s) we are interested in
        # account_id = clih.get_account_id_manual() # METHOD 1: individual account
        acc_id_arr = acch.get_all_acc_id()

        # loop through month/year combos
        acc_data_status = []
        for year in dateh.get_valid_years():
            for month in range(1, 12 + 1):
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

    ########              ##########################              ########
    #######  BELOW FUNCTIONS AVAILABLE AFTER STATEMENT IS LOADED IN ######
    ######################                          ######################

    # a03_categorize_statement: helps user categorize currently loaded statement data
    def a06_categorize_statement(self):
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
    def a07_save_statement_csv(self):
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
    def a08_print_ledger(self):
        print(" ... printing current Ledger object")
        self.statement.sort_date_desc()
        self.statement.print_statement()

    # a07_sort_ledger: sorts the ledger by some metric
    def a09_sort_ledger(self):
        print(" ... sorting Ledger object")
        strings_arr = ["$ up", "$ down", "date up", "date down"]
        method = clih.inp_auto("Enter sorting method", strings_arr, echo=True)

        if method == strings_arr[0]:
            self.statement.sort_trans_asc()
        elif method == strings_arr[1]:
            self.statement.sort_trans_desc()
        elif method == strings_arr[2]:
            self.statement.sort_date_asc()
        elif method == strings_arr[3]:
            self.statement.sort_date_desc()
        else:
            return False

        # re-print the statement
        self.statement.print_statement()
        return True

    def a10_save_statement_db(self):
        print("... saving statement to .db file ...")
        res = clih.promptYesNo("Are you sure you want to save the statement?")
        if res:
            status = self.statement.save_statement()
            return status
        else:
            return False

    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################

    def update_listing(self):
        if self.updated == False:
            # append new actions to menu now that statement is loaded in
            new_actions = [
                Action("Categorize statement", self.a06_categorize_statement),
                Action("Save to .csv", self.a07_save_statement_csv),
                Action("Print new Ledger", self.a08_print_ledger),
                Action("Sort ledger", self.a09_sort_ledger),
                Action("Save to database", self.a10_save_statement_db),
            ]
            self.action_arr.extend(new_actions)
            self.updated = True
            return True
        else:
            return False

