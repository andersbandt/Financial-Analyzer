# import needed packages
import tkinter as tk
from tkinter import *
from tkcalendar import *
from tkinter import ttk

from functools import partial

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# import Statement_Classes
from Statement_Classes import Ledger

# import user defined helper modules
from Finance_GUI import gui_helper
from categories import category_helper
from analyzing import analyzer_helper
from analyzing import graphing_analyzer
from db import db_helper
from Scraping import scraping_helper

from tools import date_helper


class tabSpendingHistory:
    def __init__(self, master):
        ### add master, frame, and scrollbar
        self.master = master
        self.frameX = tk.Frame(self.master, width=1200, height=850)

        ### create a canvas and scrollbar
        self.canvas = Canvas(self.frameX, width=1200, height=800)  # for some reason increasing the height breaks the scrollbar?

        # add scrollbar
        scroll = Scrollbar(command=self.canvas.yview, orient="vertical")
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
        self.fr_date_select.grid(row=0, column=0)

        # initialize graph processing frame
        self.fr_graph_proc = tk.Frame(self.frame, bg="#00bcd4")
        self.fr_graph_proc.grid(row=5, column=0)

        # current transactions and accounts for analyzing
        self.transactions = []

        self.initTabContent()


# initTabContent: initializes the main content of the tab
    # for this tab, most of the initial content is date and account selection for recalling data
    def initTabContent(self):
        self.init_date_account_selection()
        self.init_graph_proc()


# init_date_account_selection: initializes the calendar widgets and account selection checkbox
    def init_date_account_selection(self):
        print("Initializing tab 2 content")

        # set up top row of text labels
        Label(self.fr_date_select, text="Select Start Date").grid(row=0, column=1)
        Label(self.fr_date_select, text="Select End Date").grid(row=0, column=2)
        Label(self.fr_date_select, text="Select Accounts (please toggle one result each query)").grid(row=0, column=3)

        # set up calendar pick for start search date
        fone = Frame(self.fr_date_select)
        fone.grid(row=1, column=1)

        cal_start = Calendar(fone, selectmode="day", year=2022, month=1, day=1)
        cal_start.grid(row=0, column=0, padx=10, pady=5)

        # set up calendar pick for end search date
        ftwo = Frame(self.fr_date_select)
        ftwo.grid(row=1, column=2)

        cal_end = Calendar(ftwo, selectmode="day", year=2022, month=1, day=1)
        cal_end.grid(row=0, column=0, padx=10, pady=5)

        # create checkbox list for accounts
        account_checkbox_frame = Frame(self.fr_date_select)
        account_checkbox_frame.grid(row=1, column=3)

        # function for updating current accounts in checkbox
        def on_select(vars):
            self.accounts = []
            for var in vars:
                account_id = int(var.get())
                self.accounts.append(account_id)

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

        # set up button to start the searching and show analyzing options
        start_analyzing = Button(self.fr_date_select, text="Recall Data", command=lambda: self.analyze_history(cal_start.get_date(), cal_end.get_date(), self.accounts))
        start_analyzing.grid(row=1, column=4, padx=10, pady=5)  # place 'Start Categorizing' button


# init_graph_proc: initializes content related to showing graphs about analyzed data
    def init_graph_proc(self):
        # add title and buttons in their own frame
        fr_title_button = tk.Frame(self.fr_graph_proc)
        fr_title_button.grid(row=0, column=0, pady=10, padx=10, sticky="")
        Label(fr_title_button, text="Graph Processing", font=("Arial", 16)).grid(row=0, column=0, pady=10)
        self.show_graphical_processing_gui(fr_title_button)

        self.frame.update_idletasks()


# analyze_history: pulls in data based on date and account selections
    def analyze_history(self, date_start, date_end, accounts):
        # error handle no accounts
        if len(accounts) == 0:
            gui_helper.alert_user("Error with recalling data", "No accounts selected.", "error")

        # format the date strings
        formatted_start = scraping_helper.format_date_string(date_start)
        formatted_end = scraping_helper.format_date_string(date_end)

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

        # TODO: deleting the statement deletes the calendar date select
        self.fr_date_select.grid_forget()  # hide the date selection Frame
        ledge = Ledger.Ledger(self.frame, "Recalled Data", 3, 0)
        ledge.set_statement_data(self.transactions)
        ledge.createStatementTable()
        return True


    # show_graphical_processing_gui
    def show_graphical_processing_gui(self, frame):
        print("Running guiTab_analyzeSpendingHistory: show_graphical_processing_gui")

        # set up button to show pie chart of all categories and expenses
        Button(frame, text="Show Pie Chart", command=lambda: self.show_pie_chart()).grid(row=1, column=0, padx=5)

        # set up button to show a summary over time of the transactions recalled
        Button(frame, text="Show Pie Chart (top level)", command=lambda: self.show_top_pie_chart()).grid(row=1, column=1, padx=5)

        # set up button to show pie chart of all categories and expenses
        Button(frame, text="Show Bar Chart", command=lambda: self.create_bar_chart()).grid(row=1, column=2, padx=5)

        # set up button to show a summary over time of the transactions recalled
        Button(frame, text="Show Sums over Time", command=lambda: self.create_summation_vs_time()).grid(row=1, column=3, padx=5)

        # set up button to show a summary over time of the transactions recalled
        Button(frame, text="Show Budget Diff", command=lambda: self.show_budget_diff_chart()).grid(row=1, column=4, padx=5)


    def show_pie_chart(self):
        # get pyplot figure
        figure = graphing_analyzer.create_pie_chart(self.transactions, category_helper.load_categories())
        canvas = FigureCanvasTkAgg(figure, self.fr_graph_proc)
        canvas.get_tk_widget().grid(row=2, column=0)

        # Update buttons frames idle tasks to let tkinter calculate sizes
        self.frame.update_idletasks()


    def show_top_pie_chart(self):
        # get pyplot figure
        figure = graphing_analyzer.create_top_pie_chart(self.transactions, category_helper.load_categories())
        canvas = FigureCanvasTkAgg(figure, self.fr_graph_proc)
        canvas.get_tk_widget().grid(row=2, column=0)

        # Update buttons frames idle tasks to let tkinter calculate sizes
        self.frame.update_idletasks()


    def show_budget_diff_chart(self):
        # get pyplot figure
        figure = graphing_analyzer.create_top_pie_chart(self.transactions, category_helper.load_categories())
        canvas = FigureCanvasTkAgg(figure, self.fr_graph_proc)
        canvas.get_tk_widget().grid(row=2, column=0)

        # Update buttons frames idle tasks to let tkinter calculate sizes
        self.frame.update_idletasks()



