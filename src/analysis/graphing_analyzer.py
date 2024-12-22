"""
@file graphing_analyzer.py
@brief

"""

# import needed modules
import matplotlib.pyplot as plt
import os
import secrets
import numpy as np

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


def create_stack_bar_chart(x_axis, y_axis_arr, title=None, labels=None, y_label=None, y_format=None, colors=None):
    """
    Create a stacked bar chart.

    Parameters:
        x_axis (list): Labels for the x-axis.
        y_axis_arr (list of lists): Data for each stack.
        title (str): Title of the chart.
        labels (list): Labels for each stack (used for legend).
        y_label (str): Label for the y-axis.
        y_format (func): Format function for y-axis tick labels.
        colors (list): Colors for each stack.
    """
    ind = np.arange(len(x_axis))  # x positions
    width = 0.5

    # # Default colors if not provided
    # if colors is None:
    #     colors = plt.cm.tab10.colors  # Default to matplotlib's tab10 colormap

    # Plot each stack
    cumulative = np.zeros(len(x_axis))
    for i, y_ax in enumerate(y_axis_arr):
        label = labels[i] if labels else None
        plt.bar(ind, y_ax, width, bottom=cumulative, label=label)
        cumulative += y_ax  # Update cumulative height for stacking

    # Customize chart
    plt.ylabel(y_label if y_label else 'Value')
    plt.title(title if title else 'Stacked Bar Chart')
    plt.xticks(ind, x_axis)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tick_params(top=False, bottom=True, left=True, right=False)

    # Add legend
    if labels:
        plt.legend()

    # Apply y-axis format if specified
    if y_format:
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(y_format))

    plt.tight_layout()
    plt.show()


# create_stacked_balances: creates a 'stacked' balances graph showing different asset types
# NOTE: I believe this is a bar graph
#   @param      x_axis      this is a matrix of dimension N
#   @param      y_axis      this is a matrix of dimension [M, N]
#     https://stackoverflow.com/questions/21688402/stacked-bar-chart-space-between-y-axis-and-first-bar-matplotlib-pyplot
@logfn
def create_stack_line_chart(x_axis, y_axis, title=None, label=None, y_format=None):
    # TODO: just add some built-in sorting to this function. I know I implemented it somewhere else too

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

