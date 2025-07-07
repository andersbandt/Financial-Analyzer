
# import needed modules
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import yahoo_fin.stock_info as si
import yfinance as yf
import warnings
import xml.etree.ElementTree as ET
import requests
import plotly.graph_objects as go


def get_last_trading_day():
    today = datetime.datetime.now()
    weekday = today.weekday()

    if weekday == 5:  # Saturday
        return today - timedelta(days=1)
    elif weekday == 6:  # Sunday
        return today - timedelta(days=2)
    else:
        return today


def get_ticker_price(ticker):
    # METHOD 1: download data from yf module
    # warnings.filterwarnings("ignore", category=FutureWarning)
    # try:
    #     data = yf.download(ticker,
    #                    start=get_last_trading_day() - timedelta(1),
    #                    end=get_last_trading_day())
    # except requests.exceptions.JSONDecodeError:
    #     data = None
    # warnings.filterwarnings("default")
    #
    # if not data.empty or data is not None:
    #     try:
    #         price = float(data['Close'].iloc[0])  # Ensures it's a float
    #         print(f"method 1: {price}")
    #         return price
    #     except IndexError:
    #         pass

    # METHOD 2: attempt to get live price using yahoo_fin. This method seems to always fail
    try:
        price = si.get_live_price(ticker)
        print("hey fuckface below is method 2 price")
        print(price)
        if np.isnan(price):
            price = 0
        warnings.filterwarnings("default")
        print(f"method 2: {price}")
        return price
    except (AssertionError, requests.exceptions.JSONDecodeError):
        print("yeppp ERROR BITCH")

    return 0




ticker = "VBTLX"  # example mutual fund ticker, Vanguard Total Stock Market Index Fund
mf = yf.Ticker(ticker)

# Try fetching historical price data
hist = mf.history(period="5d")
print(hist)

#get_ticker_price("VBTLX")

# labels = ['MEDIA', 'RIDESHARE', 'MISC FINANCE', 'BARS', 'HEALTH', 'PAYMENT', 'FEE', 'CLOTHING', 'HYGIENE', 'FAST FOOD', 'RACES', 'LODGING', 'TRAVEL', 'LIQOUR' \
# 'STORE', 'REWARDS', 'INTERNAL', 'TRANSPORTATION', 'ELECTRONICS', 'TRANSFER', 'EATING OUT', 'MAKING', 'PAYCHECK', 'RESTAURANT', 'LIVING', 'GAS', 'GIFT', 'SHOPPING', \
#           'TAX', 'HOUSING', 'INTEREST', 'COSMETICS', 'EYECARE', 'LESIURE', 'FOOD AND DRINK', 'CAR_INSRANCE', 'COMPUTER', 'HAIRCUT', 'RENT', 'SHOWS', 'KITCHEN', \
#     'HOUSEHOLD', 'AIRPLANE', 'HOBBIES', 'INTERNET', 'ENERGY', 'THC', 'GROCERY', 'VISION', 'CAR', 'DENTIST', 'CAFFIENE', 'GIVING', 'INCOME', 'NA', 'PARKING']

#
# for i in range(0, len(labels)):
#     print(f"{i}: {labels[i]}")


# sources = [21, 32, 15, 21, 4, 2, 33, 52, 15, 52, 33, 33, 32, 2, 21, 21, 28, 32, 19, 33, 48, 21, 4, 48, 21, 21, 8, 28, 16, 20, 19, 16, 2, 33, 28, 2, 26, 21, 23
# , 42, 40, 21, 42, 4, 32, 12, 16, 52, 2, 4, 48, 4]
#
# targets = [0, 12, 5, 4, 49, 25, 19, 29, 18, 21, 50, 3, 42, 6, 32, 28, 37, 45, 9, 46, 34, 26, 31, 24, 16, 23, 30, 44, 41, 17, 22, 1, 27, 13, 43, 14, 7, 33, 35,
#  10, 39, 53, 20, 8, 38, 11, 48, 52, 51, 47, 54, 36]
#
# values = [-279.1, -3093.5299999999997, 10429.78, -251.12, -159.57, 14970.830000000002, -1583.1600000000014, 0.65,
#           -46183.479999999996, 61562.450000000004, -315.26999999999987, -2365.2699999999995, -289.62, -229.82,
#           -1599.43, -124.76, -13263.36, -570.11, -701.32, -3379.82, -1008.0, -3768.1900000000005, -20.0, -762.9899999999999,
#           -413.23, -240.0, -422.4, -788.6999999999999, -2905.5, -749.37, -2505.42, -1011.27, 2151.0, -331.55, -374.4, 107.64999999999999,
#           -238.83000000000004, -88.99, -442.83, -103.13, -9.72, -130.46, -193.75, -65.0, -44.0, -399.46, -1954.64, 4173.19, -40.0,
#           -318.7, -5.0, -180.0]
#
#
# for i in range(0, len(values)):
#     values[i] = abs(values[i])
#
#
#
# # labels = ["A1", "A2", "B1", "B2", "C1", "C2"]
# # sources = [0, 1, 0, 2, 3, 3]  # indices correspond to labels, eg A1, A2, A1, B1, ...
# # targets = [2, 3, 3, 4, 4, 5]
# # values = [8, 4, 2, 8, 4, 2]
#
#
# # Create the Sankey diagram
# fig = go.Figure(go.Sankey(
#     node=dict(
#         pad=15,
#         thickness=20,
#         line=dict(color="black", width=0.5),
#         label=labels,
#     ),
#     link=dict(
#         source=sources,
#         target=targets,
#         value=values,
#     )
# ))
#
#
# # fig.show()
# fig.write_html('plot.html', auto_open=True)


