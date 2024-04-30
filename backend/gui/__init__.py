
# import needed packages
import tkinter as tk
from tkinter import ttk

import sv_ttk

# import tab classes
from gui.tabs import dashboard 
from gui.tabs import analyze_history 
from gui.tabs import edit_category
from gui.tabs import load_data 
from gui.tabs import review_investments
from gui.tabs import review_balances
from gui.tabs import categorize_transactions
from gui.tabs import budgeting

class MainApplication:
	def __init__(self, window, *args, **kwargs):
		self.nb = ttk.Notebook(window)

		self.tab1 = None
		self.tab2 = None
		self.tab3 = None
		self.tab4 = None
		self.tab5 = None
		self.tab6 = None
		self.tab7 = None

		self.basefilepath = "C:/Users/ander/OneDrive/Documents/Financials/2021/Monthly Statements/"

		self.setTabs()


	# set up tab control
	def setTabs(self):
		print("Creating tab nav bar and initializing tab content")
		self.tab1 = dashboard.tabMainDashboard(self.nb)
		self.tab2 = analyze_history.tabSpendingHistory(self.nb)
		self.tab3 = edit_category.tabEditCategory(self.nb)
		self.tab4 = load_data.tabFinanceData(self.nb)
		self.tab5 = review_investments.tabInvestments(self.nb)
		self.tab6 = review_balances.tabBalances(self.nb)
		self.tab7 = categorize_transactions.tabCategorizeTransactions(self.nb)
		self.tab8 = budgeting.tabBudgeting(self.nb)

		self.nb.add(self.tab1.frame, text="Run Program")
		self.nb.add(self.tab2.frameX, text="Review Spending History")
		self.nb.add(self.tab3.frame, text="Edit Categories")
		self.nb.add(self.tab4.frame, text="Load Data")
		self.nb.add(self.tab5.frame, text="Review Investments")
		self.nb.add(self.tab6.frame, text="Review Balances")
		self.nb.add(self.tab7.frame, text="Categorize Transactions")
		self.nb.add(self.tab8.frame, text="Budgeting")

		self.nb.grid(column=0, row=0)

		return True
		

###########################################################
######################### MAIN ############################
###########################################################

# main function
def main():
	print("Executing main function of gui_driver.py")

	# setup window
	window = tk.Tk()

	window.title("FINANCE AND BUDGET ANALYZER")
	window.geometry('1250x900')

	# set the theme
	# window.tk.call("source", 'Finance_GUI/themes/azure.tcl')
	# window.tk.call("set_theme", "dark")

	sv_ttk.set_theme("dark")

	### add window Style
	# 	theme options are
	# 	"default", "alt", "classic", "clam"
	# style = ttk.Style(window)
	# style.theme_use("")

	# style.configure('TNotebook.Tab', background="green3")
	# style.map("TNotebook", background=[("selected", "green3")])

	#style.configure('TNotebook.Tab', background="Red")
	#style.map("TNotebook", background=[("selected", "red")])

	# place main app
	MainApplication(window)

	# run application
	window.mainloop()


#dir = filedialog.askdirectory()








