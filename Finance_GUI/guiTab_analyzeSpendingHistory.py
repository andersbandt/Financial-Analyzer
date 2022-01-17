# import needed packages
import tkinter as tk
from tkinter import *
from tkinter import ttk

import lambdas

# import user defined modules
from Statement_Classes import Statement

from Finance_GUI import gui_helper


class tabSpendingHistory:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.prompt = Text(self.frame, padx=5, pady=5, height=5)

        self.load_yes = 0  # yes button to loading statement data
        self.load_no = 0  # no button for loading statement data

        self.statement = 0

        self.times_analyze_ran = 0

        self.initTabContent()


# initTabContent: initializes the main content of the tab
    def initTabContent(self):
        # set up top row of text labels
        label = Label(self.frame, text="Select Year")
        label.grid(row=0, column=0)
        label = Label(self.frame, text="Select Month")
        label.grid(row=0, column=1)

        # set up user inputs for statement (year and month)
        year_dropdown = self.generateYearDropDown()
        year_dropdown[0].grid(row=1, column=0)
        month_dropdown = self.generateMonthDropDown()
        month_dropdown[0].grid(row=1, column=1)

        # set up button to start the categorization process
        start_analyzing = Button(self.frame, text="Start Categorizing",
                                 command=lambda: self.analyzeStatement(month_dropdown[1].get(),
                                                                       year_dropdown[1].get()))
        start_analyzing.grid(row=1, column=3)  # place 'Start Categorizing' button


# analyzeStatement: loads GUI elements for analyzing a statement
    def analyzeStatement(self, month, year):
        print("Got this month: " + str(month))
        print("Got this year: " + str(year))

        if self.times_analyze_ran > 1:
            self.statement.hide_statement_gui()

        self.statement = (Statement.Statement(int(year), gui_helper.month2Int(month), self.frame, 6, 0))

        # if a statement is already created
        if self.statement.checkStatementStatus():
            print("Found a statement for " + self.statement.name)
            self.statement.loadStatement()

        # if no statement currently exists
        else:
            print("No statement found, prompting for user action")

            self.prompt.insert(INSERT,
                          "Statement for " + self.statement.name + " is not loaded yet! Would you like to load it in?\n")
            self.prompt.grid(row=3, column=0)

            self.load_yes = Button(self.frame, text="YES", command=lambda: self.statement.createStatementData())
            self.load_yes.grid(row=3, column=1)  # place button

            self.load_no = Button(self.frame, text="NO", command=lambda: self.declineAnalyzeStatement())
            self.load_no.grid(row=3, column=2)  # place button

        self.times_analyze_ran += 1

        return True


# declineAnalyzeStatement
    def declineAnalyzeStatement(self):
        pass


# generateYearDropDown: generate a year drop down menu
    def generateYearDropDown(self):
        years = [
            "2020",
            "2021",
        ]

        clickedYear = StringVar()  # datatype of menu text
        clickedYear.set("2021")  # initial menu text
        drop = OptionMenu(self.frame, clickedYear, *years)  # create drop down menu of years
        return drop, clickedYear


# generate a drop down menu with all 12 months
    def generateMonthDropDown(self):
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        clickedMonth = StringVar()  # datatype of menu text
        clickedMonth.set("January")  # initial menu text
        drop = OptionMenu(self.frame, clickedMonth, *months)  # create drop down menu of months
        return drop, clickedMonth

