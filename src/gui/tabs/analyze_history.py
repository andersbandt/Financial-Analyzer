# import needed packages
import tkinter as tk
from tkinter import ttk

import tkinter as tk
from tkcalendar import Calendar
from functools import partial

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# import Statement_Classes
from statement_types import Ledger

# import user defined helper modules
from gui import gui_helper
import categories.categories_helper as category_helper
from analysis import analyzer_helper
from analysis import graphing_analyzer
from db import db_helper

from tools import date_helper

# TODO: lots
# this should be the main focus of my program. The other stuff is cool but I have the data in place now where I can really focus
# on the analysis. Ultimate customization.

# things like
# - % increase/decrease over selected date range vs previous period of x days
# - clickable categories to view list of transactions in categories for period of days
# - budgeting can easily be started now

class tabSpendingHistory:
    def __init__(self, master):
        ### add master, frame, and scrollbar
        self.master = master
        self.frameX = tk.Frame(self.master, width=1200, height=850)

        ### create a canvas and scrollbar
        self.canvas = tk.Canvas(self.frameX, width=1200, height=800)  # for some reason increasing the height breaks the scrollbar?

        # add scrollbar
        scroll = tk.Scrollbar(self.frameX, command=self.canvas.yview, orient="vertical")
        scroll.grid(row=0, column=1, sticky="ns")

        # configure canvas
        self.canvas.configure(yscrollcommand=scroll.set, scrollregion=self.canvas.bbox("all"))
        self.canvas.grid(row=0, column=0)

        # create internal frame for content
        self.frame = tk.Frame(self.canvas)
        self.frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        ### initialize frames within tab
        # init date select frame
        self.fr_date_select = tk.Frame(self.frame, bg="#856ff8")
        self.fr_date_select.grid(row=0, column=0, padx=10, pady=10)

        # initialize graph processing frame
        self.fr_graph_proc = tk.Frame(self.frame, bg="#00bcd4")
        self.fr_graph_proc.grid(row=5, column=0, padx=10, pady=10)

        # current transactions and accounts for analyzing
        self.transactions = []

        # flag variables
        self.data_loaded = False

        # initialize the tab GUI content
        self.initTabContent()


# initTabContent: initializes the main content of the tab
    # for this tab, most of the initial content is date and account selection for recalling data
    def initTabContent(self):
        print("\nInitializing tab 2 content")
        self.init_date_account_selection()
        self.init_graph_proc()


# init_date_account_selection: initializes the calendar widgets and account selection checkbox
    def init_date_account_selection(self):
        # print frame title
        tk.Label(self.fr_date_select, text="Select Date Range", font=("Arial", 16)).grid(row=0, column=0, columnspan=5, padx=3, pady=3)

        # set up top row of text labels
        tk.Label(self.fr_date_select, text="Select Start Date").grid(row=1, column=0)
        tk.Label(self.fr_date_select, text="Select End Date").grid(row=1, column=1)
        tk.Label(self.fr_date_select, text="Select Accounts").grid(row=1, column=3)

        # set up calendar pick for start search date
        cur_date = date_helper.get_date_int_array()
        cal_start = Calendar(self.fr_date_select, selectmode="day", year=cur_date[0], month=cur_date[1], day=cur_date[2])
        cal_start.grid(row=2, column=0, padx=10, pady=5)

        # set up calendar pick for end search date
        cal_end = Calendar(self.fr_date_select, selectmode="day", year=cur_date[0], month=cur_date[1], day=cur_date[2])
        cal_end.grid(row=2, column=1, padx=10, pady=5)

        ### create checkbox list for accounts
        # add Frame to store checkboxes
        account_checkbox_frame = tk.Frame(self.fr_date_select)
        account_checkbox_frame.grid(row=2, column=3)

        # function for updating current accounts in checkbox
        def on_select(vars):
            self.accounts = []
            for var in vars:
                account_id = int(var.get())
                self.accounts.append(account_id)

        # populate checkboxes with account data
        account_data = db_helper.get_account_ledger_data()
        checkboxes = []
        checkbox_vars = []
        x = 0
        for account_sql in account_data:
            checkbox_vars.append(tk.StringVar())
            checkbox_vars[-1].set(account_sql[0])
            checkboxes.append(ttk.Checkbutton(account_checkbox_frame,
                                       text=str(account_sql[1]),
                                       command=lambda: on_select(checkbox_vars),
                                       variable=checkbox_vars[-1],
                                       onvalue=account_sql[0],
                                       offvalue=None))
            checkboxes[-1].grid(row=x, column=0, sticky="w")
            x += 1
        on_select(checkbox_vars)  # run to initialize values

        # set up button to start the searching and show analyzing options
        start_analyzing = ttk.Button(self.fr_date_select, text="Recall Data", command=lambda: self.analyze_history(cal_start.get_date(), cal_end.get_date(), self.accounts))
        start_analyzing.grid(row=3, column=4, padx=10, pady=5)  # place 'Start Categorizing' button


# init_graph_proc: initializes content related to showing graphs about analyzed data
    def init_graph_proc(self):
        # add title and buttons in their own frame
        fr_title_button = tk.Frame(self.fr_graph_proc)
        fr_title_button.grid(row=0, column=0, pady=10, padx=10, sticky="")
        tk.Label(fr_title_button, text="Graph Processing", font=("Arial", 16)).grid(
            row=0,
            column=0,
            columnspan=3,
            padx=10,
            pady=10)

        self.show_graphical_processing_gui(fr_title_button)
        self.frame.update_idletasks()


