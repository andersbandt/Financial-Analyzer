# import needed packages
import tkinter as tk
from tkinter import *
from tkinter import ttk

from functools import partial

import lambdas
import sqlite3

# import user defined modules
from Statement_Classes import Statement
from Statement_Classes import Transaction

from Finance_GUI import gui_helper

from categories import category_helper


class tabInvestments:
    def __init__(self, master, conn):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.date_select_frame = tk.Frame(self.frame)
        self.date_select_frame.grid(row=0, column=0)

        # create prompt for console output
        self.prompt = Text(self.frame, padx=5, pady=5, height=5)

        # current transaction for analyzing
        self.transactions = []

        # stuff for handling GUI table
        self.frame_data = 0
        self.labels = []
        self.clicked_category = []  # holds all the user set categories

        # establish SQl database properties
        self.conn = conn
        self.cur = self.conn.cursor()

        # load Category objects
        self.categories = category_helper.load_categories(self.conn)

        self.initTabContent()


# initTabContent: initializes the main content of the tab
    def initTabContent(self):
        print("Initializing tab 5 content")

        # set up top row of text labels
        label = Label(self.date_select_frame, text="Select Year")
        label.grid(row=0, column=0)
        label = Label(self.date_select_frame, text="Select Month")
        label.grid(row=0, column=1)

        # set up user inputs for statement (year and month)
        year_dropdown = gui_helper.generateYearDropDown(self.date_select_frame)
        year_dropdown[0].grid(row=1, column=0)
        month_dropdown = gui_helper.generateMonthDropDown(self.date_select_frame)
        month_dropdown[0].grid(row=1, column=1)

        # set up button to start examining investment account
        start_analyzing = Button(self.date_select_frame, text="Review Investment Account",
                                 command=lambda: self.review_investment_account() )
        start_analyzing.grid(row=1, column=3)  # place 'Start Categorizing' button



    def review_investment_account(self):
        pass