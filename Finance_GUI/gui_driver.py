# import needed packages
import tkinter as tk
from tkinter import *
from tkinter import ttk

import lambdas
import matplotlib.pyplot as plt

from Finance_GUI import gui_helper
from Finance_GUI import guiTab_mainDashboard
from Finance_GUI import guiTab_analyzeSpendingHistory

from Statement_Classes import Statement


class MainApplication(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent

		self.tab1 = 0
		self.tab2 = 0

		self.setTabs()

		self.basefilepath = "C:/Users/ander/OneDrive/Documents/Financials/2021/Monthly Statements/"


	# set up tab control
	def setTabs(self):
		print("Creating tab nav bar and initializing tab content")
		tab_control = ttk.Notebook(self)

		self.tab1 = guiTab_mainDashboard.tabMainDashboard(self.parent)
		self.tab2 = guiTab_analyzeSpendingHistory.tabSpendingHistory(self.parent)
		#self.tab3 = ttk.Frame(tab_control);
		#self.tab4 = ttk.Frame(tab_control);
		#self.tab5 = ttk.Frame(tab_control)
		tab_control.add(self.tab1.frame, text="Run Program")
		tab_control.add(self.tab2.frame, text="Review Spending History")
		#tab_control.add(self.tab3, text="Budget Analysis")
		#tab_control.add(self.tab4, text="Categorize Statements")
		#tab_control.add(self.tab5, text="Forecasts")
		tab_control.grid(column=0, row=0)

		return True
		

###########################################################
######################### MAIN ############################
###########################################################

# main function
def main():
	print("Executing main function of gui_driver.py")
	window = tk.Tk()
	window.title("FINANCE AND BUDGET ANALYZER")
	window.geometry('1300x1000')
	MainApplication(window).grid(row=0, column=0, padx=5, pady=5)
	window.mainloop()


#dir = filedialog.askdirectory()








