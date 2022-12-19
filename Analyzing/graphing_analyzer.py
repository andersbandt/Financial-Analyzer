
# import needed modules
import numpy as np

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import datetime
from datetime import date

from analyzing import analyzer_helper
from analyzing import graphing_helper
from analyzing import inv_h
from Finance_GUI import gui_helper
from tools import date_helper

##############################################################################
####      SPENDING PLOTTING FUNCTIONS    #####################################
##############################################################################

# TODO: add amounts
# TODO: feature idea. Figure out how to create list of final items that you can click "on" or "off" to toggle visibility.
# piChartExpenseSummary: plots a pie chart of expenses
# input: statement
# output: none (plots pie chart)
def create_pie_chart(transactions, categories, printmode=None):
    print("Running graphing_analyzer: create_pie_chart")

    # create an array of category strings and array of amount floats
    #   using an array of Transactions and an array of Category objects
    categories, amounts = analyzer_helper.create_category_amounts_array(transactions, categories)

    # strip transaction data
    categories, amounts = graphing_helper.strip_non_graphical_transactions(categories, amounts)
    categories, amounts = graphing_helper.strip_non_expense_categories(categories, amounts)
    categories, amounts = graphing_helper.strip_zero_categories(categories, amounts)
    amounts = graphing_helper.format_expenses(amounts)

    # print Transaction list to console
    if printmode is not None:
        for i in range(0, len(amounts)-1):
            graphing_helper.print_category_amount(categories[i], amounts[i])

    #  create and return figure
    fig = plt.figure(1)
    graphing_helper.get_pie_plot(amounts, categories, explode=.1, title="Pie Chart")
    return fig, categories, amounts


# create_top_pie_chart: return a pyplot figure of a summation of all top level categories
def create_top_pie_chart(transactions, categories, printmode=None):
    print("Running graphing_analyzer: create_top_pie_chart")

    # initialize array
    categories, amounts = analyzer_helper.create_top_category_amounts_array(transactions, categories)

    # strip data and format
    categories, amounts = graphing_helper.strip_non_graphical_transactions(categories, amounts)
    categories, amounts = graphing_helper.strip_non_expense_categories(categories, amounts)
    amounts = graphing_helper.format_expenses(amounts)

    # error handle generated categories and amounts array
    if len(categories) != len(amounts):
        print("Categories is not the same length as amounts")
        gui_helper.alert_user("Error generating graph.", "Generated categories is not the same length as generated amounts", "error")

    # print categories and amounts in console
    if printmode is not None:
        for i in range(0, len(amounts) - 1):
            graphing_helper.print_category_amount(categories[i], amounts[i])

    #  create and return figure
    fig = plt.figure(1)
    patches, texts = graphing_helper.get_pie_plot(amounts, categories, explode=.1, title="Top Level Data")
    return fig


# create_bar_chart:
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


##############################################################################
####      BALANCES PLOTTING FUNCTIONS    ###################################
##############################################################################

# figure out how to carry forward A vector and only
# https://stackoverflow.com/questions/21688402/stacked-bar-chart-space-between-y-axis-and-first-bar-matplotlib-pyplot
def create_stacked_balances(days_prev, N):

    spl_Bx = analyzer_helper.gen_Bx_matrix(days_prev, N)

#     # init today date object
#     today = date.today()
#
#     # init date object 'days_prev' less
#     d = datetime.timedelta(days=days_prev)  # this variable can only be named d. No exceptions. Ever.
#     a = today - d  # compute the date (today - timedelta)
#
#     # FORMATING IS NOT NEEDED WITH ABOVE METHOD TODO: FIGURE OUT WHY the below methods need formatting?
#     #formatted_today = scraping_helper.format_date_string(today)
#     #formatted_end = scraping_helper.format_date_string(a)
#
#     B = db_helper.get_balances_between_date(a, today)  # balance data
#
#
# # TODO: this function needs to 'carry foward' the dominant A vector and replace values (regardless of up/down status)
# #   if there is a new account id info
#     # init A vector
#     a_A = {}
#     for account_id in db_helper.get_all_account_ids():
#         a_A[account_id] = 0
#

    ##################################################################################
    ### SET WHICH ACCOUNT_IDS CORRESPOND TO WHAT TYPE OF ACCOUNT
    inv_acc = [3]
    liquid_acc = [0, 1]
    ##################################################################################

    # error handling on amount of binning done to balances
    if len(spl_Bx) != N:
        print("Length of spl_Bx: ", len(spl_Bx))
        print("N is:", str(N))
        raise BaseException("FUCK YOU BITCH YOUR spl_Bx array is not of length N it is length ", len(spl_Bx))

    #investment = []  # array for investment assets+  !NOTE!THIS MUST BE THE LENGTH OF N
    #liquid = []  # array for liquid assets !NOTE! THIS BUST THE LENGTH OF N

    investment, liquid = analyzer_helper.gen_bin_A_matrix(spl_Bx, inv_acc, liquid_acc)

    ### create the stacked bar plt objects ##
    # set params
    ind = np.arange(N)
    width = 0.5
    scale_factor = 1000

    inv_color = "#20774c"  # dark green
    liq_color = "#202377"  # dark blue

    # resize investment data based on scale factor
    for i in range(0, len(investment)):
        investment[i] = investment[i]/scale_factor
        liquid[i] = liquid[i]/scale_factor

    # create the objects
    fig = plt.figure(1)

    p1 = plt.bar(ind, investment, width, color=inv_color)
    p2 = plt.bar(ind, liquid, width, color=liq_color, bottom=investment)

    # set general plot info
    plt.title('Total of Balances for previous ' + str(days_prev) + " days")
    plt.legend((p1[0], p2[0]), ('Investment', 'Liquid'), loc=2, frameon='false')

    # set X axis (date) info
    date_ticks = []  # this array should be of length N
    for edge in date_helper.get_edge_code_dates(date.today(), days_prev, N):
        date_ticks.append(edge.strftime("%Y-%m-%d"))
    date_ticks.append(date.today().strftime("%Y-%m-%d"))  # add today
    plt.xticks(ind + width / 2., date_ticks)

    # set Y axis (balance $) info
    max_val = 200000
    max_val_s = max_val/scale_factor
    ticks = 10

    plt.ylabel('Amount (k dollaz $)')
    plt.yticks(np.arange(0, max_val_s, max_val_s/ticks))  # sets the y axis scaling and step size
    plt.tick_params(top='off', bottom='off', right='off')

    plt.grid(axis='y', linestyle='-')

    return fig


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
    graphing_helper.get_pie_plot(amounts, labels, explode=.1, title="Asset Allocation")
    return fig


