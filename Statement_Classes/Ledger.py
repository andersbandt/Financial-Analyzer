# import needed modules
import tkinter as tk
from tkinter import *

from functools import partial
import sqlite3

# import user defined modules
from Finance_GUI import gui_helper
from categories import category_helper
from Statement_Classes import Transaction
from db import db_helper

# TODO: add dropdown where you can 'sort by' for the transactions
#   examples - sort by ascending, descending, category,
class Ledger:
    def __init__(self, master, title, row_num, column_num, *args, **kwargs):
        # set ledger variables
        self.title = title

        # init ledger data variables
        self.transactions = []
        self.clicked_category = []  # holds all the user set categories

        # initialize general GUI variables
        self.master = master
        self.frame = tk.Frame(self.master, bg="#194d33")
        self.frame.grid(row=row_num, column=column_num)
        self.prompt = Text(self.frame, padx=10, pady=10, height=5)
        self.prompt.grid(row=2, column=0, rowspan=3)

        # initialize more GUI content for table
        self.frame_canvas = 0
        self.canvas = 0
        self.vsb = 0
        self.frame_data = 0

        # get categories # TODO: get rid of this
        self.categories = category_helper.load_categories()


    ##############################################################################
    ####      DATA LOADING FUNCTIONS    ##########################################
    ##############################################################################

    # set_statement_data: sets the transaction data
    def set_statement_data(self, transactions):
        self.transactions = transactions


    ##############################################################################
    ####      CATEGORIZATION FUNCTIONS    ########################################
    ##############################################################################

    # categorizeStatementAutomatic: adds a category label to each statement array based predefined
    def categorizeLedgerAutomatic(self):
        for transaction in self.transactions:
            transaction.categorizeTransactionAutomatic(self.categories)


    ##############################################################################
    ####      DATA SAVING FUNCTIONS    ###########################################
    ##############################################################################

    # saveStatement: saves a categorized statement as a csv
    def saveStatement(self):
        gui_helper.gui_print(self.frame, self.prompt, "Attempting to save statement")
        response = gui_helper.promptYesNo("Are you sure you want to change this set of data?")
        if response is False:
            gui_helper.gui_print(self.frame, self.prompt, "Ok, not saving statement")
            return False
        else:
            error_status = 0
            for transaction in self.transactions:
                success = db_helper.update_transaction(transaction)
                if success == 0:
                    error_status = 1

            if error_status == 1:
                gui_helper.alert_user("Error in ledger adding!", "At least 1 thing went wrong adding to ledger")
                return False
            else:
                gui_helper.gui_print(self.frame, self.prompt, "Saved statement")
            return True


    ##############################################################################
    ####      ORDERING FUNCTIONS    ##############################################
    ##############################################################################

    # sort:trans_asc: sorts the transactions by amount ascending (highest to lowest)
    def sort_trans_asc(self):
        sorted_trans = sorted(self.transactions, key=lambda t: t.amount)
        self.transactions = sorted_trans

    #sort_trans_desc: sorts the transaction by amount descending (lowest to highest)
    def sort_trans_desc(self):
        sorted_trans = sorted(self.transactions, key=lambda t: t.amount, reverse=True)
        self.transactions = sorted_trans

    ##############################################################################
    ####      PRINTING FUNCTIONS    ##############################################
    ##############################################################################

    # printStatement: pretty prints a statement
    def printStatement(self):
        print("Statement", self.title)
        for transaction in self.transactions:
            transaction.printTransaction()


    ##############################################################################
    ####      INTERACTIVE GUI FUNCTIONS    #######################################
    ##############################################################################

    # change_transaction_category
    def change_transaction_category(self, index, *args):
        gui_helper.gui_print(self.frame, self.prompt, "Changing transaction number " + str(index) + " to category: " + self.clicked_category[index].get())
        category_id = category_helper.category_name_to_id(self.clicked_category[index].get())
        self.transactions[index].setCategory(category_id)
        return

