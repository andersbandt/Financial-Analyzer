
# import needed modules
import tkinter as tk
from tkinter import *

import keyboard
from functools import partial  # needed adding callback functions with correct variables in for loops

# import user defined modules
from gui import gui_helper
from categories import categories_helper
from db import db_helper


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

        # NOTE: frame_canvas goes at (row=1, column=0)
        # Frame for Ledger statistics
        #self.fr_stat = tk.Frame(self.frame).grid(row=2, column=1)

        # Frame for Ledger actions
        self.fr_action = tk.Frame(self.frame)
        self.fr_action.grid(row=2, column=1)
        self.fr_sel_action = tk.Frame(self.frame)
        self.fr_sel_action.grid(row=2, column=2)

        # prompt for text output
        self.prompt = Text(self.frame, padx=10, pady=10, height=5)
        self.prompt.grid(row=2, column=0, padx=10, pady=10)

        # initialize more GUI content for table
        self.frame_canvas = 0
        self.canvas = 0
        self.vsb = 0
        self.frame_data = 0

        # selected transactions
        self.sel_trans = []  # stores the sql key of selected transactions
        self.m_sel_ind = [0] * 2  # for storing a group select ('shift' key down) of multiple transactions. This stores transaction # NOT sql key

        # get categories  # TODO: get rid of this
        #self.categories = category_helper.load_categories()


    ##############################################################################
    ####      DATA LOADING FUNCTIONS    ##########################################
    ##############################################################################

    # set_statement_data: sets the transaction data
    def set_statement_data(self, transactions):
        self.transactions = transactions


    ##############################################################################
    ####      DATA LOADING FUNCTIONS    ##########################################
    ##############################################################################

    # del_sel_trans: deletes selected transactions DIRECTLY from the SQL database
    def del_sel_trans(self):
        # print out what transactions we are deleting
        print("Deleting the transactions with the following sql keys: ")
        print(self.sel_trans)

        gui_helper.gui_print(self.frame, self.prompt, "Deleting the transactions with the following sql keys: ")
        gui_helper.gui_print(self.frame, self.prompt, self.sel_trans)

        # go through selected Transactions and delete
        for sql_key in self.sel_trans:
            db_helper.delete_transaction(sql_key)
        return

    ##############################################################################
    ####      CATEGORIZATION FUNCTIONS    ########################################
    ##############################################################################

    # categorizeStatementAutomatic: adds a category label to each statement array based predefined
    def categorizeLedgerAutomatic(self):
        categories = categories_helper.load_categories()
        for transaction in self.transactions:

            transaction.categorizeTransactionAutomatic(categories)
        return


    ##############################################################################
    ####      ORDERING FUNCTIONS    ##############################################
    ##############################################################################

    # sort:trans_asc: sorts the transactions by amount ascending (highest to lowest)
    def sort_trans_asc(self):
        sorted_trans = sorted(self.transactions, key=lambda t: t.amount)
        self.transactions = sorted_trans

        # Populate statement data and update table sizing
        labels = self.pop_ledger_data()
        self.update_ledger_sizing(labels)

    #sort_trans_desc: sorts the transaction by amount descending (lowest to highest)
    def sort_trans_desc(self):
        sorted_trans = sorted(self.transactions, key=lambda t: t.amount, reverse=True)
        self.transactions = sorted_trans

        # Populate statement data and update table sizing
        labels = self.pop_ledger_data()
        self.update_ledger_sizing(labels)

    def sort_date_asc(self):
        pass

    # TODO: finish these date sorting functions
    def sort_date_desc(self):
        pass

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
        category_id = categories_helper.category_name_to_id(self.clicked_category[index].get())
        self.transactions[index].setCategory(category_id)
        return


