
# import needed modules
# from googlefinance import getQuotes - googlefinance yields HTTP 404 request
from yahoo_fin import stock_info
from db import db_helper
import json



##############################################################################
######      INDIVIDUAL TICKER FUNCTIONS      #################################
##############################################################################

def print_ticker_info(ticker):
    print("printing ticker info for ticker: ", ticker)
    price = stock_info.get_live_price(ticker)
    print(price)

    #print(json.dumps(quote, indent=2))


def get_ticker_price(ticker):
    price = stock_info.get_live_price(ticker)
    return price


##############################################################################
######      OVERALL ANALYSIS FUNCTIONS      ##################################
##############################################################################

def create_investment_dicts():
    inv_data = []
    inv_ledge = db_helper.get_inv_ledge_data()

    for ledge in inv_ledge:
        ledge_dict = {
            "ticker": ledge[3],
            "account": ledge[2],
            "shares": ledge[4],
            "type": ledge[7]

        }
        inv_data.append(ledge_dict)
    return inv_data
