"""
Plaid Adapter Module

Converts Plaid API responses to Transaction/Statement objects.
This is the bridge between Plaid data and the existing transaction processing pipeline.
"""

from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from statement_types.Transaction import Transaction
from statement_types.Statement import Statement


def plaid_transaction_to_transaction(
    plaid_trans: Dict,
    account_id: int,
    category_id: int = 0
) -> Optional[Transaction]:
    """
    Convert a single Plaid transaction to a Transaction object.

    Args:
        plaid_trans: Dictionary from Plaid API transaction response
        account_id: Our internal account_id to map to
        category_id: Initial category (default: 0 for uncategorized)

    Returns:
        Transaction object or None on error

    Plaid Transaction Structure:
        {
            "transaction_id": "ABC123",
            "account_id": "plaid_acc_xyz",
            "date": "2024-01-15",
            "amount": 45.50,  # Positive for debits, negative for credits
            "name": "TRADER JOES #523",
            "merchant_name": "Trader Joe's",
            "category": ["Food and Drink", "Groceries"],
            ...
        }
    """
    try:
        # Extract required fields
        trans_date = plaid_trans.get('date')
        trans_amount = plaid_trans.get('amount', 0)
        trans_description = plaid_trans.get('name', 'Unknown')
        plaid_transaction_id = plaid_trans.get('transaction_id')
        plaid_account_id = plaid_trans.get('account_id')

        # Plaid uses positive for debits (money out), we use negative
        # Convert: Plaid's positive amount → our negative value
        trans_value = -1 * float(trans_amount)

        # Create note with Plaid metadata
        merchant_name = plaid_trans.get('merchant_name')
        note_parts = []
        if merchant_name and merchant_name != trans_description:
            note_parts.append(f"merchant={merchant_name}")
        note_parts.append("source=plaid")
        note = ";".join(note_parts)

        # Create Transaction object with Plaid fields
        transaction = Transaction(
            date=trans_date,
            account_id=account_id,
            category_id=category_id,
            value=trans_value,
            description=trans_description,
            note=note,
            plaid_transaction_id=plaid_transaction_id,
            plaid_account_id=plaid_account_id,
            transaction_source='PLAID',
            plaid_synced_at=datetime.now().isoformat()
        )

        return transaction

    except Exception as e:
        logger.error(f"Failed to convert Plaid transaction: {e}")
        logger.error(f"Plaid transaction data: {plaid_trans}")
        return None


def plaid_response_to_statement(
    plaid_response: Dict,
    account_id: int,
    year: int,
    month: int
) -> Optional[Statement]:
    """
    Convert Plaid API response to a Statement object (which extends Ledger).

    Args:
        plaid_response: Dictionary from Plaid API (get_transactions or sync_transactions)
        account_id: Our internal account_id
        year: Year for the statement
        month: Month for the statement

    Returns:
        Statement object with transactions loaded, or None on error
    """
    try:
        from statement_types.Ledger import Ledger

        # Extract transactions from response
        # Handle both get_transactions (has 'transactions' key) and sync_transactions (has 'added' key)
        if 'transactions' in plaid_response:
            plaid_transactions = plaid_response['transactions']
        elif 'added' in plaid_response:
            plaid_transactions = plaid_response['added']
        else:
            logger.error("Invalid Plaid response: missing 'transactions' or 'added' key")
            return None

        # Convert each Plaid transaction to our Transaction object
        transactions = []
        for plaid_trans in plaid_transactions:
            transaction = plaid_transaction_to_transaction(plaid_trans, account_id)
            if transaction is not None:
                transactions.append(transaction)

        logger.info(f"Converted {len(transactions)} Plaid transactions to Transaction objects")

        # Create a Statement object (extends Ledger)
        # Statement expects: account_id, year, month
        statement = Statement(account_id, year, month)

        # Manually populate the ledger with transactions
        statement.ledger = transactions

        logger.info(f"Created Statement with {len(statement.ledger)} transactions")
        return statement

    except Exception as e:
        logger.error(f"Failed to create Statement from Plaid response: {e}")
        return None


def deduplicate_by_plaid_id(transactions: List[Transaction]) -> List[Transaction]:
    """
    Remove duplicate transactions based on plaid_transaction_id.

    Args:
        transactions: List of Transaction objects

    Returns:
        Deduplicated list of transactions
    """
    seen_ids = set()
    unique_transactions = []

    for trans in transactions:
        plaid_id = getattr(trans, 'plaid_transaction_id', None)

        if plaid_id is None:
            # Not a Plaid transaction, keep it
            unique_transactions.append(trans)
        elif plaid_id not in seen_ids:
            # First occurrence of this Plaid ID
            seen_ids.add(plaid_id)
            unique_transactions.append(trans)
        else:
            # Duplicate, skip
            logger.debug(f"Skipping duplicate Plaid transaction: {plaid_id}")

    if len(unique_transactions) < len(transactions):
        logger.info(f"Removed {len(transactions) - len(unique_transactions)} duplicate transactions")

    return unique_transactions


def extract_date_range(plaid_transactions: List[Dict]) -> Optional[tuple]:
    """
    Extract the date range from a list of Plaid transactions.

    Args:
        plaid_transactions: List of transaction dictionaries from Plaid

    Returns:
        Tuple of (earliest_date, latest_date) as strings, or None if empty
    """
    if not plaid_transactions:
        return None

    dates = [trans.get('date') for trans in plaid_transactions if trans.get('date')]

    if not dates:
        return None

    earliest = min(dates)
    latest = max(dates)

    return earliest, latest


def group_transactions_by_month(transactions: List[Transaction]) -> Dict[tuple, List[Transaction]]:
    """
    Group transactions by (year, month) for batch processing.

    Args:
        transactions: List of Transaction objects

    Returns:
        Dictionary mapping (year, month) tuples to lists of transactions
    """
    grouped = {}

    for trans in transactions:
        try:
            # Parse date string (format: "YYYY-MM-DD")
            date_parts = trans.date.split('-')
            year = int(date_parts[0])
            month = int(date_parts[1])

            key = (year, month)
            if key not in grouped:
                grouped[key] = []

            grouped[key].append(trans)

        except Exception as e:
            logger.warning(f"Failed to parse date for transaction: {trans.date} - {e}")
            continue

    logger.info(f"Grouped {len(transactions)} transactions into {len(grouped)} month buckets")
    return grouped


def plaid_accounts_to_summary(plaid_accounts: List[Dict]) -> List[Dict]:
    """
    Convert Plaid account objects to simplified summary dictionaries.

    Args:
        plaid_accounts: List of account dictionaries from Plaid API

    Returns:
        List of simplified account summaries
    """
    summaries = []

    for account in plaid_accounts:
        summary = {
            'plaid_account_id': account.get('account_id'),
            'name': account.get('name'),
            'official_name': account.get('official_name'),
            'type': account.get('type'),
            'subtype': account.get('subtype'),
            'mask': account.get('mask'),
            'current_balance': account.get('balances', {}).get('current'),
            'available_balance': account.get('balances', {}).get('available'),
            'currency': account.get('balances', {}).get('iso_currency_code', 'USD')
        }
        summaries.append(summary)

    return summaries
