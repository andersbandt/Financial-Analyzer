# import needed packages
import tkinter as tk
from tkinter import *
from tkinter import ttk

import csv
#import lambdas
#import xml.sax

import matplotlib.pyplot as plt
import matplotlib.pyplot as pyplot

#from Scraping import monthlyStatementScraper
#from Finance_GUI import gui_driver
#from categories import load_categories
#from Statement_Classes import Statement


##############################################################################
####      ANALYTICAL FUNCTIONS    ############################################
##############################################################################





##############################################################################
####      PLOTTING FUNCTIONS    ##############################################
##############################################################################

# piChartExpenseSummary: plots a pie chart of expenses
	# input: statement
	# output: none (plots pie chart)
def piChartExpenseSummary(statement):
	print("Creating a pi chart for categories with amounts")
	categories, amounts = statement.sumCategories() # get array of Category objects and array of float amounts, in the same order
	print(categories)
	print(amounts)
	
	j = 0
	for i in range(0, len(amounts)-1): # index through all elements
	# check if past current length of amounts array
		if j > len(amounts):
			print("Uh oh, index exceeded amount array length. Breaking.")
			break
		print("START OF ELEMENT EXAMINATION")
		print("The length of amounts is: " + str(len(amounts)))
		print("The length of categories is: " + str(len(categories)))
		print("i: " + str(i))
		print("j: " + str(j))
		print(categories[j])
		print(categories)
		print(amounts)
		y = 0 # variable to track if element was removed or not
	# remove certain categories, regardless of value
		if categories[j] == 'CASH SAVING':
			print("Removing CASH SAVING from array")
			amounts.remove(amounts[j]) # remove the element
			categories.remove(categories[j])
			#j = max(j - 1,0)
			y = y + 1
		elif categories[j] == 'CRYPTO':
			print("Removing CRYPTO from array")
			amounts.remove(amounts[j]) # remove the element
			categories.remove(categories[j])
			#j = max(j - 1,0)
			y = y + 1
	# remove net additition amounts, zero amounts, and turn expenses into positive values
		if amounts[j] >= 0: # if the element is greater than or equal to 0
			print("Removing greater than or equal to 0 element")
			amounts.remove(amounts[j]) # remove the element
			categories.remove(categories[j])
			#j = max(j - 1,0)
			y = y + 1
		elif amounts[j] < 0: # if the amount is less than 0
			amounts[j] = abs(amounts[j]) # absolute value the amount
			print("Converted to absolute value: " + str(amounts[j]))

		
		j = j + 1 - y
		
		if j < 0:
			j = 0


	amounts = [abs(ele) for ele in amounts] # for some reason some elements aren't getting absoluted
	print(categories)
	print(amounts)
	pyplot.pie(amounts, labels=categories)
	pyplot.show()

	return True





