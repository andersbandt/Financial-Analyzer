# import needed modules
import tkinter as tk
from tkinter import ttk
from tkinter import *  # TODO: bad practice I think, fix this. Like get Text module
from functools import partial

# import user defined modules
from Statement_Classes import Ledger
from Finance_GUI import gui_helper
from categories import category_helper
from db import db_helper


class Statement(Ledger.Ledger):
    def __init__(self, master, account_id, year, month, file, row_num, column_num, *args, **kwargs):
        # initialize identifying statement info
        self.account_id = account_id
        self.year = year
        self.month = month
        self.title = str(self.account_id) + ":" + str(self.year) + "-" + str(self.month)

        # load in statement filepath info
        self.base_filepath = "C:/Users/ander/OneDrive/Documents/Financials"
        self.filepath = gui_helper.get_statement_folder(self.base_filepath, year, month) + file  # generate filepath of .csv file to download

        # initialize statement data content
        self.transactions = []
        self.clicked_category = []  # holds all the user set categories

        # initialize gui content
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.grid(row=row_num, column=column_num)
        self.prompt = Text(self.frame, padx=5, pady=5, height=10)
        self.prompt.grid(row=4, column=0)

        # get categories
        self.categories = category_helper.load_categories()

        # photo filepath
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
        for transaction in self.transactions:
            transaction.categorizeTransactionAutomatic(self.categories)



