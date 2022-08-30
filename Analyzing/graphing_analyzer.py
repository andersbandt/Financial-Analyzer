

from analyzing import analyzer_helper
from analyzing import graphing_helper

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.pyplot as pyplot

##############################################################################
####      PLOTTING FUNCTIONS    ##############################################
##############################################################################

# TODO: feature idea. Figure out how to create list of final items that you can click "on" or "off" to toggle visibility.
# piChartExpenseSummary: plots a pie chart of expenses
# input: statement
# output: none (plots pie chart)
def create_pie_chart(transactions, categories):
    print("Running graphing_analyzer: create_pie_chart")

    categories, amounts = analyzer_helper.create_category_amounts_array(transactions, categories)
    #for i in range(0, len(amounts)-1):
    #    graphing_helper.print_category_amount(categories[i], amounts[i])

    categories, amounts = graphing_helper.strip_non_graphical_transactions(categories, amounts)

    for i in range(0, len(amounts)-1):
        graphing_helper.print_category_amount(categories[i], amounts[i])

    j = 0
    length = len(amounts)
    for i in range(0, length):  # index through all elements
        # check if past current length of amounts array
        if j > len(amounts):
            print("Uh oh, index exceeded amount array length. Breaking.")
            break

        # remove net addition amounts, zero amounts, and turn expenses into positive values
        if amounts[j] == 0:  # if the element is greater than or equal to 0
            print("Removing equal to 0 element")
            categories.remove(categories[j])
            del amounts[j]
            j -= 1
        elif amounts[j] < 0:  # if the amount is less than 0
            amounts[j] = abs(amounts[j])  # absolute value the amount
            print("Converted to absolute value: " + str(amounts[j]) + " for category " + categories[j])

        j += 1

    #amounts = [abs(ele) for ele in amounts]  # for some reason some elements aren't getting absoluted
    myexplode = []
    for i in range(0, len(amounts)):
        myexplode.append(.2)

    pyplot.pie(amounts, labels=categories, explode=myexplode, shadow=True)
    #pyplot.legend(title="Spending Categories")
    pyplot.show()

    return True


def create_bar_chart(transactions, categories):
    print("Running graphing_analyzer: create_pie_chart")

    categories, amounts = analyzer_helper.create_category_amounts_array(transactions, categories)
    categories, amounts = graphing_helper.strip_non_graphical_transactions(categories, amounts)

    plt.rcdefaults()
    fig, ax = plt.subplots()

    y_pos = np.arange(len(categories))

    ax.barh(y_pos, amounts, align='center', color='green', ecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Amount ($)')
    ax.set_title('Financial Bar Chart')

    plt.show()


def create_summation_vs_time(transactions, categories):
    exec_summary = analyzer_helper.return_transaction_exec_summary(transactions)
    print("create_summation_vs_time got this for expenses", exec_summary["expenses"])
    print("create_summation_vs_time got this for incomes", exec_summary["incomes"])


# TODO: finish this graphical function
# https://stackoverflow.com/questions/21688402/stacked-bar-chart-space-between-y-axis-and-first-bar-matplotlib-pyplot
def create_stacked_balances():
    pass

