# import needed modules
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from functools import partial
import csv
import os.path

# import user defined modules
from categories import load_categories
from Statement_Classes import Transaction


class Statement:
	def __init__(self, year, month, master, row_num, column_num, *args, **kwargs):
		# initialize identifying statement info
		self.year = year
		self.month = month
		self.name = str(self.month) + "/" + str(self.year)

		# initialize categories
		self.categories = load_categories.load_categories("C:/Users/ander/OneDrive - UW-Madison/Code/Python/Spending and Budgeting Analyzer/categories/categories.xml")
		load_categories.check_categories(self.categories)

		# load in statement filepath info
		self.basefilepath = "C:/Users/ander/OneDrive/Documents/Financials/"
		self.statementFolder, self.statementFilepath = self.getFilepaths(year, month)  # generate filepath of .csv file to download
		self.transactions = []

		# initialize gui content
		self.master = master
		self.frame = tk.Frame(self.master)
		self.frame.grid(row=row_num, column=column_num)
		self.prompt = Text(self.frame, padx=5, pady=5, height=10)
		self.prompt.grid(row=4, column=0)

		self.clicked_category = []  # holds all the user set categories


##############################################################################
####      DATA LOADING FUNCTIONS    ##########################################
##############################################################################

	# loadStatement: loads statement based on filepath
	def loadStatement(self):
		status = self.checkStatementStatus()
		if status:
			self.guiPrint("Found a pre-existing statement for " + self.name)
			self.extractStatementContent()

			if (self.checkContent() == False):
				if self.promptYesNo("There seems to be an error in loading the transaction data. Overwrite and load in new data from source?"):
					self.createStatementData()
				else:
					self.guiPrint("Ok! Not loading in statement data.")

			self.printStatement()
			self.createStatementTable(6, 0)
			return
		else:
			self.guiPrint("Uh oh, statement for " + self.name + " is not loaded yet! Would you like to load it in? Y or N: ")
			if self.promptYesNo("Would you like to load in and create new statement data?"):
				self.createStatementData()
			else:
				self.guiPrint("Ok! Not loading in statement data.")
				return

		return


	# extractStatementContents: populates the statement's transactions with pre-existing statement data
	def extractStatementContent(self):
		with open(self.statementFilepath) as f:
			csv_reader = csv.reader(f, delimiter=',')
			for line in csv_reader:
				try:
					self.transactions.append(Transaction.Transaction(line[0], float(line[1]), line[2], line[3], None)) # order: date, amount, description, category, source

				except IndexError:
					print("Whoops, transaction line from .csv file might be missing some data")
				except ValueError:
					print("Error converting: " + line[1] + " to a float")
			
		print("Extracted statement from pre-existing statement data. Statement: " + self.name + " now contains " + str(len(self.transactions)) + " transactions")


	# createStatement: combines and automatically categorizes transactions across all raw account statement data
	def createStatementData(self):
		self.transactions = []
		self.transactions.extend(self.loadWellsFargoChecking())
		self.transactions.extend(self.loadWellsFargoSaving())
		self.transactions.extend(self.loadWellsFargoCredit())

		self.guiPrint("Loaded in raw transaction data, running categorizeStatementAutomatic() now!")
		self.categorizeStatementAutomatic()  # run categorizeStatementAutomatic on the transactions

		self.createStatementTable(6, 0)  # creates a statement table at position (6, 0) *(row, column)

		if self.checkNA():
			if self.promptYesNo("NA (category-less) entries detected in statement. Would you like to start user categorization?"):
				self.userCategorize()
			else:
				self.guiPrint("Ok, not manually categorizing statement")


	# checkStatementStatus: checks the status of a specific month's statement
	def checkStatementStatus(self):
		return os.path.exists(self.statementFilepath)


	# loadWellsFargoChecking: loads data from file 'Checking1.csv' from Wells Fargo account
	# below are the indexes (column numbers) of the source data from the CSV file
		# 0: date
		# 1: amount
		# 4: description
	def loadWellsFargoChecking(self):
		transactions = []
		filepath = self.statementFolder + 'Checking1.csv'
		self.guiPrint("Extracting raw statement at: " + filepath)
		try:
			with open(filepath) as f:
				csv_reader = csv.reader(f, delimiter=',')
				for line in csv_reader:
					transactions.append(Transaction.Transaction(line[0], float(line[1]), line[4], None, 'Checking'))  # order: date, amount, description, category, source
		except FileNotFoundError:
			self.alert_user("Missing data!", "You might be missing your Wells Fargo Checking .csv file")

		return transactions


	# loadWellsFargoSaving: loads data from file 'Saving2.csv' from Wells Fargo account
	# below are the indexes (column numbers) of the source data from the CSV file
		# 0: date
		# 1: amount
		# 4: description
	def loadWellsFargoSaving(self):
		transactions = []
		filepath = self.statementFolder + 'Savings2.csv'
		self.guiPrint("Extracting raw statement at: " + filepath)
		try:
			with open(filepath) as f:
				csv_reader = csv.reader(f, delimiter=',')
				for line in csv_reader:
					transactions.append(Transaction.Transaction(line[0], float(line[1]), line[4], None, 'Saving'))  # order: date, amount, description, category, source
		except FileNotFoundError:
			self.alert_user("Missing data!", "You might be missing your Wells Fargo Saving .csv file")
		return transactions


	# loadWellsFargoCredit: loads data from file 'Checking1.csv' from Wells Fargo account
	# below are the indexes (column numbers) of the source data from the CSV file
		# 0: date
		# 1: amount
		# 4: description
	def loadWellsFargoCredit(self):
		transactions = []
		filepath = self.statementFolder + 'CreditCard3.csv'
		self.guiPrint("Extracting raw statement at: " + filepath)
		try:
			with open(filepath) as f:
				csv_reader = csv.reader(f, delimiter=',')
				for line in csv_reader:
					transactions.append(Transaction.Transaction(line[0], float(line[1]), line[4], None, 'Credit')) # order: date, amount, description, category, source
		except FileNotFoundError:
			self.alert_user("Missing data!", "You might be missing your Wells Fargo Credit .csv file")
		return transactions


