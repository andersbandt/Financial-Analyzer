# import needed packages
import sqlite3
import tkinter as tk
from tkinter import *
from datetime import date  # needed to get current date
import os  # needed to examine filesystem

# import user defined helper modules
from Finance_GUI import gui_helper
from categories import category_helper

# import Statement classes
from Statement_Classes import Marcus
from Statement_Classes import Robinhood
from Statement_Classes import WellsCredit
from Statement_Classes import WellsChecking
from Statement_Classes import WellsSaving
from Statement_Classes import VanguardBrokerage
from Statement_Classes import VanguardRoth
from Statement_Classes import Venmo


# TODO: eliminate any scraping functions in this and replace them solely with GUI based functions

class tabFinanceData:
    def __init__(self, master, conn):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.prompt = Text(self.frame, padx=5, pady=5, height=5)

        self.load_yes = 0  # yes button to loading statement data
        self.load_no = 0  # no button for loading statement data

        self.statement = 0
        self.files_drop = 0

        self.conn = conn
        self.cur = self.conn.cursor()

        self.initTabContent()

    # initTabContent: initializes the main content of the tab
    def initTabContent(self):
        print("Initializing tab 4 content")

        # create frame for initial tab content
        sel_frame = tk.Frame(self.frame)
        sel_frame.grid(row=0, column=0)

        # set up top row of text labels
        label = Label(sel_frame, text="Select Year")
        label.grid(row=0, column=0)
        label = Label(sel_frame, text="Select Month")
        label.grid(row=0, column=1)

        # set up user inputs for statement (year and month)
        year_dropdown = gui_helper.generateYearDropDown(sel_frame)
        year_dropdown[0].grid(row=1, column=0)
        month_dropdown = gui_helper.generateMonthDropDown(sel_frame)
        month_dropdown[0].grid(row=1, column=1)

        # set up button to start generate list of files in certain month/year directory
        gen_file_drop = Button(sel_frame, text="Select Month",
                               command=lambda: self.grab_month_files(sel_frame, year_dropdown[1].get(), month_dropdown[1].get()))
        gen_file_drop.grid(row=1, column=3)


        # initialize the investment content
        self.init_investment_content()


    # TODO: this whole function will fail miserably. Variables still need to be renamed
    def init_investment_content(self):
        # KEYWORD ADDING
        # add drop down for category
        with self.conn:
            self.cur.execute('SELECT * FROM category where parent=?', [10000000027])  # TODO: can I not hard code this in?
            categories = self.cur.fetchall()

        i = 0
        for category in categories:
            print(category)
            #categories[i] = gui_helper.convertTuple(category)
            categories[i] = category[2][0:]
            i += 1

        clicked_investment_category = StringVar()  # datatype of menu text
        clicked_investment_category.set(categories[0])  # initial menu text

        investment_category_dropdown = OptionMenu(self.frame, clicked_investment_category, *categories)  # create drop down menu of months
        investment_category_dropdown.grid(row=6,column=0)

        # text input for user to add investment ticker information
        label = Label(self.frame, text="Investment Ticker")
        label.grid(row=5, column=1)
        investment_ticker = Text(self.frame, height=3, width=12)
        investment_ticker.grid(row=6, column=1)

        # text input for user to add investment amount information
        label = Label(self.frame, text="Investment Transaction Amount")
        label.grid(row=5, column=2)
        transaction_amount = Text(self.frame, height=3, width=12)
        transaction_amount.grid(row=6, column=2)

        # place drop down for investment account
        investment_account = Label(self.frame, text="Investment Account")
        investment_account.grid(row=6, column=3)
        self.cur.execute('SELECT account_id, name FROM account')
        accounts = self.cur.fetchall()

        account_names = list((x[1] for x in accounts))

        clicked_account = StringVar()  # datatype of menu text
        clicked_account.set(accounts[0])  # initial menu text
        drop = OptionMenu(self.frame, clicked_account, *accounts)  # create drop down menu of months
        drop.grid(row=6, column=3)

        # set up button to add a keyword
        add_keyword = Button(self.frame, text="Add Investment Ticker Data",
                             command=lambda: self.add_investment_data(clicked_account.get(), clicked_investment_category.get(),
                                                                      investment_ticker.get(1.0, "end"), transaction_amount.get(1.0, "end")))
        add_keyword.grid(row=6, column=4)


    # TODO: this function is not adding correctly to the database
    # add_investment_data
    def add_investment_data(self, investment_account, investment_category, investment_ticker, investment_amount):
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

        with self.conn:
            try:
                self.conn.set_trace_callback(print)
                self.cur.execute('INSERT INTO ledger (trans_date, account_id, category_id, amount, description) VALUES(?, ?, ?, ?, ?)', (investment_date, investment_account, investment_category_id, investment_amount, investment_ticker))
                self.conn.set_trace_callback(None)
            except sqlite3.Error as e:
                print("Uh oh, something went wrong with adding to ledger table: ", e)
            else:
                gui_helper.gui_print(self.frame, self.prompt, "Added investment transaction: ", investment_ticker)
                #category_name_obj.delete("1.0", "end")
        pass

    # grab_month_files: grabs files from a certain month and display drop down
        # TODO: get this function to also display an indicator of which data has been loaded in
    def grab_month_files(self, frame, year, month):
        print("guiTab_loadSpendingData - grab_month_files got:")
        print("\tyear: ", year)
        print("\tmonth: ", month)

        # add label
        label = Label(frame, text="Month Files")
        label.grid(row=3, column=0)

        # delete previous month files drop down
        if (self.files_drop != 0):
            self.files_drop.grid_remove()

        # create and place new file dropdown
        base_path = "C://Users//ander//OneDrive//Documents//Financials"
        dir_path = gui_helper.get_statement_folder(base_path, year, month)

        dir_list = os.listdir(dir_path)

        clicked_file = StringVar()  # datatype of menu text
        clicked_file.set(dir_list[0])
        self.files_drop = OptionMenu(frame, clicked_file, *dir_list)  # create drop down menu of months
        self.files_drop.grid(row=3, column=1)

        # place drop down for statement type
        self.cur.execute('SELECT account_id, name FROM account')
        accounts = self.cur.fetchall()

        account_names = list((x[1] for x in accounts))

        clicked_account = StringVar()  # datatype of menu text
        clicked_account.set(accounts[0])  # initial menu text
        drop = OptionMenu(frame, clicked_account, *accounts)  # create drop down menu of months
        drop.grid(row=3, column=2)

        # set up button to start loading in file data
        gen_file_drop = Button(frame, text="Select File",
                               command=lambda: self.load_statement(clicked_file.get(), clicked_account.get()[1:11], year, month))
        gen_file_drop.grid(row=3, column=3)


    # creates an array of true/false depending on if data seems to have been loaded in or not
    def check_month_data_status(self, year, month):
        pass


    # TODO: figure out how to get actual date and month into this statement creation
    def load_statement(self, file_name, account_id, year, month):
        account_id = int(account_id)  # unsure if this is needed or not

        print("GOT MONTH", month)

        month_int = gui_helper.month2Int(month)

        # TODO: can I figure out a way to not hard code this in?
        if account_id == 2000000001:  # Marcus
            stat = Marcus.Marcus(self.frame, self.conn, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
        elif account_id == 2000000002:
            stat = WellsChecking.WellsChecking(self.frame, self.conn, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
        elif account_id == 2000000003:
            stat = WellsSaving.WellsSaving(self.frame, self.conn, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
        elif account_id == 2000000004:
            stat = WellsCredit.WellsCredit(self.frame, self.conn, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
        elif account_id == 2000000005:  # Vanguard Brokerage
            stat = VanguardBrokerage.VanguardBrokerage(self.frame, self.conn, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
        elif account_id == 2000000006:  # Vanguard Roth
            stat = VanguardRoth.VanguardRoth(self.frame, self.conn, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
        elif account_id == 2000000007:  # Venmo
            stat = Venmo.Venmo(self.frame, self.conn, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
        elif account_id == 2000000008:  # Robinhood
            stat = Robinhood.Robinhood(self.frame, self.conn, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
        else:
            print("No valid account selected in guiTab_loadSpendingData: load_statement")
            gui_helper.alert_user("Error in code account binding", "No valid Statement Class exists for the selected account ID", "info")
