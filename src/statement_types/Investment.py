"""
Class: Investment

Investment represents a single investment in an asset

"""
from statement_types.Transaction import Transaction
from datetime import date  # needed to get current date
from googlefinance import getQuotes
import json


class Investment(Transaction):
    def __init__(self, ticker, shares, account_id, *args):
        self.ticker = ticker
        self.shares = shares
        self.account_id = account_id


    # get_current_value: gets the current value of the investment
    def get_current_value(self):
        # get stock information
        info = getQuotes(self.ticker)  # For example: "AAPL", "MSFT", etc.
        stuff = json.dumps(info)
        final = ""
        for i in range(118, 123):
            final += stuff[i]
        price = float(final)

        return self.shares * price