##############################################################################
####      CATEGORIZATION FUNCTIONS    ########################################
##############################################################################

	#categorizeStatementAutomatic: adds a category label to each statement array based predefined
	def categorizeStatementAutomatic(self):
		for transaction in self.transactions:
			transaction.categorizeTransactionAutomatic(self.categories)


	# promptUserCategorize: prompts a user to categorize a specific item
		# input: categories
		# input: transaction (transaction to be categorized)
		# output: new transaction category index, or -1 if user wants to quit categorization
	def promptUserCategorize(self, transaction):
		self.guiPrint("PLEASE CATEGORIZE THIS TRANSACTION")
		for i in range(0, len(self.categories)):
			self.guiPrint(str(i) + " " + self.categories[i].printCategory())
		self.guiPrint("Q: Quit user categorization")
		self.guiPrint("S: Skip transaction")
		self.guiPrint(transaction.printTransaction())
		#category_index = input("What is the category?: ") # takes category input as index of category to assign
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
				if userCategorizeResponse == -1: # if user wants to quit categorization
					print("Quitting user categorization")
					return
				elif userCategorizeResponse == -2: # if user wants to skip transaction
					print("Transaction skipped")
				else:
					transaction.category = self.categories[userCategorizeResponse].name


##############################################################################
####      ANALYSIS FUNCTIONS    ##############################################
##############################################################################

	# sumIndividualCategory: returns the dollar ($) total of a certain category in a statement
		# output: dollar total
	def sumIndividualCategory(self, category):
		total_amount = 0
		for transaction in self.transactions: # for every transaction in the statement
			if transaction.category == category:
				total_amount += transaction.amount
		return total_amount


	# sumCategories: returns the dollar ($) total of all categories in a statement
		# output: 1D array of category strings
		# output: 1D array of amounts
	def sumCategories(self):
		category_amounts = [] # form 1D array of amounts to return
		return_categories = [] # form 1D array of categories to populate and return
		for category in self.categories:
			category_amounts.append(self.sumIndividualCategory(category.name))
			return_categories.append(category.name)
			print("Got this amount for category " + category.name + " " + str(category_amounts[-1]) )

		return return_categories, category_amounts


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
		if self.checkStatementStatus():
			response = self.promptYesNo("It looks like a saved statement for " + self.name + " already exists, are you sure you want to overwrite by saving this one?")
			if response == "no":
				self.guiPrint("Ok, not saving statement")
				return False

		self.guiPrint("Saving statement at: " + self.statementFilepath)
		self.guiPrint("Saving " + str(len(self.transactions)) + " transactions")
		try:
			with open(self.statementFilepath, 'w') as f:
				writer = csv.writer(f, delimiter=',', lineterminator='\n')
				for transaction in self.transactions:
					writer.writerow(transaction.getSaveStringArray())
		except TypeError:
			self.guiPrint("Uh oh, something went wrong with saving!")
			self.alert_user("Uh, oh.", "Something went wrong with saving the statement")

##############################################################################
####      PRINTING FUNCTIONS    ##############################################
##############################################################################

	# printStatement: pretty prints a statement
	def printStatement(self):
		for i in range(0, len(self.transactions)):
			self.transactions[i].printTransaction()


	#guiPrint: prints a message both on the Python terminal and a Tkinter frame
	def guiPrint(self, message):
		message = ">>>" + message + "\n"
		print(message)
		if self.frame != 0:
			self.prompt.insert(INSERT, message)

		self.prompt.see("end")
		return True


