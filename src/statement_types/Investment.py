"""
Class: Investment

Investment represents a single investment in an asset

"""

# import needed modules
import json
from googlefinance import getQuotes

# import user created modules
from analysis import investment_helper as invh
from statement_types.Transaction import Transaction



class Investment(Transaction):
    def __init__(self, date, account_id, category_id, amount, description, ticker, shares, note=None, sql_key=None):
        super.__init__(date, account_id, category_id, amount, description, note=None, sql_key=None)

        # add investment specific information
        self.ticker = ticker
        self.shares = shares

        self.price = invh.get_ticker_price(ticker)

