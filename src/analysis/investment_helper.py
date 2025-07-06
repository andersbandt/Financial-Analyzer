
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

# import user created modules
import db.helpers as dbh
from tools import date_helper as dateh
from account import account_helper as acch
from analysis.data_recall import transaction_recall as transr
from cli import cli_printer as clip
from utils import internet_helper
from statement_types.Transaction import Transaction

# import logger
from utils import logfn

# XML filepath for saving money market tickers
MM_ACCOUNT_PATH = "C:/Users/ander/Documents/GitHub/Financial-Analyzer/src/db/mmticks.xml" # tag:hardcode


class InvestmentHelperError(Exception):
    def __init__(self, origin="InvestmentHelper", msg="Error encountered"):
        self.msg = f"{origin} error encountered: {msg}"
        return self.msg

    def __str__(self):
        return self.msg



class InvestmentTransaction(Transaction):
    def __init__(self, date, account_id, category_id, ticker, shares, value, trans_type, description, note=None,
                 sql_key=None):
        super().__init__(date, account_id, category_id, value, description, note, sql_key)


        self.ticker = ticker
        self.shares = shares
        self.trans_type = trans_type
        try:
            self.strike_price = self.value/self.shares
        except ZeroDivisionError:
            self.strike_price = -1
        self.price = 0
        self.gain = 0

        self.type = get_ticker_asset_type(ticker)

        self.update_price()
        self.value = self.price * self.shares

    def update_price(self):
        self.price = get_ticker_price(self.ticker)

    def get_price(self):
        return round(self.price, 2)

    def get_gain(self):
        try:
            self.gain = self.price/self.strike_price
            self.gain = (self.gain - 1)*100  # express gain in percent
        except ZeroDivisionError:
            self.gain = 0

        return round(self.gain, 3)

# TODO: somehow capture in Obsidian or something that this thing exists and like class structure and shit
    def print_trans(self, print_mode=True, include_sql_key=False):
        # add some InvestmentTransaction specific information
        prnt_str = " || TICKER: " + "".join(
            self.ticker + self.getSpaces(len(str(self.account_id)), 14))

        prnt_str = prnt_str + " || PRICE: " + "".join(
            "$ " + str(self.get_price()) + self.getSpaces(len(str(self.account_id)), 14))

        prnt_str = prnt_str + " || GAIN: " + "".join(
            str(self.get_gain()) + "%" + self.getSpaces(len(str(self.account_id)), 13))

        # add main Transaction stuff
        tmp_note = self.note
        self.note = None
        prnt_str = prnt_str + super().print_trans(print_mode=False, include_sql_key=include_sql_key, trim=35)
        self.note = tmp_note  # so hack lmao

        if print_mode:
            print(prnt_str)
        return prnt_str


# TODO: combine this with InvestmentTransaction? (delete Ticker?)
# class Ticker:
#     def __init__(self, ticker, shares):
#         self.ticker = ticker
#         self.shares = shares
#         self.price = get_ticker_price(ticker)
#         self.value = self.shares * self.price


# def create_ticker_from_transaction(transaction):
#     ticker = transaction[0]
#     shares = transaction[2]
#     ticker_class = Ticker(ticker, shares)
#     return ticker_class


##############################################################################
######      INDIVIDUAL TICKER FUNCTIONS      #################################
##############################################################################

def validate_ticker(ticker):
    print(" ... validating ticker for ticker: ", ticker)

    price = get_ticker_price(ticker)
    if price is False:
        return False

    print("Valid ticker found with price: ", price)
    return True


# print_ticker_info: prints the info for a certain ticker to the console
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
def get_ticker_price(ticker):
    # check for internet connection
    if not internet_helper.is_connected():
        print('Not connected to Internet!')
        return False


    # METHOD 1: download data from yf module
    warnings.filterwarnings("ignore", category=FutureWarning)
    try:
        data = yf.download(ticker,
                       start=datetime.datetime.now(datetime.UTC) - timedelta(days=2),
                       end=datetime.datetime.now(datetime.UTC))
    except requests.exceptions.JSONDecodeError:
        data = None
    warnings.filterwarnings("default")

    if not data.empty or data is not None:
        try:
            price = float(data['Close'].iloc[0])  # Ensures it's a float
            print(f"method 1: {price}")
            return price
        except IndexError:
            pass

    # METHOD 2: attempt to get live price using yahoo_fin. This method seems to always fail
    # try:
    #     price = si.get_live_price(ticker)
    #     if np.isnan(price):
    #         price = 0
    #     warnings.filterwarnings("default")
    #     print(f"method 2: {price}")
    #     return price
    # except (AssertionError, requests.exceptions.JSONDecodeError):
    #     pass

    return 0

