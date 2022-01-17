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















