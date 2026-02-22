# import needed modules
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import time
import yahoo_fin.stock_info as si
import yfinance as yf
import xml.etree.ElementTree as ET
import yfinance.exceptions

# import user created modules
import db.helpers as dbh
from account import account_helper as acch
from analysis.data_recall import transaction_recall as transr
from cli import cli_printer as clip
from utils import internet_helper
from statement_types.Transaction import Transaction

# XML filepath for saving money market tickers
MM_ACCOUNT_PATH = "C:/Users/ander/Documents/GitHub/Financial-Analyzer/src/db/mmticks.xml"  # tag:hardcode

# Finnhub API configuration
# Get your free API key at https://finnhub.io/register
FINNHUB_API_KEY = "d632gspr01qnpqnvib80d632gspr01qnpqnvib8g"  # tag:hardcode

# Price cache: {ticker: price} - lasts entire program run
_PRICE_CACHE = {}

# Asset type cache: {ticker: asset_type} - lasts entire program run
_ASSET_TYPE_CACHE = {}

# Initialize Finnhub client (lazy loaded)
_finnhub_client = None


def get_finnhub_client():
    """Get or create Finnhub client instance."""
    global _finnhub_client
    if _finnhub_client is None:
        try:
            import finnhub
            if FINNHUB_API_KEY != "YOUR_API_KEY_HERE" and FINNHUB_API_KEY != "d632gspr01qnpqnvib80d632gspr01qnpqnvib8g":
                _finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
                print("✓ Finnhub client initialized")
            elif FINNHUB_API_KEY == "d632gspr01qnpqnvib80d632gspr01qnpqnvib8g":
                _finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
                print("✓ Finnhub client initialized (will fall back to Yahoo for unsupported tickers)")
            else:
                print("⚠️  Finnhub API key not configured (using fallback sources)")
        except ImportError:
            print("⚠️  finnhub-python not installed. Install with: pip install finnhub-python")
    return _finnhub_client


class InvestmentHelperError(Exception):
    def __init__(self, origin="InvestmentHelper", msg="Error encountered"):
        self.msg = f"{origin} error encountered: {msg}"
        super().__init__(self.msg)

    def __str__(self):
        return self.msg



class InvestmentTransaction(Transaction):
    def __init__(self, date, account_id, category_id, ticker, shares, value, trans_type, description, note=None,
                 sql_key=None, live_price=True):
        super().__init__(date, account_id, category_id, value, description, note, sql_key)

        self.ticker = ticker
        self.shares = shares
        self.trans_type = trans_type
        try:
            self.strike_price = self.value / self.shares
        except ZeroDivisionError:
            self.strike_price = -1
        self.price = 0
        self.gain = 0

        # Only fetch live data if live_price=True
        if live_price:
            self.type = get_ticker_asset_type(ticker)
            self.update_price()
            self.value = self.price * self.shares
        else:
            # Use cached data or placeholder when not fetching live prices
            self.type = _ASSET_TYPE_CACHE.get(ticker, "UNKNOWN")
            self.price = self.strike_price  # Use historical strike price
            # self.value keeps the value passed to constructor

    def update_price(self):
        """Update the current price for this ticker (uses caching)."""
        self.price = get_ticker_price(self.ticker)

    def get_price(self):
        return round(self.price, 2)

    def get_gain(self):
        try:
            self.gain = self.price / self.strike_price
            self.gain = (self.gain - 1) * 100  # express gain in percent
        except ZeroDivisionError:
            self.gain = 0

        return round(self.gain, 3)

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


##############################################################################
######      INDIVIDUAL TICKER FUNCTIONS      #################################
##############################################################################

def validate_ticker(ticker):
    """Validate that a ticker exists and has a fetchable price."""
    print(f" ... validating ticker: {ticker}")

    price = get_ticker_price(ticker)
    if price == 0:
        print(f"Invalid ticker or unable to fetch price for: {ticker}")
        return False

    print(f"Valid ticker found with price: ${price:.2f}")
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


