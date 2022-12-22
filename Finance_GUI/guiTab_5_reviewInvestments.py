
# import needed packages
import tkinter as tk
from tkinter import *
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests

# import user defined modules
from categories import category_helper
from Finance_GUI import gui_helper
from db import db_helper
from Analyzing import inv_h
from Analyzing import graphing_analyzer


class tabInvestments:
    def __init__(self, master):
        ### add GUI content for tab
        self.master = master
        self.frame = tk.Frame(self.master)

        # add Frame for adding investment data
        self.fr_add_inv_data = tk.Frame(self.frame)
        self.fr_add_inv_data.grid(row=0, column=0)

        # add Frame for reviewing investment data
        self.fr_rev_inv_data = tk.Frame(self.frame)
        self.fr_rev_inv_data.grid(row=1, column=0)

        # add Frame for displaying graphs
        self.fr_gr_inv = tk.Frame(self.frame)
        self.fr_gr_inv.grid(row=2, column=0)

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

        self.init_fr_add_inv_data()
        self.init_fr_rev_inv_data()
        self.init_fr_gr_inv()


    # init_fr_add_inv_data: inits GUI content for adding investment data
    def init_fr_add_inv_data(self):
        # add date selector
        Label(self.fr_add_inv_data, text="Date").grid(row=1, column=0, pady=5)
        date_entry = DateEntry(self.fr_add_inv_data, width=16, background="magenta3", foreground="white", bd=2)
        date_entry.grid(row=2, column=0, padx=10, pady=10)

        # list of investment accounts (type III)
        Label(self.fr_add_inv_data, text="Investment Account").grid(row=1, column=1)

        acc_names = db_helper.get_account_names_by_type(3)

        clicked_account = StringVar()  # datatype of menu text
        clicked_account.set(acc_names[0])  # initial menu text
        drop = OptionMenu(self.fr_add_inv_data, clicked_account, *acc_names)  # create drop down menu of months
        drop.grid(row=2, column=1, padx=10, pady=10)

        # ticker information
        Label(self.fr_add_inv_data, text="Ticker").grid(row=1, column=2)
        investment_ticker = Text(self.fr_add_inv_data, height=3, width=12)
        investment_ticker.grid(row=2, column=2, pady=10, padx=10)

        # shares amount information
        Label(self.fr_add_inv_data, text="Shares").grid(row=1, column=3)
        transaction_amount = Text(self.fr_add_inv_data, height=3, width=12)
        transaction_amount.grid(row=2, column=3, pady=10, padx=10)

        # investment type
        # create dropdown for 1 through 5
        Label(self.fr_add_inv_data, text="Investment Type").grid(row=1, column=4)
        inv_type = Text(self.fr_add_inv_data, height=3, width=12)
        inv_type.grid(row=2, column=4, pady=10, padx=10)
        Label(self.fr_add_inv_data, text="1: pure stock\n2: mutual fund\n3: bonds\n4: crypto\n5: cash").grid(row=2, column=5)


        # add button to execute addition of investment information
        add_keyword = Button(self.fr_add_inv_data, text="Add Investment Ticker Data",
                             command=lambda: self.add_investment_data(date_entry.get(),
                                                                      clicked_account.get(),
                                                                      investment_ticker,
                                                                      transaction_amount,
                                                                      inv_type))
        add_keyword.grid(row=6, column=4)


    # init_fr_rev_inv_data: inits the GUI content for reviewing investment data
    def init_fr_rev_inv_data(self):
        # add dropdown for investment type accounts (type III)

        # set up button to start examining investment account
        start_analyzing = Button(self.fr_rev_inv_data, text="Print Current Position Data", command=lambda: self.review_inv_acc())
        start_analyzing.grid(row=1, column=3)  # place 'Start Categorizing' button


    def init_fr_gr_inv(self):
        # add title and buttons in their own frame
        fr_title_button = tk.Frame(self.fr_gr_inv)
        fr_title_button.grid(row=0, column=0, pady=10, padx=10, sticky="")
        Label(fr_title_button, text="Graph Processing", font=("Arial", 16)).grid(
            row=0,
            column=0,
            padx=10,
            pady=10)

        # set up button to show asset allocation
        b_asset_alloc = Button(fr_title_button, text="Show Asset Allocation", command=lambda: self.show_asset_alloc())
        b_asset_alloc.grid(row=0, column=1, padx=5)  # place 'Start Categorizing' button

        # set up button to print historical price history of accounts
        b_hist_price = Button(fr_title_button, text="Show Historical Price", command=lambda: self.show_hist_price_data())
        b_hist_price.grid(row=0, column=2, padx=5)  # place 'Start Categorizing' button


# TODO: refactor this to add account_id instead of account name
    # add_investment_data: adds investment data to the SQL database
    def add_investment_data(self, date, account_id, ticker_obj, amount_obj, inv_type_obj):
        # get values from text entries
        ticker = ticker_obj.get(1.0, "end")
        amount = amount_obj.get(1.0, "end")
        inv_type = inv_type_obj.get(1.0, "end")

        # delete values
        amount_obj.delete("1.0", "end")
        ticker_obj.delete("1.0", "end")
        inv_type_obj.delete("1.0", "end")

        # do some processing on variables
        ticker = ticker.strip('\n')
        amount = float(amount.strip('\n'))
        inv_type = int(inv_type)

        # final variable error handling
        if ticker == '':
            raise ValueError

        # insert investment
        db_helper.insert_investment(date, account_id, ticker, amount, inv_type)


    def review_inv_acc(self):
        print("guiTab_5_reviewInvestments: running review_inv_acc")
        tickers = db_helper.get_all_ticker()

        for ticker in tickers:
            inv_h.print_ticker_info(ticker[0])


    def show_asset_alloc(self):
        # get pyplot figure
        try:
            figure = graphing_analyzer.create_asset_alloc_chart()
        except requests.exceptions.ConnectionError as e:
            print("Connection error:", e)
            gui_helper.alert_user("Error generating graph", "Connection error. Please check connection and try again.", kind="error")

        canvas = FigureCanvasTkAgg(figure, self.fr_gr_inv)
        canvas.get_tk_widget().grid(row=2, column=0)

        # Update buttons frames idle tasks to let tkinter calculate sizes
        self.frame.update_idletasks()


    def show_hist_price_data(self):
        # get pyplot figure
        figure = graphing_analyzer.create_hist_price_data_line_chart()
        canvas = FigureCanvasTkAgg(figure, self.fr_gr_inv)
        canvas.get_tk_widget().grid(row=2, column=0)

        # Update buttons frames idle tasks to let tkinter calculate sizes
        self.frame.update_idletasks()


