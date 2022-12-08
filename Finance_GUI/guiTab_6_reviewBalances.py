
# import needed packages
import tkinter as tk
from tkinter import *
from tkcalendar import Calendar, DateEntry
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from functools import partial

import lambdas
import sqlite3

# import user defined modules
from Statement_Classes import Statement
from Statement_Classes import Transaction

from Finance_GUI import gui_helper
from db import db_helper
from tools import date_helper
from categories import category_helper
from analyzing import graphing_analyzer
from analyzing import analyzer_helper

# TODO: add some slots for tabular data
#   for example:
#       -latest balance record for each account along with date it was recorded on and type
class tabBalances:
    def __init__(self, master):
        # set up class Tkinter frame info
        self.master = master
        self.frame = tk.Frame(self.master)

        # frame for adding account balance information
        self.fr_ins_bal = tk.Frame(self.frame)
        self.fr_ins_bal.grid(row=0, column=0, padx=10, pady=10)

        # frame for reviewing balance information
        self.fr_rev_bal = tk.Frame(self.frame)
        self.fr_rev_bal.grid(row=1, column=0, padx=10, pady=10)

        # create prompt for console output
        self.prompt = Text(self.frame, padx=5, pady=5, height=5)
        self.prompt.grid(row=0, column=1)

        # current transaction for analyzing
        self.transactions = []

        # stuff for handling GUI table
        self.frame_data = 0
        self.labels = []
        self.clicked_category = []  # holds all the user set categories

        # load Category objects
        self.categories = category_helper.load_categories()

        self.initTabContent()


    # initTabContent: initializes all content for the tab
    def initTabContent(self):
        print("Initializing tab 6 content")
        self.init_fr_ins_bal()

        self.init_fr_rev_bal()


    # init_fr_ins_bal: initializes the content for inserting balance information
    def init_fr_ins_bal(self):
        print("Initializing balance info insert frame")

        # add a frame title
        Label(self.fr_ins_bal, text="Insert Account Balance", font=("Arial", 16)).grid(row=0, column=0, columnspan=5, padx=3, pady=3)

        # set up top row of text labels
        Label(self.fr_ins_bal, text="Select Account").grid(row=1, column=0)
        Label(self.fr_ins_bal, text="Enter Amount").grid(row=1, column=1)
        Label(self.fr_ins_bal, text="Enter Date (MM/DD/YY)").grid(row=1, column=2)


        ### set up user inputs for account balance
        # account
        accounts = db_helper.get_account_names()

        clicked_account = StringVar()  # datatype of menu text
        clicked_account.set(accounts[0])  # initial menu text
        account_drop = OptionMenu(self.fr_ins_bal, clicked_account, *accounts)  # create drop down menu of accounts
        account_drop.grid(row=2, column=0)

        # amount
        bal_amount = Text(self.fr_ins_bal, padx=5, pady=5, height=5, width=20)
        bal_amount.grid(row=2, column=1)

        # date entry
        date_entry = DateEntry(self.fr_ins_bal, width=16, background="magenta3", foreground="white", bd=2)
        date_entry.grid(row=2, column=2)

        # set up button to insert account balance update
        ins_bal_but = ttk.Button(self.fr_ins_bal, text="Insert Balance",
                                 command=lambda: self.ins_acc_bal(clicked_account.get(),
                                                                  bal_amount.get("1.0", "end").strip("\n"),
                                                                  date_entry.get()))
        ins_bal_but.grid(row=1, column=3, rowspan=2)  # place 'Start Categorizing' button


    # init_fr_rev_bal: initializes the content for tab for reviewing balances
    def init_fr_rev_bal(self):
        print("Initializing balance review frame")

        # add a frame title
        Label(self.fr_rev_bal, text="Review Balance History", font=("Arial", 16)).grid(row=0, column=0, columnspan=5, padx=3, pady=3)

        # set up button to insert account balance update
        start_reviewing = ttk.Radiobutton(self.fr_rev_bal, text="Review Balances",
                                 command=lambda: self.show_balances_graph())
        start_reviewing.grid(row=1, column=0)  # place 'Start Categorizing' button


    # ins_acc_bal: inserts data for an account balance record into the SQL database
    # TODO: add error checking for multiple balances per account on SAME day
    def ins_acc_bal(self, account, amount, date):
        try:
            account_id = db_helper.get_account_id_from_name(account)
            formatted_date = date_helper.conv_two_digit_date(date)

            db_helper.insert_account_balance(account_id, amount, formatted_date)
            gui_helper.gui_print(self.frame, self.prompt, "Inserted balance of " + str(amount) + " for account " + account + " on date " + formatted_date)
        except Exception as e:
            gui_helper.gui_print(self.frame, self.prompt, "Something went wrong inserting balance")
            gui_helper.gui_print(self.frame, self.prompt, e)
            gui_helper.gui_print(self.frame, self.prompt, "Try again when your code is fixed")


    # this function will be interesting to write.
    # I think I should keep a cumulative total of two balances - checkings/savings and investments
    # Then as I iterate across dates everytime there is a new entry I update that total and make a new record
    def show_balances_graph(self):
        print("INFO: show_balances_graph running")

        # create Frame
        fr = tk.Frame(self.fr_rev_bal)
        fr.grid(row=2, column=0, columnspan=3, rowspan=3)

        # TODO: checkbox creation not working
        # # create checkboxes for account type graph selection
        # acc_types = ["Liquid", "Investment"]
        # acc_type_sel = []
        #
        # i = 0
        # for acc_t in acc_types:
        #     print("Creating a checkbutton for account type: ", acc_t)
        #
        #     row = i
        #     print("Placing at row:", str(row))
        #
        #     var1 = tk.IntVar()
        #     acc_type_sel.append(var1)
        #     tk.Checkbutton(self.frame, text=acc_t, variable=acc_type_sel[i], onvalue=1, offvalue=0,
        #                command=lambda: self.set_acc_show_settings(acc_type_sel).grid(row=row, column=1))
        #     i += 1

        # set params
        days_previous = 180  # half a year maybe?
        N = 5

        # get pyplot figure
        figure = graphing_analyzer.create_stacked_balances(days_previous, N)
        canvas = FigureCanvasTkAgg(figure, fr)
        canvas.get_tk_widget().grid(row=3, column=1, columnspan=2)


        # get data for displaying balances in tabular form
        spl_Bx = analyzer_helper.gen_Bx_matrix(days_previous, N)
        recent_Bx = spl_Bx[-1]

        print("Working with this for tabulated data conversion")
        print(recent_Bx)

        # Update buttons frames idle tasks to let tkinter calculate sizes
        #self.frame.update_idletasks()



    def set_acc_show_settings(self, var):
        print("Got this for var:", var)
        return