# TODO (LOW PRIORITY): this thing doesn't account for holidays that occur on a Friday. Kind of fixed it with always going 1 BEFORE last trading day
def get_last_trading_day():
    today = datetime.datetime.now()
    weekday = today.weekday()

    if weekday == 5:  # Saturday
        return today - timedelta(days=1)
    elif weekday == 6:  # Sunday
        return today - timedelta(days=2)
    else:
        return today


def clear_price_cache():
    """Clear the price cache. Useful for forcing fresh data."""
    global _PRICE_CACHE
    _PRICE_CACHE = {}
    print("Price cache cleared")


def clear_asset_type_cache():
    """Clear the asset type cache. Useful for forcing fresh data."""
    global _ASSET_TYPE_CACHE
    _ASSET_TYPE_CACHE = {}
    print("Asset type cache cleared")


def clear_all_caches():
    """Clear all caches (price and asset type)."""
    clear_price_cache()
    clear_asset_type_cache()


def get_cache_stats():
    """Return cache statistics for debugging."""
    return {
        "cached_prices": len(_PRICE_CACHE),
        "cached_asset_types": len(_ASSET_TYPE_CACHE)
    }


# get_ticker_price: returns the current live price for a certain ticker
def get_ticker_price(ticker, use_cache=True, max_retries=2):
    """
    Get current price for a ticker with multi-source fallback and caching.

    Tries multiple data sources in order:
    1. Finnhub (60 calls/min, most reliable)
    2. yfinance (fast_info) - fallback
    3. yahoo_fin (si.get_live_price) - fallback #2
    4. yfinance (history) - last resort

    Args:
        ticker: Stock ticker symbol
        use_cache: Whether to use cached prices (default True)
        max_retries: Number of retries on rate limit (default 2)

    Returns:
        float: Current price, or 0 if unable to fetch
    """
    # Check internet connection
    if not internet_helper.is_connected():
        print(f'Not connected to Internet! Cannot fetch price for {ticker}')
        return 0

    # Check cache first (no expiration - lasts entire program run)
    if use_cache and ticker in _PRICE_CACHE:
        return _PRICE_CACHE[ticker]

    # METHOD 1: Try Finnhub (60 calls/min - best option!)
    finnhub_client = get_finnhub_client()
    if finnhub_client:
        try:
            quote = finnhub_client.quote(ticker)
            price = quote.get('c')  # 'c' is current price
            if price and price > 0:
                _PRICE_CACHE[ticker] = float(price)
                # print(f"✓ {ticker} via Finnhub")  # Uncomment for verbose logging
                return float(price)
        except Exception as e:
            # Finnhub doesn't have this ticker (common for mutual funds, some ETFs)
            pass  # Silently fall back to yfinance

    # METHOD 2: Try yfinance fast_info
    try:
        ticker_obj = yf.Ticker(ticker)
        price = ticker_obj.fast_info.get('lastPrice')
        if price and not np.isnan(price):
            _PRICE_CACHE[ticker] = float(price)
            # print(f"✓ {ticker} via yfinance")  # Uncomment for verbose logging
            return float(price)
    except yfinance.exceptions.YFRateLimitError:
        pass  # Continue to next method
    except Exception as e:
        pass  # Continue to next method

    # METHOD 3: Try yahoo_fin as fallback
    try:
        price = si.get_live_price(ticker)
        if price and not np.isnan(price):
            _PRICE_CACHE[ticker] = float(price)
            # print(f"✓ {ticker} via yahoo_fin")  # Uncomment for verbose logging
            return float(price)
    except Exception as e:
        pass  # Continue to next method

    # METHOD 4: Last resort - yfinance history
    try:
        ticker_obj = yf.Ticker(ticker)
        hist = ticker_obj.history(period="1d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            if not np.isnan(price):
                _PRICE_CACHE[ticker] = float(price)
                # print(f"✓ {ticker} via yfinance history")  # Uncomment for verbose logging
                return float(price)
    except Exception as e:
        pass

    print(f"❌ Unable to fetch price for {ticker} from any source")
    return 0


def batch_get_ticker_prices(tickers, delay_between_requests=0.1):
    """
    Fetch prices for multiple tickers with rate limiting protection.

    Args:
        tickers: List of ticker symbols
        delay_between_requests: Seconds to wait between API calls (default 0.1)

    Returns:
        dict: {ticker: price} mapping
    """
    prices = {}
    for i, ticker in enumerate(tickers):
        prices[ticker] = get_ticker_price(ticker)
        # Add delay between requests to avoid rate limiting (skip for last item)
        if i < len(tickers) - 1:
            time.sleep(delay_between_requests)
    return prices


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


def get_ticker_asset_type(ticker, use_cache=True, use_db=True, max_retries=2):
    """
    Get the asset type (quoteType) for a ticker with DB and memory caching.

    Priority order:
    1. Memory cache (fastest)
    2. Database (no API call)
    3. Finnhub API
    4. yfinance API (fallback)

    Args:
        ticker: Stock ticker symbol
        use_cache: Whether to use memory cache (default True)
        use_db: Whether to check/store in database (default True)
        max_retries: Number of retries on rate limit (default 2)

    Returns: Asset type string (e.g., 'EQUITY', 'ETF', 'MUTUALFUND') or None
    """
    # Check memory cache first
    if use_cache and ticker in _ASSET_TYPE_CACHE:
        return _ASSET_TYPE_CACHE[ticker]

    # Check database second (no API call!)
    if use_db:
        db_asset_type = dbh.ticker_metadata.get_ticker_asset_type(ticker)
        if db_asset_type:
            _ASSET_TYPE_CACHE[ticker] = db_asset_type
            return db_asset_type

    # Not in cache or DB - need to fetch from API
    asset_type = None

    # METHOD 1: Try Finnhub (60 calls/min)
    finnhub_client = get_finnhub_client()
    if finnhub_client:
        try:
            profile = finnhub_client.company_profile2(symbol=ticker)
            # Map Finnhub type to yfinance-style type
            finnhub_type = profile.get('finnhubIndustry', '')
            if 'ETF' in finnhub_type.upper():
                asset_type = 'ETF'
            else:
                asset_type = 'EQUITY'  # Default for stocks
        except Exception as e:
            # Finnhub doesn't have this ticker - silently fall back
            pass

    # METHOD 2: Fallback to yfinance if Finnhub failed
    if not asset_type:
        ticker_obj = yf.Ticker(ticker)
        for attempt in range(max_retries + 1):
            try:
                # Try fast_info first (less rate limited)
                try:
                    quote_type = ticker_obj.fast_info.get('quoteType')
                    if quote_type:
                        asset_type = quote_type
                        break
                except (AttributeError, KeyError, TypeError):
                    pass

                # Fallback to full info
                info = ticker_obj.info
                asset_type = info.get("quoteType")
                break

            except yfinance.exceptions.YFRateLimitError:
                if attempt < max_retries:
                    wait_time = (2 ** attempt)
                    print(f"Rate limited fetching asset type for {ticker}, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"Rate limit exceeded getting asset type for {ticker}")
                    break

            except Exception as e:
                print(f"Error fetching asset type for {ticker}: {type(e).__name__}")
                break

    # Cache and save to DB if we got a result
    if asset_type:
        _ASSET_TYPE_CACHE[ticker] = asset_type
        if use_db:
            dbh.ticker_metadata.insert_ticker_metadata(ticker, asset_type)

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
def get_all_active_ticker(live_price=False, delay_between_tickers=0.15):
    """
    Get all active investment positions (net shares > 0 after accounting for sells).

    Aggregates shares by (account_id, ticker) via the DB so fully-sold positions
    are excluded. Previously this iterated raw transactions, which incorrectly
    included SELL rows as non-zero-share positions.

    Args:
        live_price: If True, fetch live prices (slower, may hit rate limits)
        delay_between_tickers: Seconds to wait between API calls when live_price=True (default 0.15)

    Returns:
        List of InvestmentTransaction objects representing net active positions
    """
    ticker_list = []
    today = datetime.date.today().strftime("%Y-%m-%d")

    for account_id in acch.get_account_id_by_type(4):
        for (ticker_sym,) in dbh.investments.get_account_ticker(account_id):
            try:
                net_row = dbh.investments.get_ticker_shares(account_id, ticker_sym)
                net_shares = net_row[2]
            except (IndexError, TypeError):
                continue

            if not net_shares or net_shares <= 0:
                continue

            inv_trans = InvestmentTransaction(
                date=today,
                account_id=account_id,
                category_id=-1,
                ticker=ticker_sym,
                shares=net_shares,
                value=0,
                trans_type="HOLD",
                description=f"Net position: {ticker_sym}",
                live_price=live_price,
            )
            ticker_list.append(inv_trans)

            if live_price:
                time.sleep(delay_between_tickers)

    return ticker_list


def get_account_ticker_shares(account_id, ticker):
    ticker_tuple = dbh.investments.get_ticker_shares(account_id, ticker)
    return ticker_tuple[2]


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
        ticker = InvestmentTransaction("2000/1/1", account_id, -1, transaction[0], transaction[2], -1, -1,
                                       "description")

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


def populate_ticker_metadata_from_investments(delay_between_tickers=1.0):
    """
    One-time setup: Populate ticker_metadata table from existing investment transactions.

    This fetches asset types for all unique tickers in your investment table
    and stores them in the database so future lookups are instant.

    Args:
        delay_between_tickers: Seconds to wait between API calls (default 1.0)
    """
    print("\n" + "="*80)
    print("POPULATING TICKER METADATA FROM INVESTMENT HISTORY")
    print("="*80)

    # Get all unique tickers from investment table
    conn = dbh.investments.sqlite3.connect(dbh.investments.DATABASE_DIRECTORY)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT ticker FROM investment")
    all_tickers = [row[0] for row in cur.fetchall()]
    conn.close()

    print(f"\nFound {len(all_tickers)} unique tickers in investment table")

    # Check which ones are already in metadata table
    existing_tickers = dbh.ticker_metadata.get_all_tickers()
    tickers_to_fetch = [t for t in all_tickers if t not in existing_tickers]

    if not tickers_to_fetch:
        print("✓ All tickers already have metadata!")
        return

    print(f"Need to fetch metadata for {len(tickers_to_fetch)} tickers\n")

    # Fetch and store asset types
    success_count = 0
    fail_count = 0

    for i, ticker in enumerate(tickers_to_fetch, 1):
        print(f"[{i}/{len(tickers_to_fetch)}] Fetching {ticker}...", end=" ")

        asset_type = get_ticker_asset_type(ticker, use_db=False)  # Force API fetch

        if asset_type:
            print(f"✓ {asset_type}")
            success_count += 1
        else:
            print(f"❌ Failed")
            fail_count += 1

        # Rate limiting delay (except for last item)
        if i < len(tickers_to_fetch):
            time.sleep(delay_between_tickers)

    print("\n" + "="*80)
    print(f"RESULTS: {success_count} successful, {fail_count} failed")
    print("="*80 + "\n")
    print("✓ Ticker metadata populated! Future asset allocation will be much faster.")


def update_ticker_asset_type(ticker, asset_type):
    """
    Manually set the asset type for a ticker, updating both the DB and memory cache.
    Use this to correct misclassifications (e.g. BND classified as ETF instead of BOND).
    """
    dbh.ticker_metadata.insert_ticker_metadata(ticker, asset_type)
    _ASSET_TYPE_CACHE[ticker] = asset_type


def print_ticker_metadata_table():
    """Print all ticker metadata in a nice table."""
    data = dbh.ticker_metadata.get_ticker_metadata_table()

    if not data:
        print("No ticker metadata in database yet.")
        print("Run 'Populate ticker metadata' from Investments tab to set up.")
        return

    print(f"\nTicker Metadata ({len(data)} tickers)")
    print("-" * 80)
    clip.print_variable_table(
        ["Ticker", "Asset Type", "Name", "Last Updated"],
        data
    )
