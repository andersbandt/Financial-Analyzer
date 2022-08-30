# import needed packages
import tkinter as tk
from tkinter import *
from tkcalendar import *
from tkinter import ttk

from functools import partial
import lambdas

# import user defined modules
from Statement_Classes import Statement
from Statement_Classes import Transaction

from Finance_GUI import gui_helper
from categories import category_helper
from analyzing import analyzer_helper
from analyzing import graphing_analyzer
from databases import database_helper
from Scraping import scraping_helper


class tabSpendingHistory:
    def __init__(self, master, conn):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.date_select_frame = tk.Frame(self.frame, bg="blue", highlightcolor="red")
        self.date_select_row_pos = 0
        self.date_select_col_pos = 0
        self.date_select_frame.grid(row=self.date_select_row_pos, column=self.date_select_col_pos)

        # create prompt for console output
        self.prompt = Text(self.frame, padx=5, pady=5, height=5)

        # current transaction for analyzing
        self.transactions = []

        # current accounts we are analyzing
        self.accounts = []

        # stuff for handling GUI table
        self.frame_data = 0
        self.labels = []
        self.clicked_category = []  # holds all the user set categories

        # establish SQl database properties
        self.conn = conn
        self.cur = self.conn.cursor()

        # load Category objects
        self.categories = category_helper.load_categories()

        self.initTabContent()


# initTabContent: initializes the main content of the tab
    # for this tab, most of the initial content is date and account selection for recalling data
    def initTabContent(self):
        print("Initializing tab 2 content")

        # set up top row of text labels
        label = Label(self.date_select_frame, text="Select Start Date")
        label.grid(row=0, column=1)
        label = Label(self.date_select_frame, text="Select End Date")
        label.grid(row=0, column=2)
        label = Label(self.date_select_frame, text="Select Accounts (please toggle one result each query)")
        label.grid(row=0, column=3)

        # set up calendar pick for start search date
        fone = Frame(self.date_select_frame)
        fone.grid(row=1, column=1)

        cal_start = Calendar(
            fone,
            selectmode="day",
            year=2022,
            month=1,
            day=1
        )
        cal_start.grid(row=0, column=0, padx=10, pady=5)

        # set up calendar pick for end search date
        ftwo = Frame(self.date_select_frame)
        ftwo.grid(row=1, column=2)

        cal_end = Calendar(
            ftwo,
            selectmode="day",
            year=2022,
            month=1,
            day=1
        )
        cal_end.grid(row=0, column=0, padx=10, pady=5)

        # create checkbox list for accounts
        account_checkbox_frame = Frame(self.date_select_frame)
        account_checkbox_frame.grid(row=1, column=3)

        account_data = database_helper.get_account_ledger_data()

        # function for updating current accounts in checkbox
        def on_select(vars):
            self.accounts = []
            for var in vars:
                account_id = int(var.get())
                self.accounts.append(account_id)

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
        start_analyzing = Button(self.date_select_frame, text="Recall Data", command=lambda: self.analyze_history(cal_start.get_date(), cal_end.get_date(), self.accounts))
        start_analyzing.grid(row=1, column=4, padx=10, pady=5)  # place 'Start Categorizing' button


    def analyze_history(self, date_start, date_end, accounts):
        print("analyze_history got this for date_start:", date_start)
        print("analyze_history got this for date_end:", date_end)
        print("analyze_history got this for accounts", accounts)

        # format the date strings
        formatted_start = scraping_helper.format_date_string(date_start)
        formatted_end = scraping_helper.format_date_string(date_end)

        # recall transaction data and display it on the frame
        self.transactions = []
        self.transactions = analyzer_helper.recall_transaction_data(self.conn, formatted_start, formatted_end, accounts)

        if self.transactions is None:
            print("Recalled 0 transactions. Exiting")
            return False
        else:
            self.date_select_frame.grid_forget()  # hide the date selection Frame
            self.display_data()
            new_frame = (tk.Frame(self.master))
            new_frame.grid(row=4, column=0)
            self.show_graphical_processing_gui(new_frame)
            return True


    # TODO: I think it will be easier to create a basic class for displaying transaction data, then statement will inherit from that
    # display_data: displays data in a table format from a certain transaction date range
    #   and certain accounts
    def display_data(self):
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

        self.clicked_category = [StringVar(self.frame_data) for i in range(rows)]  # initialize StringVar entries for OptionMenus

        # place data for each transaction in a separate row
        for i in range(0, rows):
            # get dictionary containing string items
            string_dict = self.transactions[i].getStringDict()

            # place labels for each item variable (except category)
            self.labels[i][0] = tk.Label(self.frame_data, text=string_dict["date"])
            self.labels[i][1] = tk.Label(self.frame_data, text=string_dict["description"])
            self.labels[i][2] = tk.Label(self.frame_data, text=string_dict["amount"])
            self.labels[i][3] = tk.Label(self.frame_data, text=category_helper.category_id_to_name(string_dict["category"]))
            self.labels[i][4] = tk.Label(self.frame_data, text=database_helper.get_account_name_from_id(string_dict["source"]))

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

        # set up button to save the recalled financial data
        save_statement = Button(self.frame, text="Save Financial Data", command=lambda: self.save_data())
        save_statement.grid(row=5, column=3)

        # set up button to delete all the recalled data from the tab
        save_statement = Button(self.frame, text="Discard Recalled Financial Data", command=lambda: self.discard_data())
        save_statement.grid(row=6, column=3)

        print("Reached end of display_data")
        return True


    def show_graphical_processing_gui(self, frame):
        print("Running guiTab_analyzeSpendingHistory: show_graphical_processing_gui")

        # set up button to show pie chart of all categories and expenses
        show_pie_chart_button = Button(frame, text="Show Pie Chart", command=lambda: graphing_analyzer.create_pie_chart(self.transactions,
                                                                                        category_helper.load_categories(self.conn)))
        show_pie_chart_button.grid(row=0, column=0)
        # set up button to show pie chart of all categories and expenses
        show_bar_chart_button = Button(frame, text="Show Bar Chart", command=lambda: graphing_analyzer.create_bar_chart(self.transactions,
                                                                                        category_helper.load_categories(self.conn)))
        show_bar_chart_button.grid(row=0, column=1)

        # set up button to show a summary over time of the transactions recalled
        show_summation_button = Button(frame, text="Show Sums over Time", command=lambda: graphing_analyzer.create_summation_vs_time(self.transactions,
                                                                                        category_helper.load_categories(self.conn)))
        show_summation_button.grid(row=0, column=2)


    # change_transaction_category
    def change_transaction_category(self, index):
        gui_helper.gui_print(self.frame, self.prompt, "Changing transaction number " + str(index) + " to category: " + self.clicked_category[index].get())
        category_id = category_helper.category_name_to_id(self.conn, self.clicked_category[index].get())
        self.transactions[index].setCategory(category_id)
        return


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


    # discard data
    def discard_data(self):
        print("Discarding recalled transaction data")
        self.frame_data.grid_forget()
        #self.frame_data.destroy()

        # re show the date selection frame
        self.date_select_frame.grid(row=self.date_select_row_pos, column=self.date_select_col_pos)  # hide the date selection Frame











