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


class tabSpendingHistory:
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
        print("Initializing tab 2 content")

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

        # set up button to start the categorization process
        start_analyzing = Button(self.date_select_frame, text="Recall Data",
                                 command=lambda: self.display_data(1, 999999999999, [0, 0]))
        start_analyzing.grid(row=1, column=3)  # place 'Start Categorizing' button


# recall_data: loads GUI elements for analyzing a selection of transaction data
    def recall_data(self, datetime_start, datetime_end, accounts):
        try:
            self.cur.execute("SELECT * FROM ledger WHERE ?<trans_date<?", (datetime_start, datetime_end))
            ledger_data = self.cur.fetchall()
        except sqlite3.Error as e:
            print("Uh oh, something went wrong recalling transaction data:", e)
            return False

        print(ledger_data)

        self.transactions = [] # clear transactions
        for item in ledger_data:
            self.transactions.append(Transaction.Transaction(item[1], item[2], item[3], item[4], item[5], item[0]))
        return True


    # display_data: displays data in a table format from a certain transaction date range
    #   and certain accounts
    def display_data(self, date_start, date_end, accounts):
        self.recall_data(date_start, date_end, accounts)

        print("Running guiTab_analyzeSpendingHistory: display_data")
        # Create a frame for the canvas with non-zero row+column weights
        frame_canvas = tk.Frame(self.frame)
        frame_canvas.grid(row=3, column=0, pady=(5, 0), sticky='nw')
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
        self.frame_data = tk.Frame(canvas, bg="blue")
        canvas.create_window((0, 0), window=self.frame_data, anchor='nw')

        # Populate statement data
        rows = len(self.transactions)
        columns = 5
        self.labels = [[tk.Label() for j in range(columns)] for i in range(rows)]

        self.clicked_category = [StringVar(self.frame_data) for i in
                                 range(rows)]  # initialize StringVar entries for OptionMenus

        # place data for each transaction in a separate row
        for i in range(0, rows):
            # get dictionary containing string items
            string_dict = self.transactions[i].getStringDict()

            # place labels for each item variable (except category)
            self.labels[i][0] = tk.Label(self.frame_data, text=string_dict["date"])
            self.labels[i][1] = tk.Label(self.frame_data, text=string_dict["description"])
            self.labels[i][2] = tk.Label(self.frame_data, text=string_dict["amount"])
            self.labels[i][3] = tk.Label(self.frame_data, text=category_helper.category_id_to_name(self.conn, string_dict["category"]))
            self.labels[i][4] = tk.Label(self.frame_data, text=string_dict["source"])

            # place all the components for the transaction we are handling
            for j in range(0, columns):
                self.labels[i][j].grid(row=i, column=j, sticky='news')

        # Update buttons frames idle tasks to let tkinter calculate sizes
        self.frame_data.update_idletasks()

        # Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
        first_columns_width = sum([self.labels[0][j].winfo_width() for j in range(0, columns)])
        first_rows_height = sum([self.labels[i][0].winfo_height() for i in range(0, 20)])
        frame_canvas.config(width=first_columns_width + vsb.winfo_width(), height=first_rows_height)

        # Set the canvas scrolling region
        canvas.config(scrollregion=canvas.bbox("all"))

        # set up button to enable editing of the statement
        edit_statement = Button(self.frame, text="Edit Financial Data", command=lambda: self.edit_data())
        edit_statement.grid(row=4, column=3)

        # set up button to save the statement
        save_statement = Button(self.frame, text="Save Financial Data", command=lambda: self.save_data())
        save_statement.grid(row=5, column=3)

        return True


    # change_transaction_category
    def change_transaction_category(self, index, *args):
        gui_helper.gui_print(self.frame, self.prompt, "Changing transaction number " + str(index) + " to category: " + self.clicked_category[index].get())
        category_id = category_helper.category_name_to_id(self.conn, self.clicked_category[index].get())
        self.transactions[index].setCategory(category_id)
        return


# TODO: I think it will be easier to create a basic class for displaying transaction data, then statement will inherit from that
    def edit_data(self):
            for i in range(0, len(self.transactions)):
                # delete previous category
                self.labels[i][3].grid_forget()

                self.clicked_category[i] = StringVar(self.frame_data)  # datatype of menu text
                self.clicked_category[i].set(category_helper.category_id_to_name(self.conn, self.transactions[i].category_id))  # initial menu text

                self.clicked_category[i].trace("w", partial(self.change_transaction_category, i))

                self.labels[i][3] = tk.OptionMenu(self.frame_data, self.clicked_category[i], *(category_helper.get_category_strings(self.categories)))

                self.labels[i][3].grid(row=i, column=3, sticky='news')


    # save the statement
    def save_data(self):
        for transaction in self.transactions:
            self.cur.execute("UPDATE ledger SET category_id=? WHERE key=?", (transaction.category_id, transaction.sql_key))

        self.display_data(1, 999999999999, [0, 0])











