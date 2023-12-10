

# imported needed modules
import yfinance as yf

# import user created modules
import db.helpers as dbh


def get_ticker_value(ticker):
    try:
        stock_data = yf.Ticker(ticker)
        current_value = stock_data.info["regularMarketPrice"]
        return current_value
    except Exception as e:
        print("Error:", e)
        return None


def get_investment_value(ticker, shares):
    ticker_price = get_ticker_value(ticker)
    return int(ticker_price*shares)



def get_active_acc_ticker(account_id):
    # ledge_data = dbh.investments.get_investment_ledge_data()
    tickers = dbh.investments.get_active_ticker(account_id)
    return tickers


def generate_inv_acc_summary(account_arr):
    sum_dict = {}

    for account in account_arr:
        tickers = get_active_acc_ticker(account)
        total_value = 0
        for ticker in tickers:
            price = get_ticker_value(ticker)
            value = price*shares
            total_value += value

        sum_dict[account] = total_value


