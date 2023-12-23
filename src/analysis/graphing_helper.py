# import needed modules
import matplotlib.pyplot as plt
import numpy as np

from utils import logfn

##############################################################################
####      PLOTTING FUNCTIONS    ##############################################
##############################################################################


@logfn
def get_cat_pie_plot(amounts, categories, explode=0.1, title=None):
    # generate labels
    labels = []
    for i in range(0, len(amounts)):
        labels.append(categories[i].name + ": " + str(amounts[i]))

    myexplode = []
    for i in range(0, len(amounts)):
        myexplode.append(explode)

    plt.pie(amounts, labels=labels, explode=myexplode, shadow=False, normalize=True)

    # add legend and title
    # plt.legend(patches, labels, loc="best")
    plt.title(title)

    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis("equal")
    plt.tight_layout()


@logfn
def get_pie_plot(amounts, labels, explode=0.1, title=None, legend=False):
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
    plt.axis("equal")
    plt.tight_layout()


@logfn
def get_line_chart(x_axis, y_axis, label=None, color=None):
    # make plot
    # plt.plot(x_axis, y_axis)
    plt.plot(x_axis, y_axis, marker='o', linestyle='-', color=None, label=label)





# @usage  fig, ax = plt.subplots(num_slices, 1, figsize=(15, 3), sharex=True)
#           pass in 'ax' as variable, then use plt.show() as normal
# @logfn
def get_bar_chart(ax, i, labels, amounts, title=None):
    y_pos = np.arange(len(labels))
    ax[i].barh(y_pos, amounts, align="center", color="green", ecolor="black")
    ax[i].set_yticks(y_pos)
    ax[i].set_yticklabels(labels)
    ax[i].invert_yaxis()  # labels read top-to-bottom

    if title is not None:
        ax[i].set_title(title)



# get_stacked_bar_chart: creates a bar chart with multiple 'stacked' values on the y axis
@logfn
def get_stacked_bar_chart(
    x_ind, y_1, y_2, title, width, scale_factor, x_ticks=None, y_3=None, y_4=None
):
    # clear current plot
    plt.clf()

    inv_color = "#20774c"  # dark green
    liq_color = "#202377"  # dark blue

    p1 = plt.bar(x_ind, y_1, width, color=inv_color)
    p2 = plt.bar(x_ind, y_2, width, color=liq_color, bottom=y_1)

    # set general plot info
    plt.title(title)
    plt.legend((p1[0], p2[0]), ("Investment", "Liquid"), loc=2, frameon="false")

    # set X axis (date) info
    if x_ticks is not None:
        plt.xticks(x_ind + width / 2, x_ticks)

    # set Y axis (balance $) info
    max_val = max(y_1 + y_2)
    ticks = 10

    plt.ylabel("Amount (k dollaz $)")
    plt.yticks(
        np.arange(0, max_val, max_val / ticks)
    )  # sets the y axis scaling and step size
    plt.tick_params(top="off", bottom="off", right="off")

    plt.grid(axis="y", linestyle="-")


##############################################################################
####      STRIPPING + DATA FORMATTING FUNCTIONS    ###########################
##############################################################################

# strip_non_graphical_transactions: strips certain transactions that are part of categories
#   that don't graph well
@logfn
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
@logfn
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
@logfn
def strip_zero_categories(categories, amounts):
    new_categories = []
    new_amounts = []

    for j in range(0, len(categories)):
        if amounts[j] != 0:
            new_categories.append(categories[j])
            new_amounts.append(amounts[j])

    return new_categories, new_amounts


# graph_format_expenses: absolutes all expenses and rounds to 2 decimal points
@logfn
def format_expenses(amounts):
    # iterate through expense amounts
    for i in range(0, len(amounts)):
        amounts[i] = round(abs(amounts[i]), 2)

    return amounts



