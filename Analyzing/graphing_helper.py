
# import needed modules
import matplotlib.pyplot as plt
from datetime import date
import datetime


# import user defined modules
from db import db_helper

# TODO: create spending over time graph. To gain insight into something like weekly, daily, monthly spending and how
#  it changes through the semester


##############################################################################
####      PLOTTING FUNCTIONS    ##############################################
##############################################################################

def get_pie_plot(amounts, categories, explode=.1, title="Transaction Data"):
    # generate labels
    labels = []
    for i in range(0, len(amounts)):
        labels.append(categories[i] + ": " + str(amounts[i]))

    myexplode = []
    for i in range(0, len(amounts)):
        myexplode.append(explode)

    patches, texts = plt.pie(amounts, labels=labels, explode=myexplode, shadow=False)

    plt.legend(patches, labels, loc="best")
    plt.title(title)

    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    plt.tight_layout()

    return patches, texts



##############################################################################
####      STRIPPING FUNCTIONS    #############################################
##############################################################################


# strip_non_graphical_transactions: strips certain transactions that are part of categories
#   that don't graph well
def strip_non_graphical_transactions(categories, amounts):
    non_graphical = ["BALANCE", "SHARES", "TRANSFER", "PAYMENT", "VALUE", "INTERNAL"]

    new_categories = []
    new_amounts = []

    length = len(categories)
    for j in range(0, length):
        if categories[j] not in non_graphical:
            new_categories.append(categories[j])
            new_amounts.append(amounts[j])

    return new_categories, new_amounts


# strip_non_graphical_transactions: strips certain transactions that are part of categories
#   that don't graph well
def strip_non_expense_categories(categories, amounts):
    non_expense = ["INCOME"]

    new_categories = []
    new_amounts = []

    i = 0
    for j in range(0, len(categories)):
        if categories[i] in non_expense:
            new_categories.append(categories[i])
            new_amounts.append(amounts[i])
            i -= 1
        i += 1

    return new_categories, new_amounts


# getSpaces: gets the number of spaces needed for pretty printing in straight columns
def get_spaces(length, trim):
    spaces = ""
    for i in range(trim - length):
        spaces += " "
    return spaces


# print_category_amount
def print_category_amount(category, amount):
    string_to_print = ("CATEGORY: " + category + get_spaces(len(category), 16) + " || AMOUNT: " + str(amount))
    print(string_to_print)




