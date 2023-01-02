# import needed modules
# from googlefinance import getQuotes - googlefinance yields HTTP 404 request
import json

import yahoo_fin.stock_info as si

import db.helpers as dbh
from utils import logfn

##############################################################################
######      INDIVIDUAL TICKER FUNCTIONS      #################################
##############################################################################

# print_ticker_info: prints the info for a certain ticker to the console
@logfn
def print_ticker_info(ticker):
    print("printing ticker info for ticker: ", ticker)

    # get price and analyst info
    price = si.get_live_price(ticker)
    info = si.get_analysts_info(ticker)

    # print to console
    print("Price: ", price)
    print("Info: ", info)
    return


# get_ticker_price: returns the current live price for a certain ticker
@logfn
def get_ticker_price(ticker):
    price = si.get_live_price(ticker)
    return price


# get_ticker_price_data: generates an array of historical price data
#   input for interval: "1d", "1wk", or "1m"
@logfn
def get_ticker_price_data(ticker, start_date, end_date, interval):
    hist_price_data = si.get_data(
        ticker,
        start_date=start_date,
        end_date=end_date,
        index_as_date=False,
        interval=interval,
    )
    print(hist_price_data)
    return hist_price_data


##############################################################################
######      OVERALL ANALYSIS FUNCTIONS      ##################################
##############################################################################


@logfn
def create_investment_dicts():
    inv_data = []
    inv_ledge = dbh.investments.get_inv_ledge_data()

    for ledge in inv_ledge:
        ledge_dict = {
            "ticker": ledge[3],
            "account": ledge[2],
            "shares": ledge[4],
            "type": ledge[7],
        }
        inv_data.append(ledge_dict)
    return inv_data
