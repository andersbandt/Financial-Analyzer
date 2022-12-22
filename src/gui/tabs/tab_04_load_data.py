
# import needed packages
import sqlite3
import tkinter as tk
from tkinter import *
import os  # needed to examine filesystem

# import user defined helper modules
from gui import gui_helper
from db import db_helper
from tools import load_helper
from tools import date_helper

# import Statement classes
from statement_types import AppleCard
from statement_types import Marcus
from statement_types import Robinhood
from statement_types import WellsCredit
from statement_types import WellsChecking
from statement_types import WellsSaving
from statement_types import VanguardBrokerage
from statement_types import VanguardRoth
from statement_types import Venmo



# TODO:
#   - add cash recording
#   - add ability to split up a transaction into two different categories


class tabFinanceData:
    def __init__(self, master):
        # tkinter frame stuff
        self.master = master
        self.frame = tk.Frame(self.master)
        self.fr_date_selection = tk.Frame(self.frame)
        self.fr_load_ticker_info = tk.Frame(self.frame)

        self.prompt = Text(self.frame, padx=5, pady=5, height=5)

        self.load_yes = 0  # yes button to loading statement data
        self.load_no = 0  # no button for loading statement data

        self.statement = 0
        # TODO: figure out how to delete the below two variables. Call grid_destroy and regenerate?
        self.files_drop = 0
        self.account_drop = 0

        self.initTabContent()

    # initTabContent: initializes the main content of the tab
    def initTabContent(self):
        print("Initializing tab 4 content")

        # initialize date selection
        self.fr_date_selection.grid(row=0, column=0)
        self.init_fr_date_selection()

    # init_date_selection_content: initializes the date and year drop down
    def init_fr_date_selection(self):
        # print frame title
        Label(self.fr_date_selection, text="Choose Statement Date", font=("Arial", 16)).grid(row=0, column=0, columnspan=5, padx=3, pady=3)

        # set up top row of text labels
        label = Label(self.fr_date_selection, text="Select Year")
        label.grid(row=1, column=0)
        label = Label(self.fr_date_selection, text="Select Month")
        label.grid(row=1, column=1)

        # set up user inputs for statement (year and month)
        year_dropdown = gui_helper.generateYearDropDown(self.fr_date_selection)
        year_dropdown[0].grid(row=2, column=0)
        month_dropdown = gui_helper.generateMonthDropDown(self.fr_date_selection)
        month_dropdown[0].grid(row=2, column=1)

        # set up button to start generate list of files in certain month/year directory
        gen_file_drop = Button(self.fr_date_selection, text="Select Month",
                               command=lambda: self.show_account_file_select(self.fr_date_selection, year_dropdown[1].get(), month_dropdown[1].get()))
        gen_file_drop.grid(row=2, column=3)


    # show_account_file_select: grabs files from a certain month and display drop down
    def show_account_file_select(self, frame, year, month):
        ### show account information stuff ###
        # add label
        label = Label(frame, text="Month Files")
        label.grid(row=3, column=0)

        # delete previous month files drop down
        if self.files_drop != 0:
            self.files_drop.grid_remove()

        if self.account_drop != 0:
            self.account_drop.grid_remove()

        # create and place new file dropdown
        base_path = "C://Users//ander//OneDrive//Documents//Financials"
        dir_path = gui_helper.get_statement_folder(base_path, year, month)
        dir_list = os.listdir(dir_path)

        if len(dir_list) == 0:
            gui_helper.alert_user("No files found", "Uh oh, no files were found in selected month's file folder", "error")
            return

        # create drop down of files
        clicked_file = StringVar()  # datatype of menu text
        clicked_file.set(dir_list[0])
        self.files_drop = OptionMenu(frame, clicked_file, *dir_list)
        self.files_drop.grid(row=3, column=1)

        # place drop down for statement type
        accounts = db_helper.get_account_ledger_data()

        clicked_account = StringVar()  # datatype of menu text
        clicked_account.set(accounts[0])  # initial menu text
        self.account_drop = OptionMenu(frame, clicked_account, *accounts)  # create drop down menu of accounts
        self.account_drop.grid(row=3, column=2)

        # set up button to start loading in file data
        gen_file_drop = Button(frame, text="Select File",
                               command=lambda: self.load_statement(clicked_file.get(), clicked_account.get()[1:11], year, month))
        gen_file_drop.grid(row=3, column=3)

        ### show file status stuff ###
        self.check_month_data_status(month, year)


    # TODO: move this out of here
    # creates an array of true/false depending on if data seems to have been loaded in or not
    def check_month_data_status(self, month, year):
        ### create T/F table for account_ids
        account_stats = []
        for account_id in db_helper.get_all_account_ids():
            account_stats.append([account_id, load_helper.check_account_load_status(account_id, month, year, printmode=None)])

        ### draw red/yellow/green boxes
        # create an inner window
        width = 1000
        height = 75
        frame = tk.Frame(self.fr_date_selection)
        frame.grid(row=4, column=0, columnspan=4)
        cv = Canvas(frame, bg="gray", width=width, height=height)
        cv.grid(row=0, column=0)

        # set rectangle parameters
        width_rec = width/len(account_stats)

        i = 0
        for stats in account_stats:
            # create a rectangle representing status
            if stats[1] == 0:
                color = 'red'
            elif stats[1] == 1:
                color = 'green'
            elif stats[1] == 2:
                color = 'yellow'

            cv.create_rectangle(width_rec*i + 10, 10, width_rec*i + width_rec - 15, height - 10, fill=color)
            cv.create_text(width_rec * i + width_rec / 2, height / 2, text=db_helper.get_account_name_from_id(stats[0]),
                           fill="black")
            i += 1


    def load_statement(self, file_name, account_id, year, month):
        account_id = int(account_id)  # unsure if this is needed or not
        month_int = date_helper.month2Int(month)

        #try:
        # TODO: can I figure out a way to not hard code this in?
        if account_id == 2000000001:  # Marcus
            stat = Marcus.Marcus(self.frame, account_id, year, month_int, file_name, 5, 0)
            if not stat.create_statement_data():
                gui_helper.alert_user("Error with loading statement", "Something went wrong loading this statement")
            stat.createStatementTable()  # creates a statement table at position (7, 0) *(row, column)
        elif account_id == 2000000002:
            stat = WellsChecking.WellsChecking(self.frame, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
            stat.createStatementTable()  # creates a statement table at position (7, 0) *(row, column)
        elif account_id == 2000000003:
            stat = WellsSaving.WellsSaving(self.frame, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
            stat.createStatementTable()  # creates a statement table at position (7, 0) *(row, column)
        elif account_id == 2000000004:
            stat = WellsCredit.WellsCredit(self.frame, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
            stat.createStatementTable()  # creates a statement table at position (7, 0) *(row, column)
        elif account_id == 2000000005:  # Vanguard Brokerage
            stat = VanguardBrokerage.VanguardBrokerage(self.frame, account_id, year, month_int, file_name, 5, 0)
            if not stat.create_statement_data():
                gui_helper.alert_user("Error with loading statement", "Something went wrong loading this statement")
            stat.createStatementTable()  # creates a statement table at position (7, 0) *(row, column)
        elif account_id == 2000000006:  # Vanguard Roth
            stat = VanguardRoth.VanguardRoth(self.frame, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
            stat.createStatementTable()  # creates a statement table at position (7, 0) *(row, column)
        elif account_id == 2000000007:  # Venmo
            stat = Venmo.Venmo(self.frame, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
            stat.createStatementTable()  # creates a statement table at position (7, 0) *(row, column)
        elif account_id == 2000000008:  # Robinhood
            stat = Robinhood.Robinhood(self.frame, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
            stat.createStatementTable(6, 0)  # creates a statement table at position (7, 0) *(row, column)
        elif account_id == 2000000009:  # Apple Card
            stat = AppleCard.AppleCard(self.frame, account_id, year, month_int, file_name, 5, 0)
            stat.create_statement_data()
            stat.createStatementTable()  # creates a statement table at position (7, 0) *(row, column)
        else:
            raise Exception("No valid account selected in guiTab_loadSpendingData: load_statement")
            gui_helper.alert_user("Error in code account binding", "No valid Statement Class exists for the selected account ID", "error")
        #except Exception as e:
        #    gui_helper.alert_user("Statement creation failed", e, "error")