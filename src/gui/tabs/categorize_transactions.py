# import needed packages
import tkinter as tk
from tkinter import *

# import user defined helper modules
from db import db_helper as db_helper

# import Statement classes
from statement_types import Ledger
from statement_types import Transaction


class tabCategorizeTransactions:
    def __init__(self, master):
        # tkinter frame stuff
        self.master = master
        self.frame = tk.Frame(self.master)
        self.fr_categorize = tk.Frame(self.frame, highlightcolor="green", height=200, width=100, cursor="dot")

        self.prompt = Text(self.frame, padx=5, pady=5, height=5)

        self.load_yes = 0  # yes button to loading statement data
        self.load_no = 0  # no button for loading statement data

        self.statement = 0
        self.files_drop = 0

        self.initTabContent()

    # initTabContent: initializes the main content of the tab
    def initTabContent(self):
        print("Initializing tab 7 content")

        # initialize date selection
        self.fr_categorize.grid(row=0, column=0)
        self.init_categorization_content()


    def init_categorization_content(self):
        label = Label(self.fr_categorize, text="In this section you can categorize already loaded in transactions" \
                                                 "that don't have categories")
        label.grid(row=0, column=0)

        # set up button to start loading in file data
        categorize_transactions = Button(self.fr_categorize, text="Start Categorization", command=lambda: self.start_categorization())
        categorize_transactions.grid(row=0, column=1)


    def start_categorization(self):
        self.fr_categorize.grid_forget()

        # get list of transactions without categories and form transactions
        ledger_data = db_helper.get_uncategorized_transactions()

        transactions = []
        for data in ledger_data:
            transactions.append(Transaction.Transaction(data[1], data[2], data[3], data[4], data[5], data[0]))

        statement = Ledger.Ledger(self.frame, "Uncategorized Transactions", 1, 0)
        statement.set_statement_data(transactions)
        statement.categorizeLedgerAutomatic()
        statement.createStatementTable()




