
# import needed modules
import numpy as np
from datetime import date
import matplotlib.pyplot as plt

# import user created modules
import analysis.analyzer_helper as anah
import analysis.graphing_helper as grah
import analysis.investment_helper as invh
from tools import date_helper

# import logger
from utils import logfn
from loguru import logger


# TODO: This module can remain, but needs a lot of cleanup


@logfn
class GraphingAnalyzerError(Exception):
    """Graphing Analyzer Error"""

    def __init__(self, origin="Graphing Analyzer", msg="Error encountered"):
        self.msg = f"{origin} error encountered: {msg}"
        return self.msg

    def __str__(self):
        return self.msg




##############################################################################
####      SPENDING PLOTTING FUNCTIONS    #####################################
##############################################################################


@logfn
def create_pie_chart(transactions, categories, printmode=None):
    logger.debug("Running graphing_analyzer: create_pie_chart")

    # create an array of category strings and array of amount floats
    #   using an array of Transactions and an array of Category objects
    categories, amounts = analyzer_helper.create_category_amounts_array(
        transactions, categories
    )

    # strip transaction data
    categories, amounts = graphing_helper.strip_non_graphical_transactions(
        categories, amounts
    )
    categories, amounts = graphing_helper.strip_non_expense_categories(
        categories, amounts
    )
    categories, amounts = graphing_helper.strip_zero_categories(categories, amounts)
    amounts = graphing_helper.format_expenses(amounts)

    # print Transaction list to console
    if printmode is not None:
        for i in range(0, len(amounts) - 1):
            graphing_helper.print_category_amount(categories[i], amounts[i])

    #  create and return figure
    fig = plt.figure(1)
    graphing_helper.get_pie_plot(amounts, categories, explode=0.1, title="Pie Chart")
    return fig, categories, amounts


# create_top_pie_chart: return a pyplot figure of a summation of all top level categories
@logfn
def create_top_pie_chart(transactions, categories, printmode=None):
    logger.debug("Running graphing_analyzer: create_top_pie_chart")

    # initialize array
    categories, amounts = analyzer_helper.create_top_category_amounts_array(
        transactions, categories
    )

    # strip data and format
    categories, amounts = graphing_helper.strip_non_graphical_transactions(
        categories, amounts
    )
    categories, amounts = graphing_helper.strip_non_expense_categories(
        categories, amounts
    )
    amounts = graphing_helper.format_expenses(amounts)

    # error handle generated categories and amounts array
    if len(categories) != len(amounts):
        logger.info("Categories is not the same length as amounts")
        gui_helper.alert_user(
            "Error generating graph.",
            "Generated categories is not the same length as generated amounts",
            "error",
        )

    # print categories and amounts in console
    if printmode is not None:
        for i in range(0, len(amounts) - 1):
            graphing_helper.print_category_amount(categories[i], amounts[i])

    #  create and return figure
    fig = plt.figure(1)
    patches, texts = graphing_helper.get_pie_plot(  # TODO: return values not being used
        amounts, categories, explode=0.1, title="Top Level Data"
    )
    return fig


# create_bar_chart:
@logfn
def create_bar_chart(labels, values, xlabel=None, title=None):
    logger.debug("Running graphing_analyzer: create_pie_chart")
    plt.rcdefaults()
    fig, ax = plt.subplots()
    grah.get_bar_chart([ax], 0, labels, values, title)

    if xlabel is not None:
        ax.set_xlabel(xlabel)

    plt.show()


# TODO: add support for labels
@logfn
def create_stackline_chart(x_axis, y_axis, title=None, label=None, y_format=None):
    plt.stackplot(x_axis, y_axis, labels=label)
    plt.title(title)
    plt.axis("tight")

    # format y-axis as currency
    if y_format == 'currency':
        plt.gca().yaxis.set_major_formatter('${x:,.0f}')

    plt.legend(loc="best")

    # plt.show()
    plt.show(block=False)


def create_line_chart(x_axis, y_axis, title=None, legend=False, y_format=None):
    plt.clf()

    grah.get_line_chart(x_axis,
                        y_axis,
                        color='purple')

    # format y-axis as currency
    if y_format == 'currency':
        plt.gca().yaxis.set_major_formatter('${x:,.0f}')

    # add legend and title
    if legend:
        plt.legend(loc="best")

    # add grid lines
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.title(title)
    plt.show()


# create_mul_line_chart: creates multiple
# THIS FUNCTION WORKS IN CLI VERSIoN
def create_mul_line_chart(x_axis, y_axis_arr, title=None, labels=[], legend=False, y_format=None):
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

    # add legend and title
    if legend:
        plt.legend(loc="best")

    # add grid lines
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.title(title)
    plt.show()


@logfn
def create_summation_vs_time(transactions, categories):
    exec_summary = analyzer_helper.return_transaction_exec_summary(transactions)
    logger.info(
        f"create_summation_vs_time got this for expenses {exec_summary['expenses']}"
    )
    logger.info(
        f"create_summation_vs_time got this for incomes {exec_summary['incomes']}"
    )


##############################################################################
####      BALANCES PLOTTING FUNCTIONS    ###################################
##############################################################################

# create_stacked_balances: creates a 'stacked' balances graph showing different asset types
#     https://stackoverflow.com/questions/21688402/stacked-bar-chart-space-between-y-axis-and-first-bar-matplotlib-pyplot
@logfn
def create_stacked_balances(days_prev, N):
    # create the stacked bar chart figure
    fig = plt.figure(1)
    grah.get_stacked_bar_chart(
        ind, investment, liquid, title, width, scale_factor, x_ticks=date_ticks
    )
    return fig


# TODO: can't figure out this function until I get a good way to SET WHICH ACCOUNT_IDS CORRESPOND TO WHAT TYPE OF ACCOUNT
@logfn
def create_liquid_over_time(days_prev, N):
    pass


##############################################################################
####      INVESTMENT PLOTTING FUNCTIONS    ###################################
##############################################################################

# create_asset_alloc_chart: creates a pie chart representing asset allocation
@logfn
def create_asset_alloc_chart():
    # get list of investment dict objects
    inv_dict = invh.create_investment_dicts()

    # set up investment types to track totals
    t_1 = 0
    t_2 = 0
    t_3 = 0
    t_4 = 0
    t_5 = 0

    # iterate through list and add to totals
    for investment in inv_dict:
        if investment["type"] == 1:
            value = investment["shares"] * invh.get_ticker_price(investment["ticker"])
            t_1 += value
        elif investment["type"] == 2:
            value = investment["shares"] * invh.get_ticker_price(investment["ticker"])
            t_2 += value
        elif investment["type"] == 3:
            value = investment["shares"] * invh.get_ticker_price(investment["ticker"])
            t_3 += value
        elif investment["type"] == 4:
            value = investment["shares"] * invh.get_ticker_price(investment["ticker"])
            t_4 += value
        elif investment["type"] == 5:
            value = investment["shares"] * invh.get_ticker_price(investment["ticker"])
            t_5 += value

    amounts = [t_1, t_2, t_3, t_4, t_5]
    labels = ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5"]

    #  create and return figure
    fig = plt.figure(1)
    grah.get_pie_plot(amounts, labels, explode=0.1, title="Asset Allocation")
    return fig


