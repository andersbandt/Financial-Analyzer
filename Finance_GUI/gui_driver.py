# import needed packages
import tkinter as tk
from tkinter import ttk
import sqlite3

# import tab classes
from Finance_GUI import guiTab_mainDashboard
from Finance_GUI import guiTab_analyzeSpendingHistory
from Finance_GUI import guiTab_3_editCategory
from Finance_GUI import guiTab_4_loadSpendingData
from Finance_GUI import guiTab_5_reviewInvestments
from Finance_GUI import guiTab_6_reviewBalances


class MainApplication(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent

		self.tab1 = 0
		self.tab2 = 0
		self.tab3 = 0
		self.tab4 = 0
		self.tab5 = 0
		self.tab6 = 0

		self.basefilepath = "C:/Users/ander/OneDrive/Documents/Financials/2021/Monthly Statements/"

		try:
			self.conn = sqlite3.connect('databases/financials.db')
		except sqlite3.Error as er:
			print("Uh oh, something went wrong with connecting to sqlite database: financials.db")

		self.setTabs()


	# set up tab control
	def setTabs(self):
		print("Creating tab nav bar and initializing tab content")
		tab_control = ttk.Notebook(self)

		self.tab1 = guiTab_mainDashboard.tabMainDashboard(self.parent, self.conn)
		self.tab2 = guiTab_analyzeSpendingHistory.tabSpendingHistory(self.parent, self.conn)
		self.tab3 = guiTab_3_editCategory.tabEditCategory(self.parent, self.conn)
		self.tab4 = guiTab_4_loadSpendingData.tabFinanceData(self.parent, self.conn)
		self.tab5 = guiTab_5_reviewInvestments.tabInvestments(self.parent, self.conn)
		self.tab6 = guiTab_6_reviewBalances.tabBalances(self.parent)

		tab_control.add(self.tab1.frame, text="Run Program")
		tab_control.add(self.tab2.frame, text="Review Spending History")
		tab_control.add(self.tab3.frame, text="Edit Categories")
		tab_control.add(self.tab4.frame, text="Load Data")
		tab_control.add(self.tab5.frame, text="Review Investments")

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