# get_ticker_price_data: generates an array of historical price data
#   input for interval: "1d", "1wk", or "1m"
def get_ticker_price_data(ticker, start_date, end_date, interval, filter_weekdays=False):
    hist_price_data = si.get_data(
        ticker,
        start_date=start_date,
        end_date=end_date,
        index_as_date=False,
        interval=interval,
    )

    if filter_weekdays:
        print("Filtering to weekdays ONLY for ticker: ", ticker)
        # Convert the 'date' column to datetime format
        hist_price_data['date'] = pd.to_datetime(hist_price_data['date'])
        # Filter data for weekdays (Monday=0, Sunday=6)
        hist_price_data = hist_price_data[hist_price_data['date'].dt.dayofweek < 5]

    return hist_price_data


def ticker_info_dump(ticker):
    ticker = yf.Ticker(ticker)
    try:
        info = ticker.info  # NOTE: too many request rate limited error when trying to call this
        import pprint
        pprint.pprint(info)
        asset_type = info.get("quoteType")
        industry = info.get("industry")
        sector = info.get("sector")
        exchange = info.get("exchange")
        print(f"\nLooking at {ticker.ticker}")
        print(f"asset_type: {asset_type}")
        print(f"sector: {sector}")
        print(f"industry: {industry}")
        print(f"exchange: {exchange}")
    except Exception as e:
        print("ERROR: can't print ticker info")
        print(e)
        return None


def get_ticker_asset_type(ticker):
    ticker = yf.Ticker(ticker)
    info = ticker.info
    asset_type = info.get("quoteType")
    # industry = info.get("industry")
    # sector = info.get("sector")
    # exchange = info.get("exchange")
    # print(f"\nLooking at {ticker}")
    # print(quoteType)
    # print(industry)
    # print(sector)
    # print(exchange)
    return asset_type


##############################################################################
######      ACCOUNT FUNCTIONS               ##################################
##############################################################################

# retrives the ticker for an accounts money market (mm) account
def get_account_mm_ticker(account_id):
    """
    Retrieves the ticker symbol of a money market fund based on the given account_id from an XML file.

    Parameters:
        account_id (str or int): The account identifier.
        file_path (str): Path to the XML file containing account-to-ticker mappings.

    Returns:
        str: The ticker symbol of the money market fund, or None if not found.
    """
    try:
        # Parse the XML file
        tree = ET.parse(MM_ACCOUNT_PATH)
        root = tree.getroot()

        # Search for the account ID in the XML
        for account in root.findall("account"):
            if account.get("id") == str(account_id):
                return account.text  # Return the ticker symbol

        print(f"No money market fund found for account: {account_id}")
        return None

    except FileNotFoundError:
        print(f"Error: File '{MM_ACCOUNT_PATH}' not found.")
        return None
    except ET.ParseError:
        print(f"Error: Failed to parse XML file '{MM_ACCOUNT_PATH}'.")
        return None


##############################################################################
######      OVERALL ANALYSIS FUNCTIONS      ##################################
##############################################################################

# get_all_active_ticker: returns "active" tickers
def get_all_active_ticker():
    ticker_list = []
    transactions = transr.recall_investment_transaction()
    for transaction in transactions:
        if transaction.shares != 0:
            ticker_list.append(transaction)
    return ticker_list


def get_account_ticker_shares(account_id, ticker):
    ticker_tuple = dbh.investments.get_ticker_shares(account_id, ticker)
    if len(ticker_tuple) > 1:
        raise InvestmentHelperError(msg="Something is weird retrieving ticker shares per account")
    return ticker_tuple[0][2]


# summarize_account: this function is for showcasing account view and holdings
def summarize_account(account_id, printmode=True):
    # check for internet connection
    if not internet_helper.is_connected():
        print('Not connected to Internet!')
        return 0

    tickers = dbh.investments.get_account_ticker(account_id)
    account_value = 0
    ticker_table = []
    for ticker in tickers:
        transaction = dbh.investments.get_ticker_shares(account_id, ticker[0])
        #def __init__(self, date, account_id, category_id, ticker, shares, value, trans_type, description, note=None,sql_key=None):
        ticker = InvestmentTransaction("2000/1/1", account_id, -1, transaction[0], transaction[2], -1, -1, "description")


        if ticker.shares != 0:
            account_value += ticker.value
            ticker_table.append([
                ticker.ticker,
                ticker.shares,
                ticker.value,
                ticker.type])

    if printmode:
        print(f"\n\n\t {dbh.account.get_account_name_from_id(account_id)} : ")
        clip.print_variable_table(
            ["Ticker", "Shares", "Value", "Type"],
            ticker_table,
            format_finance_col=2
        )

    return account_value


##############################################################################
######      DATABASE FUNCTIONS      ##########################################
##############################################################################

@logfn
def create_active_investment_dict():
    inv_acc_id = acch.get_account_id_by_type(4)
    inv_ledge = []
    for account_id in inv_acc_id:
        inv_ledge.extend(dbh.investments.get_active_ticker(account_id))

    inv_data = []
    for ledge in inv_ledge:
        ledge_dict = {
            "ticker": ledge[0],
            "account": ledge[1],
            "shares": ledge[2],
        }
        inv_data.append(ledge_dict)
    return inv_data


def delete_investment_list(sql_key_arr):
    for key in sql_key_arr:
        dbh.investments.delete_investment(key)
