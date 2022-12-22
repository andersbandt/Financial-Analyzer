# import needed modules
import tkinter as tk
from tkinter import ttk
from functools import partial

# import user defined modules
import statement_types.Ledger as Ledger
from gui import gui_helper
from categories import categories_helper
from db import db_helper


# TODO: make the 'update' button say 'save' for the Statement
class Statement(Ledger.Ledger):
    def __init__(self, master, account_id, year, month, file, row_num, column_num, *args, **kwargs):
        title = str(account_id) + ":" + str(year) + "-" + str(month)

        # call parent class __init__ method
        #super(Ledger.Ledger, self).__init__(master, title, row_num, column_num, *args, **kwargs)
        super().__init__(master, title, row_num, column_num, *args, **kwargs)

        # initialize identifying statement info
        self.account_id = account_id
        self.year = year
        self.month = month



        # # load in statement filepath info
        self.base_filepath = "C:/Users/ander/OneDrive/Documents/Financials"
        self.filepath = gui_helper.get_statement_folder(self.base_filepath, year, month) + file  # generate filepath of .csv file to download
        #
        # # initialize statement data content
        # self.transactions = []
        # self.clicked_category = []  # holds all the user set categories
        #
        # # initialize general GUI variables
        # self.master = master
        # self.frame = tk.Frame(self.master, bg="#194d33")
        # self.frame.grid(row=row_num, column=column_num)
        # self.prompt = Text(self.frame, padx=10, pady=10, height=5)
        # self.prompt.grid(row=2, column=0, rowspan=4)
        #
        # # get categories
        # self.categories = category_helper.load_categories()

        # # photo filepath
        self.photo_filepath = ""


    ##############################################################################
    ####      DATA LOADING FUNCTIONS    ##########################################
    ##############################################################################

    # create_statement_data: combines and automatically categorizes transactions across all raw account statement data
    def create_statement_data(self):
        if self.check_statement_status(self.load_statement_data()):
            gui_helper.gui_print(self.master, self.prompt, "Uh oh, looks like data already exists for this particular statement")
            res = gui_helper.promptYesNo("Data might already be loaded in for this statement... do you want to continue?")
            if res is False:
                gui_helper.gui_print(self.master, self.prompt, "Ok, not loading in statement")
                return

        print("Creating statement data for", self.title)
        self.transactions.extend(self.load_statement_data())

        # check for if transactions actually got loaded in
        if len(self.transactions) == 0:
            gui_helper.gui_print(self.master, self.prompt, "Uh oh, something went wrong retrieving transactions. Likely the transaction data is corrupt and resulted in 0 transactions. Exiting statement data creation.")
            return False

        gui_helper.gui_print(self.master, self.prompt, "Loaded in raw transaction data, running categorizeStatementAutomatic() now!")

        self.categorizeStatementAutomatic()  # run categorizeStatementAutomatic on the transactions
        gui_helper.gui_print(self.master, self.prompt,
                             "Statement should be loaded and displayed")

    # load_statement_data: this function should be defined per account's Statement class
    # DO NOT DELETE
    def load_statement_data(self):
        pass

    # TODO: failing when I try to load in Marcus statement data... however it is loading in erroneously
    # check_statement_status: returns True if data already exists for this statement, False otherwise
    def check_statement_status(self, current_transactions):
        # handle leading 0 for months less than 10 (before October)
        if self.month >= 10:
            month_start = str(self.year) + "-" + str(self.month) + "-" + "01"
            month_end = str(self.year) + "-" + str(self.month) + "-" + "31"
        else:
            month_start = str(self.year) + "-" + "0" + str(self.month) + "-" + "01"
            month_end = str(self.year) + "-" + "0" + str(self.month) + "-" + "31"

        loaded_transactions = db_helper.get_account_transactions_between_date(self.account_id, month_start, month_end)

        # compare to loaded length of transactions
        if len(loaded_transactions) == len(current_transactions):
            if len(loaded_transactions) != 0:  # prevents alerting when data might not be loading in correctly
                print("Uh oh, has this data been loaded in already?")
                # sanity check a couple transactions??
                return True
        else:
            return False


    ##############################################################################
    ####      CATEGORIZATION FUNCTIONS    ########################################
    ##############################################################################

    # categorizeStatementAutomatic: adds a category label to each statement array based predefined
    def categorizeStatementAutomatic(self):
        categories = categories_helper.load_categories()
        for transaction in self.transactions:
            transaction.categorizeTransactionAutomatic(categories)


    ##############################################################################
    ####      DATA SAVING FUNCTIONS    ###########################################
    ##############################################################################

    # TODO: make green/red checkmarks update upon completion of this (for Statement only)
    #   also - make Category dropdowns on transactions lines change into written text that can be double clicked
    # save_statement: saves a categorized statement as a csv
    def save_statement(self):
        gui_helper.gui_print(self.frame, self.prompt, "Attempting to save statement...")
        if self.check_statement_status(self.transactions):
            response = gui_helper.promptYesNo("It looks like a saved statement for " + self.title + " already exists, are you sure you want to overwrite by saving this one?")
            if response is False:
                gui_helper.gui_print(self.frame, self.prompt, "Ok, not saving statement")
                return False

        error_status = 0
        for transaction in self.transactions:
            success = db_helper.insert_transaction(transaction)
            if success == 0:
                error_status = 1

        if error_status == 1:
            gui_helper.alert_user("Error in ledger adding!", "At least 1 thing went wrong adding to ledger")
            return False
        else:
            gui_helper.gui_print(self.frame, self.prompt, "Saved statement")
        return True



