"""
@file graphing_analyzer.py
@brief

"""

# import needed modules
import matplotlib.pyplot as plt
import os
import numpy as np
import plotly.graph_objects as go

# import user created modules
import analysis.graphing.graphing_helper as grah
from utils import BASEFILEPATH, IMAGE_FOLDER

# import logger
from loguru import logger

# Global counter for figure numbering
_figure_counter = 0


def save_fig():
    """Save the current matplotlib figure with an auto-incrementing number."""
    global _figure_counter
    _figure_counter += 1
    file_name = f"{_figure_counter:03d}.png"  # Zero-padded to 3 digits (001, 002, etc.)
    save_path = os.path.join(BASEFILEPATH, IMAGE_FOLDER, file_name)
    plt.savefig(save_path, bbox_inches="tight")
    print(f"Saved figure as: {save_path}")


def reset_figure_counter():
    """Reset the figure counter back to 0. Useful when starting a new analysis session."""
    global _figure_counter
    _figure_counter = 0


def show_plots():
    plt.show(block=False)


##############################################################################
####      SPENDING PLOTTING FUNCTIONS    #####################################
##############################################################################

def create_pie_chart(values, labels, explode=0.1, title="Pie Chart", legend=True):
    plt.rcdefaults() # sets rc defaults
    plt.clf() # clears the entire current figure with all its axes

    logger.debug("Running graphing_analyzer: create_pie_chart")
    fig = plt.figure(1)
    grah.get_pie_plot(values, labels, explode, title, legend=legend)
    return fig


# create_bar_chart:
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


# create_stack_bar_chart: creates a bar chart that is "stacked"
#   @param      x_axis      this is a matrix of dimension N
#   @param      y_axis      this is a matrix of dimension [M, N]
#     https://stackoverflow.com/questions/21688402/stacked-bar-chart-space-between-y-axis-and-first-bar-matplotlib-pyplot
def create_stack_bar_chart(x_axis, y_axis_arr, title=None, labels=None, y_label=None, y_format=None, sort_by_column="first"):
    ind = np.arange(len(x_axis))  # x positions
    width = 0.5

    # Determine the sorting column
    if sort_by_column == "first":
        column_index = 0
    elif sort_by_column == "last":
        column_index = -1
    else:
        raise ValueError("Invalid value for sort_by_column. Use 'first' or 'last'.")

    # Sort y_axis_arr and labels based on the specified column
    if labels:
        sorted_data = sorted(zip(y_axis_arr, labels), key=lambda x: x[0][column_index], reverse=False)
        y_axis_arr, labels = zip(*sorted_data)
    else:
        y_axis_arr = sorted(y_axis_arr, key=lambda x: x[column_index], reverse=False)


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

    # format y-axis as currency
    if y_format == 'currency':
        plt.gca().yaxis.set_major_formatter('${x:,.0f}')

    plt.tight_layout()
    plt.show()


# create_stack_line_chart: creates a line chart that is "stacked"
def create_stack_line_chart(x_axis, y_axis, title=None, label=None, y_format=None, sort_by_column="last"):
    plt.rcdefaults() # sets rc defaults
    plt.clf() # clears the entire current figure with all its axes

    # Determine the sorting column
    if sort_by_column == "first":
        column_index = 0
    elif sort_by_column == "last":
        column_index = -1
    elif sort_by_column is None:
        column_index = None  # No sorting
    else:
        raise ValueError("Invalid value for sort_by_column. Use 'first', 'last', or None.")

    # Sort y_axis and labels based on the specified column (largest at bottom)
    if column_index is not None:
        if label:
            sorted_data = sorted(zip(y_axis, label), key=lambda x: x[0][column_index], reverse=True)
            y_axis, label = zip(*sorted_data)
            y_axis = list(y_axis)
            label = list(label)
        else:
            y_axis = sorted(y_axis, key=lambda x: x[column_index], reverse=True)

    plt.stackplot(x_axis, y_axis, labels=label)
    plt.title(title)
    plt.axis("tight")

    # format y-axis as currency
    if y_format == 'currency':
        plt.gca().yaxis.set_major_formatter('${x:,.0f}')

    plt.legend(loc="upper left")

    save_fig()


def create_line_chart(x_axis, y_axis, title=None, legend=False, y_format=None, rotate_xticks=False):
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

    plt.title(title if title else 'Stacked Line Chart')

    if rotate_xticks:
        plt.xticks(rotation=90)
        plt.tight_layout()

    save_fig()


# create_mul_line_chart: creates multiple lines on same plot
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
        plt.xticks(rotation=45, ha="right")

    # add legend and title
    if legend:
        plt.legend(loc="best")

    # add grid lines
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.title(title)
    save_fig()


# Sankey diagrams visualize the contributions to a flow by defining source to represent
# the source node, target for the target node, value to set the flow volume, and label that shows the node name.
def generate_sankey(labels, sources, targets, values, title="Spending Sankey Diagram"):
    # Create the Sankey diagram
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=70, # this is the horizontal thickness,
            line=dict(color="black", width=1), # this is just the node border
            label=labels,
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
        )
    ))

    # Customize chart layout
    fig.update_layout(
        title_text=title,
        font_size=12,
    )

    # Display the chart
    # fig.show() # NOTE: this was working super well and then all of a sudden started freezing
    fig.write_html("tmp/plot.html", auto_open=True)