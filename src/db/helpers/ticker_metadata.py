"""
@file ticker_metadata.py
@brief SQL interface file for the 'ticker_metadata' table

Stores ticker information (asset type, name) to avoid repeated API calls
"""

# import needed modules
import sqlite3
from datetime import datetime

# import user definitions
from db import DATABASE_DIRECTORY


def get_ticker_metadata(ticker):
    """
    Get all metadata for a ticker.

    Returns: tuple (ticker, asset_type, name, last_updated) or None
    """
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM ticker_metadata WHERE ticker=?",
            (ticker,),
        )
        data = cur.fetchone()
    return data


def get_ticker_asset_type(ticker):
    """
    Get just the asset type for a ticker.

    Returns: asset_type string or None
    """
    data = get_ticker_metadata(ticker)
    if data:
        return data[1]  # asset_type is second column
    return None


def insert_ticker_metadata(ticker, asset_type, name=None):
    """
    Insert or update ticker metadata.

    Args:
        ticker: Ticker symbol
        asset_type: Asset type (EQUITY, ETF, MUTUALFUND, etc.)
        name: Optional company/fund name
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO ticker_metadata
               (ticker, asset_type, name, last_updated)
               VALUES (?, ?, ?, ?)""",
            (ticker, asset_type, name, now),
        )
        conn.commit()


def update_ticker_asset_type(ticker, asset_type):
    """Update just the asset type for an existing ticker."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE ticker_metadata
               SET asset_type=?, last_updated=?
               WHERE ticker=?""",
            (asset_type, now, ticker),
        )
        conn.commit()


def get_all_tickers():
    """Get all tickers in the database."""
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT ticker FROM ticker_metadata")
        data = cur.fetchall()
    return [row[0] for row in data]


def delete_ticker_metadata(ticker):
    """Delete metadata for a ticker."""
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM ticker_metadata WHERE ticker=?", (ticker,))
        conn.commit()


def get_ticker_metadata_table():
    """Get all ticker metadata as a list of tuples."""
    with sqlite3.connect(DATABASE_DIRECTORY) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM ticker_metadata ORDER BY ticker")
        data = cur.fetchall()
    return data
