

# import needed modules
import matplotlib.pyplot as plt
import numpy as np

# import logger
from utils import logfn

##############################################################################
####      PLOTTING FUNCTIONS    ##############################################
##############################################################################

def get_pie_plot(amounts, labels, explode=0.1, title=None, legend=False):
    # Clear the current figure
    plt.clf()

    # Automatically create explode array based on the length of `amounts`
    explode_values = [explode] * len(amounts) if explode else [0] * len(amounts)

    # Add plot with additional options for better appearance
    wedges, texts, autotexts = plt.pie(
        amounts,
        labels=labels,
        explode=explode_values,
        autopct='%1.1f%%',  # Display percentages
        shadow=True,
        startangle=140,
        normalize=True
    )

    # Optionally add a legend and title
    if legend:
        plt.legend(wedges, labels, loc="best")
    if title:
        plt.title(title)

    # Set aspect ratio to ensure the pie is drawn as a circle
    plt.axis("equal")
    plt.tight_layout()

    # Show plot
    plt.show()


def get_line_chart(x_axis, y_axis, label=None, color=None):
    # make plot
    # plt.plot(x_axis, y_axis)
    plt.plot(x_axis, y_axis, marker='o', linestyle='-', color=None, label=label)


# @usage  fig, ax = plt.subplots(num_slices, 1, figsize=(15, 3), sharex=True)
#           pass in 'ax' as variable, then use plt.show() as normal
def get_bar_chart(ax, i, labels, amounts, title=None):
    y_pos = np.arange(len(labels))
    ax[i].barh(y_pos, amounts, align="center", color="green", ecolor="black")
    ax[i].set_yticks(y_pos)
    ax[i].set_yticklabels(labels)
    ax[i].invert_yaxis()  # labels read top-to-bottom

    if title is not None:
        ax[i].set_title(title)


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
def strip_non_graphical_transactions(categories, amounts):
    non_graphical = ["BALANCE", "SHARES", "TRANSFER", "PAYMENT", "VALUE", "INTERNAL"] # tag:HARDCODE

    new_categories = []
    new_amounts = []

    for j in range(0, len(categories)):
        if categories[j].name not in non_graphical:
            new_categories.append(categories[j])
            new_amounts.append(amounts[j])

    return new_categories, new_amounts


def strip_non_expense_categories(cat_str_arr, amounts):
    to_remove = ["INCOME", "INTERNAL", "INVESTMENT", "MISC FINANCE"] # tag:HARDCODE

    new_categories = []
    new_amounts = []

    for j in range(0, len(cat_str_arr)):
        if cat_str_arr[j] not in to_remove:
            new_categories.append(cat_str_arr[j])
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



