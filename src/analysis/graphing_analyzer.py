# import needed modules
import matplotlib
import numpy as np

matplotlib.use("TkAgg")

from datetime import date

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import analysis.analyzer_helper as analyzer_helper
import analysis.graphing_helper as graphing_helper
import analysis.inv_h as inv_h
from gui import gui_helper
from tools import date_helper

##############################################################################
####      SPENDING PLOTTING FUNCTIONS    #####################################
##############################################################################

# piChartExpenseSummary: plots a pie chart of expenses
#    input: statement
#    output: none (plots pie chart)
def create_pie_chart(transactions, categories, printmode=None):
    print("Running graphing_analyzer: create_pie_chart")

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
def create_top_pie_chart(transactions, categories, printmode=None):
    print("Running graphing_analyzer: create_top_pie_chart")

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
        print("Categories is not the same length as amounts")
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
    patches, texts = graphing_helper.get_pie_plot(
        amounts, categories, explode=0.1, title="Top Level Data"
    )
    return fig


# create_bar_chart:
def create_bar_chart(transactions, categories):
    print("Running graphing_analyzer: create_pie_chart")

    categories, amounts = analyzer_helper.create_category_amounts_array(
        transactions, categories
    )
    categories, amounts = graphing_helper.strip_non_graphical_transactions(
        categories, amounts
    )

    plt.rcdefaults()
    fig, ax = plt.subplots()

    y_pos = np.arange(len(categories))

    ax.barh(y_pos, amounts, align="center", color="green", ecolor="black")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel("Amount ($)")
    ax.set_title("Financial Bar Chart")

    plt.show()


def create_summation_vs_time(transactions, categories):
    exec_summary = analyzer_helper.return_transaction_exec_summary(transactions)
    print("create_summation_vs_time got this for expenses", exec_summary["expenses"])
    print("create_summation_vs_time got this for incomes", exec_summary["incomes"])


##############################################################################
####      BALANCES PLOTTING FUNCTIONS    ###################################
##############################################################################

# create_stacked_balances: creates a 'stacked' balances graph showing different asset types
#     https://stackoverflow.com/questions/21688402/stacked-bar-chart-space-between-y-axis-and-first-bar-matplotlib-pyplot
def create_stacked_balances(days_prev, N):

    # generate matrix of Bx values
    spl_Bx = analyzer_helper.gen_Bx_matrix(days_prev, N)

    ##################################################################################
    ### SET WHICH ACCOUNT_IDS CORRESPOND TO WHAT TYPE OF ACCOUNT
    inv_acc = [3]
    liquid_acc = [0, 1]
    ##################################################################################

    # error handling on amount of binning done to balances
    if len(spl_Bx) != N:
        print("Length of spl_Bx: ", len(spl_Bx))
        print("N is:", str(N))
        raise BaseException(
            "FUCK YOU BITCH YOUR spl_Bx array is not of length N it is length ",
            len(spl_Bx),
        )

    # investment = []  # array for investment assets+  !NOTE!THIS MUST BE THE LENGTH OF N
    # liquid = []  # array for liquid assets !NOTE! THIS BUST THE LENGTH OF N

    investment, liquid = analyzer_helper.gen_bin_A_matrix(spl_Bx, inv_acc, liquid_acc)

    # set graph params
    ind = np.arange(N)
    width = 0.5
    scale_factor = 1000

    # set graph title and x labels
    title = "Total of Balances for previous " + str(days_prev) + " days"

    date_ticks = []  # this array should be of length N
    for edge in date_helper.get_edge_code_dates(date.today(), days_prev, N):
        date_ticks.append(edge.strftime("%Y-%m-%d"))
    date_ticks.append(date.today().strftime("%Y-%m-%d"))  # add today

    # resize investment data based on scale factor
    for i in range(0, len(investment)):
        investment[i] = investment[i] / scale_factor
        liquid[i] = liquid[i] / scale_factor

    # create the stacked bar chart figure
    fig = plt.figure(1)
    graphing_helper.get_stacked_bar_chart(
        ind, investment, liquid, title, width, scale_factor, x_ticks=date_ticks
    )
    return fig


# TODO: can't figure out this function until I get a good way to SET WHICH ACCOUNT_IDS CORRESPOND TO WHAT TYPE OF ACCOUNT
def create_liquid_over_time(days_prev, N):
    pass


##############################################################################
####      INVESTMENT PLOTTING FUNCTIONS    ###################################
##############################################################################

# create_asset_alloc_chart: creates a pie chart representing asset allocation
def create_asset_alloc_chart():
    # get list of investment dict objects
    inv_dict = inv_h.create_investment_dicts()

    # set up investment types to track totals
    t_1 = 0
    t_2 = 0
    t_3 = 0
    t_4 = 0
    t_5 = 0

    # iterate through list and add to totals
    for investment in inv_dict:
        if investment["type"] == 1:
            value = investment["shares"] * inv_h.get_ticker_price(investment["ticker"])
            t_1 += value
        elif investment["type"] == 2:
            value = investment["shares"] * inv_h.get_ticker_price(investment["ticker"])
            t_2 += value
        elif investment["type"] == 3:
            value = investment["shares"] * inv_h.get_ticker_price(investment["ticker"])
            t_3 += value
        elif investment["type"] == 4:
            value = investment["shares"] * inv_h.get_ticker_price(investment["ticker"])
            t_4 += value
        elif investment["type"] == 5:
            value = investment["shares"] * inv_h.get_ticker_price(investment["ticker"])
            t_5 += value

    amounts = [t_1, t_2, t_3, t_4, t_5]
    labels = ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5"]

    #  create and return figure
    fig = plt.figure(1)
    graphing_helper.get_pie_plot(amounts, labels, explode=0.1, title="Asset Allocation")
    return fig


# create_asset_alloc_chart: creates a pie chart representing asset allocation
def create_hist_price_data_line_chart(days_prev=180):
    # get list of investment dict objects
    inv_dict = inv_h.create_investment_dicts()

    # set up array to handle historical price data
    total = []

    # set up date based on days_prev
    end_date = date.today()
    start_date = date_helper.get_date_days_prev(end_date, days_prev)

    # populate array holding dates (x-axis of chart)
    dates = list(range(days_prev))

    # iterate through list and add to totals
    for investment in inv_dict:
        print("INFO: retrieving historical stock price data for portfolio")
        print("Starting date: ", start_date)
        print("Ending date: ", end_date)
        hist_data = inv_h.get_ticker_price_data(
            investment["ticker"], start_date, end_date, interval="1d"
        )

    totals = list(range(days_prev))

    #  create and return figure
    fig = plt.figure(1)
    graphing_helper.get_line_chart(
        dates, totals, title="Historical Portfolio Performance"
    )
    return fig
