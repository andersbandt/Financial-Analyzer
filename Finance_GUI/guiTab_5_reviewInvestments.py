# import needed packages
import tkinter as tk
from tkinter import *
from tkinter import ttk

from datetime import date

from functools import partial

import lambdas
import sqlite3

# import user defined modules
from Statement_Classes import Statement
from Statement_Classes import Transaction

from Finance_GUI import gui_helper
from categories import category_helper
from db import db_helper


class tabInvestments:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.fr_add_inv_data = tk.Frame(self.frame)
        self.fr_add_inv_data.grid(row=0, column=0)

        # create prompt for console output
        self.prompt = Text(self.frame, padx=5, pady=5, height=5)

        # current transaction for analyzing
        self.transactions = []

        # stuff for handling GUI table
        self.frame_data = 0
        self.labels = []
        self.clicked_category = []  # holds all the user set categories

        # load Category objects
        self.categories = category_helper.load_categories()

        self.initTabContent()


# initTabContent: initializes the main content of the tab
    def initTabContent(self):
        print("Initializing tab 5 content")

        self.init_inv_data_cont()

        # set up button to start examining investment account
        start_analyzing = Button(self.fr_add_inv_data, text="Review Investment Account", command=lambda: self.review_investment_account())
        start_analyzing.grid(row=1, column=3)  # place 'Start Categorizing' button


    # TODO: this whole function will fail miserably. Variables still need to be renamed
    def init_inv_data_cont(self):

        inv_cat_names = []
        for category in db_helper.get_category_names():
            inv_cat_names.append(category)

        clicked_investment_category = StringVar()  # datatype of menu text
        clicked_investment_category.set(inv_cat_names[0])  # initial menu text

        investment_category_dropdown = OptionMenu(self.fr_add_inv_data, clicked_investment_category, *inv_cat_names)  # create drop down menu of months
        investment_category_dropdown.grid(row=6,column=0)

        ### text input for user to add investment ticker information ###
        Label(self.fr_add_inv_data, text="Investment Ticker").grid(row=5, column=1)
        investment_ticker = Text(self.fr_add_inv_data, height=3, width=12)
        investment_ticker.grid(row=6, column=1)

        ### text input for user to add investment amount information ###
        Label(self.fr_add_inv_data, text="Investment Transaction Amount").grid(row=5, column=2)
        transaction_amount = Text(self.fr_add_inv_data, height=3, width=12)
        transaction_amount.grid(row=6, column=2)

        # place drop down for investment account
        Label(self.fr_add_inv_data, text="Investment Account").grid(row=6, column=3)

        acc_names = db_helper.get_account_names()

        clicked_account = StringVar()  # datatype of menu text
        clicked_account.set(acc_names[0])  # initial menu text
        drop = OptionMenu(self.fr_add_inv_data, clicked_account, *acc_names)  # create drop down menu of months
        drop.grid(row=6, column=3)

        # set up button to add a keyword
        add_keyword = Button(self.fr_add_inv_data, text="Add Investment Ticker Data",
                             command=lambda: self.add_investment_data(clicked_account.get(), clicked_investment_category.get(),
                                                                      investment_ticker.get(1.0, "end"), transaction_amount.get(1.0, "end")))
        add_keyword.grid(row=6, column=4)


    def init_inv_data_addition_cont(self, investment_account, investment_category, investment_ticker, investment_amount):
        investment_account = investment_account[1]
        print("Got this for investment_account: " + investment_account)
        print("Got this for investment_category: " + investment_category)
        investment_category_id = category_helper.category_name_to_id(self.conn, investment_category)
        print("Got this for investment_category_id: " + str(investment_category_id))
        print("Got this for investment_ticker: " + investment_ticker)
        print("Got this for investment_amount: " + investment_amount)

        # add Investment Transaction to ledger database
        if investment_ticker == '':
            raise ValueError

        investment_date = date.today()  # Returns the current local date
        investment_ticker = investment_ticker.strip('\n')
        investment_amount = float(investment_amount.strip('\n'))

