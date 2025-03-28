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
from categories import categories_helper as cath
from account import account_helper as acch
from tools import load_helper as loadh
import db.helpers as dbh
from tools import date_helper as dateh

# import logger
from loguru import logger


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

    # TODO: this thing doesn't do the file summary printout anymore :(
    def a01_load_data(self):
        print("... loading in financial data for certain year/month ...")

        # get month / year combination to examine in
        [year, month] = clih.prompt_year_month() # TODO: there is no check for valid year in this function

        # create list of Statement objects for each file for the particular month/year combination
        statement_list = loadh.get_month_year_statement_list(
            self.basefilepath,
            year,
            month,
            printmode=False)
        logger.debug(f"Statement list --> {statement_list}")
        logger.debug(f"Statement list has length {len(statement_list)}")

        # join statement list into one "master" statement
        self.statement = loadh.join_statement(statement_list)

        logger.debug(f"Final monthly statement has {len(self.statement.transactions)} transactions")

        # auto-add certain paycheck related deduction expenses
        if clih.promptYesNo("Do you want to add preset monthly expenses?"):
            # retrieve Transaction object based on preset sql
            date = dateh.month_year_to_date_range(year, month)[1]
            amount = 22
            transaction1 = Transaction(date, 2000000019, cath.category_name_to_id("HEALTH"), -1*amount, "Texins Gym", note="auto-loaded by month")
            transaction1c = Transaction(date,
                                        2000000019,
                                        cath.category_name_to_id("INCOME"),
                                        amount,
                                        "INCOME (Texins Gym)",
                                        note="auto-loaded by month (complementary income)"
                                        )
            self.statement.add_transaction(transaction1)
            self.statement.add_transaction(transaction1c)

        self.statement.print_statement()
        self.update_listing()
        return True

    def a02_load_all_data(self):
        print("... loading in ALL financial data")
        statement_list = []
        year_range = dateh.get_valid_years()

        for year in year_range:
            for month in range(1, 12 + 1):
                tmp_list = loadh.get_month_year_statement_list(self.basefilepath, year, month, printmode=True)
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
        if not file_path:
            return False

        self.statement = loadh.create_statement("dummy-year", "dummy-month", file_path, account_id_prompt=True)
        self.statement.print_statement()
        logger.info("Single statement file loaded successfully, can continue with load process")
        self.update_listing()

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

    def a05_check_status(self):
        print("... checking data status ...")

        # get user input on which method to use
        print("Two method for data integrity checking")
        print("METHOD 1: checks for presence of files on the system matching to certain accounts")
        print("METHOD 2: actually pulls data from files and sees if it exists in the database")
        method_num = clih.spinput("What type of data integrity method to use?", inp_type="int")

        # set up information on which account(s) we are interested in
        acc_id_arr = []
        acc_types = [acch.types.SAVING.value,
                     acch.types.CHECKING.value,
                     acch.types.CREDIT_CARD.value]
        for at in acc_types:
            acc_id_arr.extend(acch.get_account_id_by_type(at))

        if method_num == 1:
            self.check_data_integrity_01(acc_id_arr)
        elif method_num == 2:
            self.check_data_integrity_02(acc_id_arr)


    ########              ##########################              ########
    #######  BELOW FUNCTIONS AVAILABLE AFTER STATEMENT IS LOADED IN ######
    ######################                          ######################

    # a03_categorize_statement: helps user categorize currently loaded statement data
    def a06_categorize_statement(self):
        print("\n\na03: Automatically categorizing Statement")
        categories = cath.load_categories()

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

    # TODO: problems with this include 1-file name changes, 2-no actual detection of what is in database
    #   for example CreditCard3.csv became CreditCard4.csv halfway through my years
    def check_data_integrity_01(self, acc_id_arr):
        acc_data_status = []
        bad_months = {acc_id: [] for acc_id in acc_id_arr}  # To track BAD months per account

        # Loop through month/year combos
        for year in dateh.get_valid_years():
            for month in range(1, 12 + 1):
                # Get list of files in that directory
                month_year_dir = loadh.get_year_month_files(self.basefilepath, year, month)
                tmp_month_status = [f"{year}-{month}"]  # Populate first column with year-month

                for acc_id in acc_id_arr:
                    def find_account_match(aid):
                        for file in month_year_dir:
                            tmp_account_id = loadh.match_file_to_account(file)
                            if tmp_account_id == aid:
                                return True
                        return False

                    # Append if match was found or not
                    if find_account_match(acc_id):
                        tmp_month_status.append("1")
                    else:
                        tmp_month_status.append("0")

                acc_data_status.append(tmp_month_status)

        # Process the data to find "BAD" patterns
        for acc_idx, acc_id in enumerate(acc_id_arr, start=1):
            account_status = [row[acc_idx] for row in acc_data_status]  # Extract data for the account
            for i in range(1, len(account_status)):
                # Check for a 1 followed by a 0
                if account_status[i - 1] == "1" and account_status[i] == "0":
                    bad_months[acc_id].append(acc_data_status[i][0])  # Log the bad month (year-month)

        # Logging and displaying results
        field_names = ["Month"] + [dbh.account.get_account_name_from_id(acc_id) for acc_id in acc_id_arr]
        logger.debug(field_names)
        logger.debug(acc_data_status)
        clip.print_variable_table(field_names, acc_data_status, min_width=5, max_width=5, max_width_column=5)

        # Log BAD months
        for acc_id, months in bad_months.items():
            if months:
                logger.warning(f"Account ID {acch.account_id_to_name(acc_id)} has BAD months: {', '.join(months)}")
            else:
                logger.info(f"Account ID {acch.account_id_to_name(acc_id)} has no BAD months.")

        logger.info("CHECK PREVIOUS TABLE")
        logger.info("Showcasing if file match exists in valid folders")

        return True

    # TODO: lots of mismatches being flagged. Believe current issue is mismatch between month start/end search ranges
    def check_data_integrity_02(self, acc_id_arr):
        """
        Checks data integrity by comparing the total count of transactions in files
        with the total count of transactions in the database for each month/year/account_id combo.
        """
        # Initialize results dictionary
        integrity_results = {}

        # Loop through valid years
        for year in dateh.get_valid_years():
            # Loop through months in the year
            for month in range(1, 13):
                # Get list of statement objects for the month/year
                statements = loadh.get_month_year_statement_list(self.basefilepath, year, month, printmode=False)


                # loop through statements and compare to database
                for statement in statements:
                    # get amount of transactions in relevant, just-loaded statement
                    statement_transaction_count = len(statement.transactions)

                    # Fetch transaction count from the database
                    db_transaction_count = dbh.transactions.get_transaction_count(statement.account_id, year, month)

                    # Store results for comparison
                    integrity_results[(year, month, statement.account_id)] = {
                        "file_transactions": statement_transaction_count,
                        "db_transactions": db_transaction_count,
                        "matches": statement_transaction_count == db_transaction_count,
                    }

                    # Log comparison results
                    if statement_transaction_count != db_transaction_count:
                        logger.warning(
                            f"Mismatch for {year}-{month}, Account ID {acch.account_id_to_name(statement.account_id)}: "
                            f"File = {statement_transaction_count}, DB = {db_transaction_count}"
                        )
                    else:
                        logger.info(
                            f"Match for {year}-{month}, Account ID {acch.account_id_to_name(statement.account_id)}: "
                            f"File = {statement_transaction_count}, DB = {db_transaction_count}"
                        )


        # Return results for further processing or debugging
        return True

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

