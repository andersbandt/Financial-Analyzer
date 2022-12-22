
# import needed modules
import matplotlib.pyplot as plt
import numpy as np


##############################################################################
####      PLOTTING FUNCTIONS    ##############################################
##############################################################################

def get_cat_pie_plot(amounts, categories, explode=.1, title=None):
    # generate labels
    labels = []
    for i in range(0, len(amounts)):
        labels.append(categories[i].name + ": " + str(amounts[i]))

    myexplode = []
    for i in range(0, len(amounts)):
        myexplode.append(explode)

    plt.pie(amounts, labels=labels, explode=myexplode, shadow=False, normalize=True)

    # add legend and title
    #plt.legend(patches, labels, loc="best")
    plt.title(title)

    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    plt.tight_layout()


def get_pie_plot(amounts, labels, explode=.1, title=None, legend=False):
    # clear current plot
    plt.clf()

    # set explore
    myexplode = []
    for i in range(0, len(amounts)):
        myexplode.append(explode)

    # add plot
    plt.pie(amounts, labels=labels, explode=myexplode, shadow=False, normalize=True)

    # add legend and title
    patches = labels
    if legend:
        plt.legend(patches, labels, loc="best")
    plt.title(title)

    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    plt.tight_layout()


def get_line_chart(x_axis, y_axis, title=None, legend=False):
    # clear current plot
    plt.clf()

    # make plot
    plt.plot(x_axis, y_axis)

    # add legend and title
    if legend:
        pass
        #plt.legend(patches, labels, loc="best")
    plt.title(title)


# get_stacked_bar_chart: creates a bar chart with multiple 'stacked' values on the y axis
def get_stacked_bar_chart(x_ind, y_1, y_2, title, width, scale_factor, x_ticks=None, y_3=None, y_4=None):
    # clear current plot
    plt.clf()

    inv_color = "#20774c"  # dark green
    liq_color = "#202377"  # dark blue

    p1 = plt.bar(x_ind, y_1, width, color=inv_color)
    p2 = plt.bar(x_ind, y_2, width, color=liq_color, bottom=y_1)

    # set general plot info
    plt.title(title)
    plt.legend((p1[0], p2[0]), ('Investment', 'Liquid'), loc=2, frameon='false')

    # set X axis (date) info
    if x_ticks is not None:
        plt.xticks(x_ind + width / 2, x_ticks)

    # set Y axis (balance $) info
    max_val = max(y_1 + y_2)
    ticks = 10

    plt.ylabel('Amount (k dollaz $)')
    plt.yticks(np.arange(0, max_val, max_val/ticks))  # sets the y axis scaling and step size
    plt.tick_params(top='off', bottom='off', right='off')

    plt.grid(axis='y', linestyle='-')


##############################################################################
####      STRIPPING + DATA FORMATTING FUNCTIONS    ###########################
##############################################################################

# strip_non_graphical_transactions: strips certain transactions that are part of categories
#   that don't graph well
def strip_non_graphical_transactions(categories, amounts):
    non_graphical = ["BALANCE", "SHARES", "TRANSFER", "PAYMENT", "VALUE", "INTERNAL"]

    new_categories = []
    new_amounts = []

    for j in range(0, len(categories)):
        if categories[j].name not in non_graphical:
            new_categories.append(categories[j])
            new_amounts.append(amounts[j])

    return new_categories, new_amounts


# strip_non_graphical_transactions: strips certain transactions that are part of categories
#   that don't graph well
def strip_non_expense_categories(categories, amounts):
    non_expense = ["INCOME"]

    new_categories = []
    new_amounts = []

    for j in range(0, len(categories)):
        if categories[j].name not in non_expense:
            new_categories.append(categories[j])
            new_amounts.append(amounts[j])

    return new_categories, new_amounts


# strip_zero_categories: strips any Category with 0$ of transaction data loaded
def strip_zero_categories(categories, amounts):
    new_categories = []
    new_amounts = []

    for j in range(0, len(categories)):
        if amounts[j] != 0:
            new_categories.append(categories[j])
            new_amounts.append(amounts[j])

    return new_categories, new_amounts


# graph_format_expenses: absolutes all expenses and rounds to 2 decimal points
def format_expenses(amounts):
    # iterate through expense amounts
    for i in range(0, len(amounts)):
        amounts[i] = round(abs(amounts[i]), 2)

    return amounts


##############################################################################
####      CONSOLE PRINTING FUNCTIONS     #####################################
##############################################################################

# getSpaces: gets the number of spaces needed for pretty printing in straight columns
def get_spaces(length, trim):
    spaces = ""
    for i in range(trim - length):
        spaces += " "
    return spaces


# print_category_amount
def print_category_amount(category, amount):
    string_to_print = ("CATEGORY: " + category.name + get_spaces(len(category.name), 16) + " || AMOUNT: " + str(amount))
    print(string_to_print)




