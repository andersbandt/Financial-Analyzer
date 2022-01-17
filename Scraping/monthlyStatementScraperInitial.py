import csv
import numpy as np
import matplotlib as plt
import matplotlib.pyplot as pyplot

##############################################################################
####      PRINTING FUNCTIONS           #######################################
##############################################################################

# getSpaces: gets the number of spaces needed for pretty printing in straight columns
def getSpaces(length, trim):
	spaces = ""
	for i in range(trim-length):
		spaces += " "
	return spaces


# printTransaction: pretty prints a single transaction
def printTransaction(transaction):
	print("DATE: " + ''.join(transaction[0]) + \
		" || AMOUNT: " + ''.join(transaction[1]) + getSpaces(len(transaction[1]), 8) + \
		" || DESC: " + ''.join(transaction[2]) + getSpaces(len(transaction[2]), 40) + \
		" || CATEGORY: "+ ''.join(transaction[3]) )
	return True


# printStatement: pretty prints an input statement
def printStatement(statement):
	for i in range(0, len(statement[0])):
		print("DATE:  " + statement[0][i] + " ||  AMOUNT:  " + statement[1][i] + " || DESCRIPTION:  " + statement[2][i])
	return True


# printStatementCategorized: pretty prints an input statement with categories attached (before saving to CSV)
def printStatementCategorized(statement):
	for i in range(0, len(statement[0])):
		print("DATE: " + statement[0][i] + \
		" || AMOUNT: " + statement[1][i] + getSpaces(len(statement[1][i]), 8) + \
		" || DESC: " + statement[2][i][0:40] + getSpaces(len(statement[2][i]), 40) + \
		" || CATEGORY: "+ statement[3][i])
	return True


# printSavedStatementCategorized: pretty prints an input statement with categories attached that has already been saved to CSV
def printSavedStatementCategorized(statement):
	for i in range(0, len(statement[0])):
		date = str(statement[0][i])
		amount = str(statement[1][i])
		description = str(statement[2][i][0:40])
		category = str(statement[3][i])
		print("DATE: " + ''.join(date) + \
		" || AMOUNT: " + ''.join(amount) + getSpaces(len(statement[1][i]), 8) + \
		" || DESC: " + ''.join(description) + getSpaces(len(statement[2][i]), 40) + \
		" || CATEGORY: "+ ''.join(category) )
	return True


# printStatementNA: pretty prints just the 'NA' entries in a categorized statement
def printStatementNA(statement):
	for i in range(0, len(statement[0])):
		category = str(statement[3][i])
		if category == "NA":
			date = str(statement[0][i])
			amount = str(statement[1][i])
			description = str(statement[2][i][0:40])
			print("DATE: " + ''.join(date) + \
			" || AMOUNT: " + ''.join(amount) + getSpaces(len(statement[1][i]), 8) + \
			" || DESC: " + ''.join(description) + getSpaces(len(statement[2][i]), 40) + \
			" || CATEGORY: "+ ''.join(category) )
	return True


# printCategories: pretty prints all the categories
def printCategories(categories):
	for i in range(0, len(categories)):
		print(str(i) + ": " + categories[i]['category'])

	return True


##############################################################################
####      EXTRACT FROM CSV FUNCTIONS           ###############################
##############################################################################

# getFilepath: gets filepath to parse based on input
def getFilepath(basefilepath, month, year):
	return True

# extractStatement: extracts date, amount, and description of a certain CSV file
		# input: file path to CSV - output: list object with data 
		# below are the indexes (column numbers) of the source data from the CSV file
		# 0: date
		# 1: amount
		# 4: description
def extractStatement(filePath):
	print("Extracting raw statement: " + filePath)
	#dataGather = np.empty(shape=(1, 3)) # 1 row to start, 3 columns representing all the data we want
	dates = []
	amounts = []
	descriptions = []
	with open(filePath) as f:
		csv_reader = csv.reader(f, delimiter=',')
		for line in csv_reader:
			dates.append(line[0]) # date
			amounts.append(line[1]) # amount
			descriptions.append(line[4]) # description
	return dates, amounts, descriptions


# extractCategorizedStatement: extracts date, amount, and description, and category of a certain CSV file
		# input: file path to CSV - output: list object with data 
		# below are the indexes (column #s) of the source data from the CSV file
		# 0: date
		# 1: amount
		# 2: description
		# 3: category
def extractCategorizedStatement(filePath):
	print("Extracting categorized Statement: " + filePath)
	#dataGather = np.empty(shape=(1, 3)) # 1 row to start, 3 columns representing all the data we want
	dates = []
	amounts = []
	descriptions = []
	categories = []
	with open(filePath) as f:
		csv_reader = csv.reader(f, delimiter=',')
		i = 0
		for line in csv_reader:
			if i % 2 == 0:
				#print(line[i])
				dates.append(line[0]) # date
				amounts.append(line[1]) # amount
				descriptions.append(line[2]) # description
				categories.append(line[3]) # categories
			i += 1
	return dates, amounts, descriptions, categories


##############################################################################
####      CATEGORIZATION FUNCTIONS    ########################################
##############################################################################


# categorizer: categorizes a single transaction based on the transactions description
def categorizer(categories, description):
	for i in range(0, len(categories)):
		if any(keyword in description for keyword in categories[i]['keywords']):
			return categories[i]['category']

	return "NA" # if no appropriate category was found


# categorizeStatementAutomatic: adds a category label to each statement array
	# based on predefined keywords in transaction description
	# input:N by 3 data array - output: 4 by N data array with category
