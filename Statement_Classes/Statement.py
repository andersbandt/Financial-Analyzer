# import needed modules
import tkinter as tk
from tkinter import *

from functools import partial
import sqlite3

# import user defined modules
from Finance_GUI import gui_helper
from categories import category_helper
from Statement_Classes import Transaction


class Statement:
    def __init__(self, master, conn, account_id, year, month, file, row_num, column_num, *args, **kwargs):
        # initialize identifying statement info
        self.account_id = account_id
        self.year = year
        self.month = month
        self.name = str(self.account_id) + ":" + str(self.year) + "-" + str(self.month)

        # load in statement filepath info
        self.base_filepath = "C:/Users/ander/OneDrive/Documents/Financials"
        self.filepath = gui_helper.get_statement_folder(self.base_filepath, year, month) + file  # generate filepath of .csv file to download

        # init statement data content
        self.transactions = []
        self.clicked_category = []  # holds all the user set categories

        # initialize gui content
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.grid(row=row_num, column=column_num)
        self.prompt = Text(self.frame, padx=5, pady=5, height=10)
        self.prompt.grid(row=4, column=0)

        # get database info
        self.conn = conn
        self.cur = self.conn.cursor()

        # get categories
        self.categories = category_helper.load_categories(self.conn)


    ##############################################################################
    ####      DATA LOADING FUNCTIONS    ##########################################
    ##############################################################################

    # create_statement_data: combines and automatically categorizes transactions across all raw account statement data
    def create_statement_data(self):
        if self.check_statement_status(self.load_statement_data()):
            gui_helper.gui_print(self.master, self.prompt, "Uh oh, looks like data already exists for this particular statement")
            res = gui_helper.promptYesNo("Data might already be loaded in for this statement... do you want to continue?")
            if not res:
                gui_helper.gui_print(self.master, self.prompt, "Ok, not loading in statement")

        print("Creating statement data for", self.name)
        self.transactions.extend(self.load_statement_data())

        # check for if transactions actually got loaded in
        if len(self.transactions) == 0:
            gui_helper.gui_print(self.master, self.prompt, "Uh oh, something went wrong retrieving transactions. Likely the transaction data is corrupt and resulted in 0 transactions. Exiting statement data creation.")
            return False

        gui_helper.gui_print(self.master, self.prompt, "Loaded in raw transaction data, running categorizeStatementAutomatic() now!")

        self.categorizeStatementAutomatic()  # run categorizeStatementAutomatic on the transactions

        self.createStatementTable(6, 0)  # creates a statement table at position (7, 0) *(row, column)

        #if self.checkNA():
        #    if gui_helper.promptYesNo("NA (category-less) entries detected in statement. Would you like to start user categorization?"):
        #        self.userCategorize()
        #    else:
        #        gui_helper.gui_print(self.master, self.prompt, "Ok, not manually categorizing statement")

    # load_statement_data: this function should be defined per account's Statement class
    # DO NOT DELETE
    def load_statement_data(self):
        pass

    # TODO: failing when I try to load in Marcus statement data... however it is loading in erroneously
    # check_statement_status: returns True if data already exists for this statement, False otherwise
    def check_statement_status(self, checking_transactions):
        # handle leading 0 for months less than 10 (before October)
        if self.month >= 10:
            month_start = str(self.year) + "-" + str(self.month) + "-" + "01"
            month_end = str(self.year) + "-" + str(self.month) + "-" + "31"
        else:
            month_start = str(self.year) + "-" + "0" + str(self.month) + "-" + "01"
            month_end = str(self.year) + "-" + "0" + str(self.month) + "-" + "31"

        # get length of number of transactions within the month's date range per account
        try:
            self.conn.set_trace_callback(print)
            self.cur.execute("SELECT * FROM ledger WHERE (trans_date BETWEEN ? AND ?) AND account_id = ?", (month_start, month_end, self.account_id))
            results = self.cur.fetchall()
            self.conn.set_trace_callback(None)
        # conn.set_trace_callback(print)
        except sqlite3.Error as e:
            print(e)

        # compare to loaded length of transactions
        if len(results) == len(checking_transactions):
            if len(results) != 0: # prevents alerting when data might not be loading in correctly
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

    # promptUserCategorize: prompts a user to categorize a specific item
    # input: categories
    # input: transaction (transaction to be categorized)
    # output: new transaction category index, or -1 if user wants to quit categorization
    def promptUserCategorize(self, transaction):
        gui_helper.guiPrint(self.master, self.prompt, "PLEASE CATEGORIZE THIS TRANSACTION")
        for i in range(0, len(self.categories)):
            gui_helper.guiPrint(self.master, self.prompt, str(i), " ", self.categories[i].printCategory())
        gui_helper.guiPrint(self.master, self.prompt, "Q: Quit user categorization")
        gui_helper.guiPrint(self.master, self.prompt, "S: Skip transaction")
        gui_helper.guiPrint(transaction.printTransaction())
        # category_index = input("What is the category?: ") # takes category input as index of category to assign
        category_index = -1

        if category_index == "Q":
            return -1
        elif category_index == 'S':
            return -2
        else:
            return int(category_index)

    # userCategorize: iterates through uncategorized transactions and prompts user to categorize them
    def userCategorize(self):
        for transaction in self.transactions:
            if transaction.category == "NA":
                userCategorizeResponse = self.promptUserCategorize(transaction)
                if userCategorizeResponse == -1:  # if user wants to quit categorization
                    print("Quitting user categorization")
                    return
                elif userCategorizeResponse == -2:  # if user wants to skip transaction
                    print("Transaction skipped")
                else:
                    transaction.category = self.categories[userCategorizeResponse].name

    ##############################################################################
    ####      ANALYSIS FUNCTIONS    ##############################################
    ##############################################################################



    # getExpenses: returns only the transactions with a negative value
    def getExpenses(self):
        expenses = []
        for transaction in self.transactions:
            if transaction.getAmount() < 0:
                expenses.append(transaction)

        return expenses

    # getAmountTotal: returns total sum of statement
    def getAmountTotal(self):
        total = 0
        for transaction in self.transactions:
            total += transaction.getAmount()

        return total

    ##############################################################################
    ####      DATA SAVING FUNCTIONS    ###########################################
    ##############################################################################

    # saveStatement: saves a categorized statement as a csv
    def saveStatement(self):
        if self.check_statement_status(self.load_statement_data()):
            response = self.promptYesNo(
                "It looks like a saved statement for " + self.name + " already exists, are you sure you want to overwrite by saving this one?")
            if response == "no":
                self.guiPrint("Ok, not saving statement")
                return False
        else:
            error_status = 0
            with self.conn:
                for transaction in self.transactions:
                    try:
                        self.conn.set_trace_callback(print)
                        self.cur.execute("INSERT INTO ledger (trans_date, account_id, category_id, amount, description) VALUES(?, ?, ?, ?, ?)",
                                        (transaction.date, transaction.account_id, transaction.category_id, transaction.amount, transaction.description))
                        self.conn.set_trace_callback(None)
                    except sqlite3.Error as e:
                        error_status = 1
                        gui_helper.gui_print(self.frame, self.prompt, "Q: Quit user categorization", "Uh oh, something went wrong with inserting into the ledger:", e)
                if error_status == 1:
                    gui_helper.alert_user("Error in ledger adding!", "At least 1 thing went wrong adding to ledger")

    ##############################################################################
    ####      PRINTING FUNCTIONS    ##############################################
    ##############################################################################

    # printStatement: pretty prints a statement
    def printStatement(self):
        print("Statement", self.name)
        for transaction in self.transactions:
            transaction.printTransaction()

    ##############################################################################
    ####      INTERACTIVE GUI FUNCTIONS    #######################################
    ##############################################################################

    # change_transaction_category
    def change_transaction_category(self, index, *args):
        gui_helper.gui_print(self.frame, self.prompt, "Changing transaction number " + str(index) + " to category: " + self.clicked_category[index].get())
        category_id = category_helper.category_name_to_id(self.conn, self.clicked_category[index].get())
        self.transactions[index].setCategory(category_id)
        return

    # createStatementTable
    def createStatementTable(self, row_num, column_num):
        print("Running Statement: createStatementTable()")
        # Create a frame for the canvas with non-zero row+column weights
        frame_canvas = tk.Frame(self.frame)
        frame_canvas.grid(row=row_num, column=column_num, pady=(5, 0), sticky='nw')
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        canvas = tk.Canvas(frame_canvas, bg="yellow")
        canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        vsb = tk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        canvas.configure(yscrollcommand=vsb.set)

        # Create a frame to contain the statement data
        frame_data = tk.Frame(canvas, bg="blue")
        canvas.create_window((0, 0), window=frame_data, anchor='nw')

        # TODO: somehow I have to figure out the statement sizing for extra long statements. For example, the save and delete button are not accessible
        #   at the bottom. Maybe figure out how to only display 15 or so entries at a time? HINT: LOOk at the way I do it in analyzeSpendingHistory. It works there

        # Populate statement data
        rows = len(self.transactions)
        columns = 5
        labels = [[tk.Label() for j in range(columns)] for i in range(rows)]

        self.clicked_category = [StringVar(frame_data) for i in range(rows)]  # initialize StringVar entries for OptionMenus

        # place data for each transaction in a separate row
        for i in range(0, rows):
            # get dictionary containing string items
            string_dict = self.transactions[i].getStringDict()

            # place labels for each item variable (except category)
            labels[i][0] = tk.Label(frame_data, text=string_dict["date"])
            labels[i][1] = tk.Label(frame_data, text=string_dict["description"])
            labels[i][2] = tk.Label(frame_data, text=string_dict["amount"])
            labels[i][4] = tk.Label(frame_data, text=string_dict["source"])

            # if the transaction does not yet have a category
            if string_dict["category"] == 0:
                self.clicked_category[i] = StringVar(frame_data)  # datatype of menu text
                self.clicked_category[i].set("Please select a category")  # initial menu text

                self.clicked_category[i].trace("w", partial(self.change_transaction_category, i))

                labels[i][3] = tk.OptionMenu(frame_data, self.clicked_category[i], *(category_helper.get_category_strings(self.categories)))

            # if the transaction already has a category assigned
            else:
                labels[i][3] = tk.Label(frame_data, text=category_helper.category_id_to_name(string_dict["category"]))

            # place all the components for the transaction we are handling
            for j in range(0, columns):
                labels[i][j].grid(row=i, column=j, sticky='news')

        # Update buttons frames idle tasks to let tkinter calculate sizes
        frame_data.update_idletasks()

        # Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
        first_columns_width = sum([labels[0][j].winfo_width() for j in range(0, columns)])
        first_rows_height = sum([labels[i][0].winfo_height() for i in range(0, rows)])
        frame_canvas.config(width=first_columns_width + vsb.winfo_width(), height=first_rows_height)

        # Set the canvas scrolling region
        canvas.config(scrollregion=canvas.bbox("all"))

        # place button for saving
        save_statement = Button(self.frame, text="Save Statement", command=self.saveStatement)
        save_statement.grid(row=8, column=column_num)

        # place button for deleting statement
        delete_statement = Button(self.frame, text="Delete Statement", command=self.delete_statement)
        delete_statement.grid(row=8, column=column_num+1)


    # hide_statement_gui
    # TODO: get statements to properly hide
    def delete_statement(self):
        print("Deleting statement", self.name)
        self.frame.grid_forget()
        self.frame.destroy()

    ##############################################################################
    ####      GENERAL HELPER FUNCTIONS    ########################################
    ##############################################################################


    # checkContent: checks for if any data is actually in the statement
    def checkContent(self):
        if len(self.transactions) == 0:
            return False
        else:
            return True

    # checkNA: checks if a statement contains any transactions with 'NA' as a category
    def checkNA(self):
        amount_NA = 0
        for transaction in self.transactions:
            if transaction.category_id == 0:
                amount_NA += 1

        if amount_NA > 0:
            print("Analyzed statement, contains " + str(amount_NA) + " NA entries")
            return True
        else:
            return False