##############################################################################
####      INTERACTIVE GUI FUNCTIONS    #######################################
##############################################################################

	#change_transaction_category
	def change_transaction_category(self, index, *args):
		self.guiPrint("Changing transaction number " + str(index) + " to category: " + self.clicked_category[index].get())
		self.transactions[index].setCategory(self.clicked_category[index].get())
		pass


	# createStatementTable
	def createStatementTable(self, row_num, column_num):
		# Create a frame for the canvas with non-zero row&column weights
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

		# Populate statement data
		rows = len(self.transactions)
		columns = 5
		labels = [[tk.Label() for j in range(columns)] for i in range(rows)]

		self.clicked_category = [StringVar(frame_data) for i in range(rows)]  # initialize StringVar entries for OptionMenus

		# place data for each transaction in a separate row
		for i in range(0, rows):
			string_dict = self.transactions[i].getStringDict()
			labels[i][0] = tk.Label(frame_data, text=string_dict["date"])
			labels[i][1] = tk.Label(frame_data, text=string_dict["description"])
			labels[i][2] = tk.Label(frame_data, text=string_dict["amount"])

			# if the transaction does not yet have a category
			if string_dict["category"] == "NA":
				self.clicked_category[i] = StringVar(frame_data)  # datatype of menu text
				self.clicked_category[i].set("Please select a category")  # initial menu text

				self.clicked_category[i].trace("w", partial(self.change_transaction_category, i))

				labels[i][3] = tk.OptionMenu(frame_data, self.clicked_category[i], *(load_categories.get_category_strings(self.categories)))

			# if the transaction already has a category assigned
			else:
				labels[i][3] = tk.Label(frame_data, text=string_dict["category"])

			labels[i][4] = tk.Label(frame_data, text=string_dict["source"])

			# place all the components
			for j in range(0, columns):
				labels[i][j].grid(row=i, column=j, sticky='news')

		# Update buttons frames idle tasks to let tkinter calculate sizes
		frame_data.update_idletasks()

		# Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
		first_columns_width = sum([labels[0][j].winfo_width() for j in range(0, columns)])
		first_rows_height = sum([labels[i][0].winfo_height() for i in range(0, 20)])
		frame_canvas.config(width=first_columns_width + vsb.winfo_width(), height=first_rows_height)

		# Set the canvas scrolling region
		canvas.config(scrollregion=canvas.bbox("all"))

		# Place buttons for saving
		# set up button to start the categorization process
		save_statement = Button(self.frame, text="Save Statement", command=self.saveStatement)
		save_statement.grid(row=row_num, column=column_num + 1)


	# alert_user:
	def alert_user(self, title, message, kind='info', hidemain=True):
		if kind not in ('error', 'warning', 'info'):
			raise ValueError('Unsupported alert kind.')

		show_method = getattr(messagebox, 'show{}'.format(kind))
		show_method(title, message)

	# hide_statement_gui
	# TODO: get statements to properly hide
	def hide_statement_gui(self):
		print("Hiding statement" + self.name)
		self.frame.grid_forget()
		self.frame.destroy()

##############################################################################
####      GENERAL HELPER FUNCTIONS    ########################################
##############################################################################

	# promptYesNo: prompts the user for a yes or no response with a certain 'message' prompt
	def promptYesNo(self, message):
		response = messagebox.askquestion('ALERT', message)

		if response == "yes":
			return True
		else:
			return False

	# checkContent: checks for if any data is actually in the statement
	def checkContent(self):
		if (len(self.transactions) == 0):
			return False
		else:
			return True

	''' getFilepath: gets filepath to parse based on input
	inputs:
		basefilepath: base file path of directory where monthly statements are stored
		year: desired year to get statement data from
		month: month taken in as an int (01, 02, .. 11, 12, etc.)
	outputs:
		filepath of statement '''
	def getFilepaths(self, year, month):
		if month == 1:
			month_string = "01-January/"
			filename = "January"
			file_ext = ".csv"
		elif month == 2:
			month_string = "02-February/"
			filename = "February"
			file_ext = ".csv"
		elif month == 3:
			month_string = "03-March/"
			filename = "March"
			file_ext = ".csv"
		elif month == 4:
			month_string = "04-April/"
			filename = "April"
			file_ext = ".csv"
		elif month == 5:
			month_string = "05-May/"
			filename = "May"
			file_ext = ".csv"
		elif month == 6:
			month_string = "06-June/"
			filename = "June"
			file_ext = ".csv"
		elif month == 7:
			month_string = "07-July/"
			filename = "July"
			file_ext = ".csv"
		elif month == 8:
			month_string = "08-August/"
			filename = "August"
			file_ext = ".csv"
		elif month == 9:
			month_string = "09-September/"
			filename = "September"
			file_ext = ".csv"
		elif month == 10:
			month_string = "10-October/"
			filename = "October"
			file_ext = ".csv"
		elif month == 11:
			month_string = "11-November/"
			filename = "November"
			file_ext = ".csv"
		elif month == 12:
			month_string = "12-December/"
			filename = "December"
			file_ext = ".csv"
		else:
			print("Bad month int stored in statement: " + str(month))
			return

		statementFolder = self.basefilepath + "/" + str(year) + "/Monthly Statements/" + month_string
		statementFilepath = statementFolder + filename + file_ext
		return statementFolder, statementFilepath


	# checkNA: checks if a statement contains any transactions with 'NA' as a category
	def checkNA(self):
		amountNA = 0
		for transaction in self.transactions:
			if transaction.category == "NA":
				amountNA += 1

		if amountNA > 0:
			print("Analyzed statement, contains " + str(amountNA) + " NA entries")
			return True
		else:
			return False


