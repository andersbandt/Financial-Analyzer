"""
@file graphing_analyzer.py
@brief

"""

# import needed modules
import matplotlib.pyplot as plt
import os
import secrets

# import user created modules
import analysis.graphing_helper as grah

# import logger
from utils import logfn
from loguru import logger


def save_fig():
    # TODO: still figure out how to make order consistent (not random generation)
    # Increment the counter for each saved figure
    random_string = secrets.token_hex(2)
    file_name = f"{random_string}.png"
    save_path = os.path.join(os.getcwd(), "tmp", file_name)
    plt.savefig(save_path)
    print(f"Saved figure as: {save_path}")


def show_plots():
    plt.show(block=False)


##############################################################################
####      SPENDING PLOTTING FUNCTIONS    #####################################
##############################################################################

@logfn
def create_pie_chart(values, labels, explode=0.1, title="Pie Chart"):
    plt.rcdefaults() # sets rc defaults
    plt.clf() # clears the entire current figure with all its axes

    logger.debug("Running graphing_analyzer: create_pie_chart")
    fig = plt.figure(1)
    grah.get_pie_plot(values, labels, explode, title)
    return fig


# create_bar_chart:
@logfn
def create_bar_chart(labels, values, xlabel=None, title=None):
    plt.rcdefaults() # sets rc defaults
    plt.clf() # clears the entire current figure with all its axes

    logger.debug("Running graphing_analyzer: create_pie_chart")
    plt.rcdefaults()
    fig, ax = plt.subplots()
    grah.get_bar_chart([ax], 0, labels, values, title)

    if xlabel is not None:
        ax.set_xlabel(xlabel)

    save_fig()


# create_stacked_balances: creates a 'stacked' balances graph showing different asset types
#     https://stackoverflow.com/questions/21688402/stacked-bar-chart-space-between-y-axis-and-first-bar-matplotlib-pyplot
@logfn
def create_stackline_chart(x_axis, y_axis, title=None, label=None, y_format=None):
    plt.rcdefaults() # sets rc defaults
    plt.clf() # clears the entire current figure with all its axes


    plt.stackplot(x_axis, y_axis, labels=label)
    plt.title(title)
    plt.axis("tight")

    # format y-axis as currency
    if y_format == 'currency':
        plt.gca().yaxis.set_major_formatter('${x:,.0f}')

    plt.legend(loc="upper left")

    save_fig()


def create_line_chart(x_axis, y_axis, title=None, legend=False, y_format=None):
    plt.rcdefaults() # sets rc defaults
    plt.clf() # clears the entire current figure with all its axes

    grah.get_line_chart(x_axis,
                        y_axis,
                        color='purple')

    # format y-axis as currency
    if y_format == 'currency':
        plt.gca().yaxis.set_major_formatter('${x:,.0f}')

    # add grid lines
    plt.grid(True, linestyle='--', alpha=0.7)

    # add legend and title
    if legend:
        plt.legend(loc="best")
    plt.title(title)

    save_fig()


# create_mul_line_chart: creates multiple
def create_mul_line_chart(x_axis, y_axis_arr, title=None, labels=None, rotate_labels=False, legend=False, y_format=None):
    plt.rcdefaults() # sets rc defaults
    plt.clf() # clears the entire current figure with all its axes

    i = 0
    for y_axis in y_axis_arr:
        grah.get_line_chart(x_axis,
                            y_axis,
                            color='blue',
                            label=labels[i])
        i += 1

    # format y-axis as currency
    if y_format == 'currency':
        plt.gca().yaxis.set_major_formatter('${x:,.0f}')

    # rotate labels
    if rotate_labels:
        plt.xticks(rotation=90)

    # add legend and title
    if legend:
        plt.legend(loc="best")

    # add grid lines
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.title(title)
    save_fig()