def categorizeStatementAutomatic(statement):
	categories = formCategories() # initialize category array of dictionary entries
	statement = np.array(statement) # form a numpy array
	length = np.size(statement[1,:])
	statement = np.append(statement, np.empty((1, length)), axis=0)
	i = 0
	for description in statement[2,:]:
		category = categorizer(categories, description)
		statement[3,i] = category
		i += 1

	return statement


# promptUserCategorize: prompts a user to categorize a specific item
	# input: categories
	# input: transaction (transaction to be categorized)
	# output: new transaction category index, or -1 if user wants to quit categorization
def promptUserCategorize(categories, transaction):
	print("\r\nPLEASE CATEGORIZE THIS TRANSACTION")
	printCategories(categories)
	print("Q: Quit user categorization")
	print("S: Skip transaction")
	printTransaction(transaction)
	category_index = input("What is the category?: ") # takes category input as index of category to assign

	if category_index == "Q":
		return -1
	elif category_index == 'S':
		return -2
	else:
		return int(category_index)


# userCategorize: iterates through uncategorized transactions and prompts user to categorize them
def userCategorize(statement):
	categories = formCategories()
	for i in range(0, len(statement[0])):
		category = str(statement[3][i])
		if category == "NA":
			date = str(statement[0][i])
			amount = str(statement[1][i])
			description = str(statement[2][i])
			category = str(statement[3][i])
			new_category_index = promptUserCategorize(categories, [date, amount, description, category])
			if new_category_index == -1: # if user wants to quit categorization
				return statement
			elif new_category_index == -2: # if user wants to skip transaction
				print("Transaction skipped")
			else:
				statement[3][i] = categories[new_category_index]['category']

	return statement


##############################################################################
####      SAVING FUNCTIONs               #####################################
##############################################################################

# saveStatement: saves a categorized statement as a csv
def saveStatement(statement, save_filepath):
	print("Saving statement at: " + save_filepath)
	with open(save_filepath, 'w') as f:
		writer = csv.writer(f, delimiter=',')
		#writer.writerow(["DATE","AMOUNT", "DESCRIPTION", "CATEGORY")
		statement = zip(*statement)
		writer.writerows(statement)

	return True


# saveMultipleStatements: saves multiple categorized statements into one csv
def saveMultipleStatements(statements, save_filepath):
	print("Saving multiple statements at: " + save_filepath)
	with open(save_filepath, 'w') as f:
		writer = csv.writer(f, delimiter=',')
		#writer.writerow(["DATE","AMOUNT", "DESCRIPTION", "CATEGORY")
		for i in range(0, len(statements)):
			statement_to_write = zip(*statements[i])
			writer.writerows(statement_to_write)

	return True


##############################################################################
####      ANALYSIS FUNCTIONS    ##############################################
##############################################################################

# sumCategory: returns the dollar ($) total of a certain category in a statement
	# input: category (string representing category)
	# input: statement
	# output: float dollar total
def sumCategory(statement, category):
	total_amount = 0
	for i in range(0, len(statement[0])): # for every transaction in the statement
		transaction_category = str(statement[3][i])
		if transaction_category == category:
			total_amount += float(statement[1][i])
	return total_amount


# sumCategories: returns the dollar ($) total of all categories in a statement
	# input: statement
	# output: 1D array of category strings
	# output: 1D array of amounts
def sumCategories(statement):
	categories = formCategories() # form category dictionary
	amount = [] # form 1D array of amounts to return
	return_categories = [] # form 1D array of categories to populate and return
	for i in range(0, len(categories)):
		
		amount.append(sumCategory(statement, categories[i]['category']))
		return_categories.append(categories[i]['category'])
		print("Got this amount for category " + categories[i]['category'] + " " + str(amount[i]))

	return return_categories, amount



##############################################################################
####      PLOTTING FUNCTIONS    ##############################################
##############################################################################


def piChartCategories(categories, amounts):
	print("Creating a pi chart for categories with amounts")
	amounts_absoluted = [abs(ele) for ele in amounts]
	pyplot.pie(amounts_absoluted, labels=categories)
	pyplot.show()

	return True



##############################################################################
####      MAIN FUNCTION               ########################################
##############################################################################

def main():
	basefilepath = "C:/Users/ander/OneDrive/Documents/Financials/2021/Monthly Statements/"
	month = '06-June/'

	june_raw = [0, 0, 0] # initialize an array containing the statements
	june_categorized = [0, 0, 0]
	june = [0, 0, 0]
	file_names = ['Savings2.csv', 'Checking1.csv', 'CreditCard3.csv']
	save_names = ['Savings_Categorized.csv', 'Checking_Categorized.csv', 'CreditCard_Categorized.csv']

	# good for extracting and automatically categorizing statements
	#for i in range(0, 3):
		#june_raw[i] = extractStatement(basefilepath + month + file_names[i])
		#printStatement(june[i])
		#june_categorized[i] = categorizeStatementAutomatic(june_raw[i])
		#printStatementCategorized(june_categorized[i])
		#saveStatement(june_categorized[i], basefilepath + month + save_names[i])

	# good for user categorizing data
	#for i in range(0, 3):
		#june[i] = extractCategorizedStatement(basefilepath + month + save_names[i])
		#printSavedStatementCategorized(june[i])
		#printStatementNA(june[i])
		#june[i] = userCategorize(june[i])
		#printSavedStatementCategorized(june[i])
		#saveStatement(june[i], basefilepath + month + save_names[i])
		#sumCategories(june[i])

	#saveMultipleStatements(june, basefilepath + month + 'June_2021.csv')
	june = extractCategorizedStatement(basefilepath + month + 'June_2021.csv')
	categories, amounts = sumCategories(june)
	piChartCategories(categories, amounts)




if __name__ == "__main__":
	main()