# analyze_history: pulls in data based on date and account selections
    def analyze_history(self, date_start, date_end, accounts):
        # error handle no accounts
        if len(accounts) == 0:
            gui_helper.alert_user("Error with recalling data", "No accounts selected.", "error")

        # format the date strings
        formatted_start = date_helper.conv_two_digit_date(date_start)
        formatted_end = date_helper.conv_two_digit_date(date_end)

        # check for if start date is earlier than end date
        if not date_helper.date_order(formatted_start, formatted_end):
            gui_helper.alert_user("Error: can't analyze spending history", "Invalid date range", 'error')

        ### recall transaction data and display it on the Frame
        # get transactions
        self.transactions = analyzer_helper.recall_transaction_data(formatted_start, formatted_end, accounts)

        if self.transactions is None:
            print("ERROR: analyze_history: Recalled 0 transactions. Exiting")
            raise Exception("Can't analyze history. Invalid transaction data recalled.")

        # get gross statistics
        ledger_stats = analyzer_helper.return_ledger_exec_dict(self.transactions)
        print("Got this for ledger statistics")
        print(ledger_stats)

        # init Ledger and display on page
        ledge = Ledger.Ledger(self.frame, "Recalled Data", 3, 0)
        ledge.set_statement_data(self.transactions)
        ledge.createStatementTable()
        self.data_loaded = True
        return True


    # show_graphical_processing_gui
    def show_graphical_processing_gui(self, frame):
        print("Running guiTab_analyzeSpendingHistory: show_graphical_processing_gui")

        # set up button to show pie chart of all categories and expenses
        ttk.Button(frame, text="Show Pie Chart", command=lambda: self.show_pie_chart()).grid(row=1, column=0, padx=5)

        # set up button to show a summary over time of the transactions recalled
        ttk.Button(frame, text="Show Pie Chart (top level)", command=lambda: self.show_top_pie_chart()).grid(row=1, column=1, padx=5)

        # set up button to show pie chart of all categories and expenses
        ttk.Button(frame, text="Show Bar Chart", command=lambda: self.create_bar_chart()).grid(row=1, column=2, padx=5)

        # set up button to show a summary over time of the transactions recalled
        ttk.Button(frame, text="Show Sums over Time", command=lambda: self.create_summation_vs_time()).grid(row=1, column=3, padx=5)

        # set up button to show a summary over time of the transactions recalled
        ttk.Button(frame, text="Show Budget Diff", command=lambda: self.show_budget_diff_chart()).grid(row=1, column=4, padx=5)


    # show_pie_chart: shows a pie chart of all category and amount data in current loaded Ledger
    def show_pie_chart(self):
        # check for data load status and error handle
        self.check_data_load_status()

        ### init Frame objects for graph processing
        # Frame for graphs
        fr_graph = tk.Frame(self.fr_graph_proc)
        fr_graph.grid(row=1, column=0)

        # Frame for graph info
        fr_g_info = tk.Frame(self.fr_graph_proc, bg="#1e254c")
        fr_g_info.grid(row=1, column=1, pady=10, padx=10)

        # Frame for storing subset of ledger data
        fr_g_ledger = tk.Frame(self.fr_graph_proc)
        fr_g_ledger.grid(row=1, column=2)

        ### get pyplot figure, patches, and texts
        figure, categories, amounts = graphing_analyzer.create_pie_chart(self.transactions, category_helper.load_categories(), printmode="debug")

        # add figure to FigureCanvas
        canvas = FigureCanvasTkAgg(figure, fr_graph)
        #canvas.get_tk_widget().grid(row=0, column=0)
        canvas.get_tk_widget().grid(row=0, column=0)

        ### populate data table for Frame fr_g_info
        w = 400
        h = 600
        canvas = tk.Canvas(fr_g_info, width=w, height=h, bg="white")
        canvas.grid(row=0, column=0, padx=20, pady=10)

        # set table params
        x = 25
        y = 20

        w = 125
        h = 30

        # draw Category GUI objects
        for category in categories:
            category.draw_Category_gui_obj(canvas, x, y, w, h, kind="other")
            y += 15 + h

        # draw amounts
        x = 25 + w
        y = 20
        for amount in amounts:
            canvas.create_text(x + w/2, y + h/2, text=str(amount), fill="black", font=('Helvetica 10 bold'))
            y += 15 + h


        # Update buttons frames idle tasks to let tkinter calculate sizes
        #fr_graph.update_idletasks()


# TODO: normalize and report as percent
    def show_top_pie_chart(self):
        # check for data load status and error handle
        self.check_data_load_status()

        # get pyplot figure
        figure = graphing_analyzer.create_top_pie_chart(self.transactions, category_helper.load_categories())
        canvas = FigureCanvasTkAgg(figure, self.fr_graph_proc)
        canvas.get_tk_widget().grid(row=2, column=0)

        # Update buttons frames idle tasks to let tkinter calculate sizes
        self.frame.update_idletasks()


    def show_budget_diff_chart(self):
        # check for data load status and error handle
        self.check_data_load_status()

        # get pyplot figure
        figure = graphing_analyzer.create_top_pie_chart(self.transactions, category_helper.load_categories())
        canvas = FigureCanvasTkAgg(figure, self.fr_graph_proc)
        canvas.get_tk_widget().grid(row=2, column=0)

        # Update buttons frames idle tasks to let tkinter calculate sizes
        self.frame.update_idletasks()


    ##############################################################################
    ####      GENERAL HELPER FUNCTIONS    ########################################
    ##############################################################################

    def check_data_load_status(self):
        if not self.data_loaded:
            gui_helper.alert_user("WARNING", "No ledger data is loaded in yet.", "warning")
        return
