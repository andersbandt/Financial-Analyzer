# import needed packages
import tkinter as tk
from tkinter import *
from tkinter import ttk

import csv
import lambdas
import xml.sax

import matplotlib.pyplot as plt

from Finance_GUI import gui_driver
from Analyzing import spending_analyzer
from Statement_Classes import Statement


def main():
	#categories = load_categories.load_categories("C:/Users/ander/OneDrive - UW-Madison/Code/Python/Spending and Budgeting Analyzer/categories/categories.xml")
	
	#june = Statement.Statement(2021, 6)
	#june.printStatement()
	#spending_analyzer.piChartExpenseSummary(june)

	#july = Statement.Statement(2021, 7)
	#july.printStatement()
	#spending_analyzer.piChartExpenseSummary(july)

	gui_driver.main()


	return None



# thing that's gotta be here
if __name__ == "__main__":
	main()





