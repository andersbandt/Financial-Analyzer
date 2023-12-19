
# import needed modules
# from googlefinance import getQuotes - googlefinance yields HTTP 404 request

import yahoo_fin.stock_info as si

# import user created modules
import db.helpers as dbh
from utils import logfn

##############################################################################
######      INDIVIDUAL TICKER FUNCTIONS      #################################
##############################################################################


def validate_ticker(ticker):
    print(" ... validating ticker for ticker: ", ticker)
    try:
        price = si.get_live_price(ticker)
    except AssertionError as e:
        print(e)
        return False
    print("Found ticker with price: ", price)
    return True


# print_ticker_info: prints the info for a certain ticker to the console
# @logfn
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
# @logfn
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


# summarize_account: this function is for showcasing account view and holdings
# @logfn
def summarize_account(account_id, printmode=True):
    transactions = dbh.investments.get_active_ticker(account_id)
    print("\n\t ",
          dbh.account.get_account_name_from_id(account_id),
          ": "
          )

    account_value = 0
    for transaction in transactions:
        ticker = transaction[0]
        shares = transaction[1]

        # calculate the value of the asset ticker
        price = get_ticker_price(ticker)
        value = shares*price

        if printmode:
            # print("\n======================================= ")
            # print("\tticker: ", ticker)
            # print("\tshares: ", shares)
            # print("\tvalue: ", value)

            print(f"Ticker: {ticker}, Quantity: {shares}, Value: {value}")

        account_value += value

    return account_value


##############################################################################
######      DATABASE CONVERSION FUNCTIONS      ###############################
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