# TODO: add headers (date, account, etc.)
# TODO: figure out how to turn account_id into name
    # createStatementTable: creates a table representing all the loaded in transactions
    def createStatementTable(self):
        # initialize the Tkinter gui stuff for table creation
        self.init_ledger_table()

        # run function to populate the top row of data
        self.pop_ledger_top_row()

        # Populate statement data and update table sizing
        labels = self.pop_ledger_data()
        self.update_ledger_sizing(labels)

        # TODO : add update statement button

        # place button for deleting statement
        delete_statement = Button(self.frame, text="Delete Statement", command=self.delete_statement)
        delete_statement.grid(row=4, column=1)

        # place button for saving statement
        save_statement = Button(self.frame, text="Save Statement", command=self.save_statement)
        save_statement.grid(row=5, column=1)


    def init_ledger_table(self):
        # Create a frame for the canvas with non-zero row+column weights
        self.frame_canvas = tk.Frame(self.frame)
        self.frame_canvas.grid(row=1, column=0, pady=(5, 0), padx=10, sticky='nw', columnspan=2)
        self.frame_canvas.grid_rowconfigure(0, weight=1)
        self.frame_canvas.grid_columnconfigure(0, weight=1)

        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        self.frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        self.canvas = tk.Canvas(self.frame_canvas, bg="yellow", height=30)
        self.canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        self.vsb = tk.Scrollbar(self.frame_canvas, orient="vertical", command=self.canvas.yview)
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Create a frame to contain the statement data
        self.frame_data = tk.Frame(self.canvas, bg="blue")
        self.canvas.create_window((0, 0), window=self.frame_data, anchor='nw')


    #pop_ledger_top_row: populates the ledger's top row of information
    def pop_ledger_top_row(self, *args):
        if len(args) > 0:
            for arg in args:
                print(arg)

        # write title
        Label(self.frame, text=self.title, font=("Arial", 16)).grid(row=0, column=0)

        ### add option for changing transaction sort method
        def change_sort(option):
            option = variable.get()
            print("change_sort received this as a command:", option)
            self.sort_trans_asc()

        # add button dropdown for sorting ledger data
        sort_options = ["Date Descending", "Amount Ascending", "Amount Descending"]

        # set variable for sorting options
        variable = StringVar()
        variable.set(sort_options[0])

        # create dropdown
        dropdown = tk.OptionMenu(
            self.frame,
            variable,
            *sort_options,
            command= change_sort
        )
        dropdown.grid(row=0, column=1)


    def pop_ledger_data(self):
        rows = len(self.transactions)
        columns = 5
        labels = [[tk.Label() for j in range(columns)] for i in range(rows)]

        self.clicked_category = [StringVar(self.frame_data) for i in
                                 range(rows)]  # initialize StringVar entries for OptionMenus

        # place data for each transaction in a separate row
        for i in range(0, rows):
            # get dictionary containing string items
            string_dict = self.transactions[i].getStringDict()

            # place labels for each item variable (except category)
            labels[i][0] = tk.Label(self.frame_data, text=string_dict["date"])
            labels[i][1] = tk.Label(self.frame_data, text=string_dict["description"])
            labels[i][2] = tk.Label(self.frame_data, text=string_dict["amount"])
            labels[i][4] = tk.Label(self.frame_data, text=string_dict["source"])

            # if the transaction does not yet have a category
            if string_dict["category"] == 0:
                self.clicked_category[i] = StringVar(self.frame_data)  # datatype of menu text
                self.clicked_category[i].set("Please select a category")  # initial menu text

                self.clicked_category[i].trace("w", partial(self.change_transaction_category, i))

                labels[i][3] = tk.OptionMenu(self.frame_data, self.clicked_category[i], *(category_helper.get_category_strings(self.categories)))

            # if the transaction already has a category assigned
            else:
                labels[i][3] = tk.Label(self.frame_data, text=category_helper.category_id_to_name(string_dict["category"]))

            # place all the components for the transaction we are handling
            for j in range(0, columns):
                labels[i][j].grid(row=i, column=j, sticky='news')

        return labels


    def update_ledger_sizing(self, labels):
        # Update buttons frames idle tasks to let tkinter calculate sizes
        self.frame_data.update_idletasks()

        # Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
        first_columns_width = sum([labels[0][j].winfo_width() for j in range(0, 5)])
        first_rows_height = sum([labels[i][0].winfo_height() for i in range(0, min(len(self.transactions), 15))])  # this number (15) sets number of rows displayed
        self.frame_canvas.config(width=first_columns_width + self.vsb.winfo_width(), height=first_rows_height)

        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))



    ##############################################################################
    ####      DATA SAVING FUNCTIONS    ###########################################
    ##############################################################################

    # TODO: make green/red checkmarks update upon completion of this (for Statement only)
    # saveStatement: saves a categorized statement as a csv
    def save_statement(self):
        gui_helper.gui_print(self.frame, self.prompt, "Attempting to save statement...")
        if self.check_statement_status(self.transactions):
            response = gui_helper.promptYesNo("It looks like a saved statement for " + self.title + " already exists, are you sure you want to overwrite by saving this one?")
            if response is False:
                gui_helper.gui_print(self.frame, self.prompt, "Ok, not saving statement")
                return False
        else:
            error_status = 0
            for transaction in self.transactions:
                success = db_helper.insert_transaction(transaction)
                if success == 0:
                    error_status = 1

            if error_status == 1:
                gui_helper.alert_user("Error in ledger adding!", "At least 1 thing went wrong adding to ledger")
                return False
            else:
                gui_helper.gui_print(self.frame, self.prompt, "Saved statement")
            return True


    ##############################################################################
    ####      GENERAL HELPER FUNCTIONS    ########################################
    ##############################################################################

    # delete_statement: deletes statement from master frame
    def delete_statement(self):
        print("Deleting ledger", self.title)
        self.frame.grid_forget()
        self.frame.destroy()


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