# TODO: add headers (date, account, etc.)
    # createStatementTable: creates a table representing all the loaded in transactions
    #   this is the main function for displaying any Ledger on the master GUI frame #  TODO: refactor it so there is another main
    def createStatementTable(self):
        # initialize the Tkinter gui stuff for table creation
        self.init_ledger_table()

        # run function to populate the top row of data
        self.pop_ledger_top_row()

        # Populate statement data and update table sizing
        labels = self.pop_ledger_data()
        self.update_ledger_sizing(labels)

        # place button for deleting statement
        delete_statement = Button(self.fr_action, text="Delete Statement", command=self.delete_statement)
        delete_statement.grid(row=0, column=0, padx=10, pady=10)

        # place button for saving statement
        save_statement = Button(self.fr_action, text="Update Statement", command=self.save_statement)
        save_statement.grid(row=1, column=0, padx=10, pady=10)

        # place button for DELETING the SELECTED Transactions only
        del_sel = Button(self.fr_sel_action, text="Delete Selected Transactions", command=self.del_sel_trans)
        del_sel.grid(row=0, column=0, padx=10, pady=10)


    # init_ledger_table: creates GUI elements for Ledger table (canvas, scrollbar, Frame)
    def init_ledger_table(self):
        # Create a frame for the canvas with non-zero row+column weights
        self.frame_canvas = tk.Frame(self.frame)
        self.frame_canvas.grid(row=1, column=0, pady=(5, 0), padx=10, sticky='nw', columnspan=5)
        self.frame_canvas.grid_rowconfigure(0, weight=1)
        self.frame_canvas.grid_columnconfigure(0, weight=1)

        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        self.frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        self.canvas = tk.Canvas(self.frame_canvas, height=30)
        self.canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        self.vsb = tk.Scrollbar(self.frame_canvas, orient="vertical", command=self.canvas.yview)
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Create a frame to contain the statement data
        self.frame_data = tk.Frame(self.canvas, bg="blue")
        self.canvas.create_window((0, 0), window=self.frame_data, anchor='nw')


    # pop_ledger_top_row: populates the ledger's top row of information
    #   this includes stuff like the title and sort options
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

            if option == "Amount Ascending":
                self.sort_trans_asc()
            elif option == "Amount Descending":
                self.sort_trans_desc()
            elif option == "Date Ascending":
                self.sort_date_asc()
            elif option == "Date Descending":
                self.sort_date_desc()

        # add button dropdown for sorting ledger data
        sort_options = ["Date Ascending", "Date Descending", "Amount Ascending", "Amount Descending"]

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
        columns = 6  # trans number, date, description, amount, category, account
        labels = [[tk.Label() for j in range(columns)] for i in range(rows)]  # populate 2D array of labels
        #labels = [[0] * columns] * rows

        #self.clicked_category = [StringVar(self.frame_data) for i in range(rows)]  # initialize StringVar entries for OptionMenus
        self.clicked_category = [0] * rows
        categories = categories_helper.load_categories()

        # place data for each transaction in a separate row
        for i in range(0, rows):
            # get dictionary containing string items
            string_dict = self.transactions[i].getStringDict()

            ### place labels for each item variable (except category)
            # transaction number
            def trans_callback(i, sql_key, button_press):
                shift_key_down = keyboard.is_pressed('shift')

                if shift_key_down:
                    print("Detected that the shift key is down!")
                    self.m_sel_ind.append(i)  # append the NUMBER of the transaction (note SQL key)

                # check for if two points of mass selection of Transactions occurred
                if len(self.m_sel_ind) == 2:
                    for j in range(self.m_sel_ind[0]+1, self.m_sel_ind[1]+1):
                        labels[j][0].config(bg="blue")
                        self.sel_trans.append(self.transactions[j].sql_key)
                    self.m_sel_ind = []
                else:
                    labels[i][0].config(bg="blue")
                    if not shift_key_down:
                        self.m_sel_ind = []
                        self.m_sel_ind.append(i)
                    self.sel_trans.append(sql_key)

            labels[i][0] = tk.Label(self.frame_data, text=str(i+1))
            labels[i][0].bind('<Double-Button-1>', partial(trans_callback, i, string_dict["sql_key"]))  # lambda 'x': needed because ButtonPress state is called back. Ex: <ButtonPress event state=Mod1 num=1 x=16 y=18>

            # date, description, and amount
            labels[i][1] = tk.Label(self.frame_data, text=string_dict["date"])  # date
            labels[i][2] = tk.Label(self.frame_data, text=string_dict["description"])  # description
            labels[i][3] = tk.Label(self.frame_data, text=string_dict["amount"])  # amount

            # account info
            account_name = db_helper.get_account_name_from_id(string_dict["source"])
            labels[i][5] = tk.Label(self.frame_data, text=account_name)

            ### if the transaction does not yet have a category
            if string_dict["category"] == 0:
                self.clicked_category[i] = StringVar(self.frame_data)  # datatype of menu text
                self.clicked_category[i].set("Please select a category")  # initial menu text
                self.clicked_category[i].trace("w", partial(self.change_transaction_category, i))
                labels[i][4] = tk.OptionMenu(self.frame_data, self.clicked_category[i],
                                             # TODO
                                             *(categories_helper.get_category_strings(categories)))

            # if the transaction already has a category assigned
            else:
                labels[i][4] = tk.Label(self.frame_data, text=categories_helper.category_id_to_name(string_dict["category"]))

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

    # save_statement: saves a categorized statement as a csv
    #   in the case of a Ledger, this is more like an "update" statement
    def save_statement(self):
        # prompt user to verify desire to update ledger data
        gui_helper.gui_print(self.frame, self.prompt, "Attempting to save Ledger...")
        response = gui_helper.promptYesNo("Are you sure you want to update this data?")
        if response is False:
            gui_helper.gui_print(self.frame, self.prompt, "Ok, not saving ledger data")
            return False
        else:
            error_status = 0
            for transaction in self.transactions:
                success = db_helper.update_transaction(transaction)
                if success == 0:
                    error_status = 1

        # more error handling and debug
        if error_status == 1:
            gui_helper.alert_user("Error in ledger adding!", "At least 1 thing went wrong adding to ledger")
            return False
        else:
            gui_helper.gui_print(self.frame, self.prompt, "Saved Ledger")
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



