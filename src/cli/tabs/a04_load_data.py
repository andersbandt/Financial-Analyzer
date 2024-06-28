"""
@file a04_load_data.py
@brief sub menu for loading in raw financial data and storing in database

"""

# import needed packages
import csv

# import user defined modules
import cli.cli_helper as clih
from cli.cli_class import SubMenu
from cli.cli_class import Action

from categories import categories_helper
from tools import load_helper as loadh
from tools import date_helper as dateh


class TabLoadData(SubMenu):
    def __init__(self, title, basefilepath):

        self.statement = None
        # self.statement_list = None # NOTE: should I try to phase this thing out...?

        self.basefilepath = basefilepath # had to add this in, at some point maybe delete?

        # initialize information about sub menu options
        action_arr = [
            Action("Load data", self.a01_load_data),
            Action("Load ALL data", self.a02_load_all_data()),
            Action("Check data status", self.a03_categorize_statement)
        ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)


    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_load_data(self):
        print("... loading in financial data for certain year/month ...")

        [year, month] = clih.prompt_year_month()
        if month == -1 or year == -1:
            res = clih.promptYesNo("Bad date input. Try again?")
            if res:
                [year, month] = clih.prompt_year_month

        statement_list = loadh.get_month_year_statement_list(
            self.basefilepath,
            year,
            month,
            printmode=False)

        print(f"\nCreating master Statement object for all files in date bin {year}-{month}")
        self.statement = loadh.create_master_statement(statement_list) # TODO: I think I should have this be a Statement instead of a Ledger
        self.statement.print_statement()

        print("Statement loaded successfully, can continue with load process")
        self.update_listing()

    def a02_load_all_data(self):
        print("... loading in ALL financial data")

        statement_list = []
        year_range = dateh. get_valid_years()

        for year in year_range:
            for month in range(1, 12+1):
                tmp_list = loadh.get_month_year_statement_list(self.basefilepath, year, month)
                statement_list.extend(tmp_list)

        print("\t... finished creating all Statement objects in range")

        print("\nCreating master Ledger object")
        self.statement = loadh.create_master_ledger(statement_list)

        print("\t... done creating Ledger object.\n Updating listings and exiting.")
        self.update_listing()

    def a03_check_status(self):
        print("... checking data status ...")

########              ##########################              ########
#######  BELOW FUNCTIONS AVAILABLE AFTER STATEMENT IS LOADED IN ######
######################                          ######################

    # a03_categorize_statement: helps user categorize currently loaded statement data
    def a04_categorize_statement(self):
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
    def a05_save_statement_csv(self):
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
    def a06_print_ledger(self):
        print(" ... printing current Ledger object")
        self.statement.sort_date_desc()
        self.statement.print_statement()


    # a07_sort_ledger: sorts the ledger by some metric
    def a07_sort_ledger(self):
        print(" ... sorting Ledger object")
        # method = ["$ up", "$ down", "date up", "date down"]
        #  inp_auto(prompt, strings_arr, echo=True, stat=None)
        self.statement.sort_trans_asc()
        self.statement.print_statement()


    def a08_save_statement_db(self):
        print("... saving statement to .db file ...")
        self.statement.save_statement()

    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################

    def update_listing(self):
        # append new actions to menu now that statement is loaded in
        new_actions = [
            Action("Categorize statement", self.a04_categorize_statement),
            Action("Save to .csv", self.a05_save_statement_csv)
            Action("Print new Ledger", self.a06_print_ledger),
            Action("Sort ledger", self.a07_sort_ledger),
            Action("Save to database", self.a08_save_statement_db),
        ]

        self.actions.extend(new_actions)
        return True


    def categorize_automatic(self):
        pass



