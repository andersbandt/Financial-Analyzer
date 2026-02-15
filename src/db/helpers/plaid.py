"""
Plaid Database Helper

CRUD operations for Plaid-specific data in the database.
"""

import sqlite3
import datetime
from typing import Optional, List, Dict, Tuple
from loguru import logger
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from plaid_integration import plaid_security
import db


def insert_access_token(
    account_id: int,
    access_token: str,
    plaid_account_id: str,
    plaid_institution_id: str
) -> bool:
    """
    Store encrypted access token for a linked account.

    Args:
        account_id: Our internal account_id
        access_token: Plaid access token (will be encrypted)
        plaid_account_id: Plaid's account identifier
        plaid_institution_id: Plaid's institution identifier

    Returns:
        True if successful, False otherwise
    """
    try:
        # Encrypt the access token
        encrypted_token = plaid_security.encrypt_token(access_token)

        with sqlite3.connect(db.DATABASE_DIRECTORY) as conn:
            cursor = conn.cursor()

            # Update account table with Plaid information
            cursor.execute("""
                UPDATE account
                SET plaid_account_id = ?,
                    plaid_institution_id = ?,
                    access_token_encrypted = ?,
                    access_token_synced = ?,
                    is_plaid_linked = 1
                WHERE account_id = ?
            """, (
                plaid_account_id,
                plaid_institution_id,
                encrypted_token,
                datetime.datetime.now(),
                account_id
            ))

            conn.commit()

        logger.info(f"Stored access token for account {account_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to insert access token: {e}")
        return False


def get_access_token(account_id: int) -> Optional[str]:
    """
    Retrieve and decrypt access token for an account.

    Args:
        account_id: Our internal account_id

    Returns:
        Decrypted access token string, or None if not found
    """
    try:
        with sqlite3.connect(db.DATABASE_DIRECTORY) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT access_token_encrypted
                FROM account
                WHERE account_id = ? AND is_plaid_linked = 1
            """, (account_id,))

            result = cursor.fetchone()

        if result is None or result[0] is None:
            logger.warning(f"No access token found for account {account_id}")
            return None

        # Decrypt the token
        encrypted_token = result[0]
        access_token = plaid_security.decrypt_token(encrypted_token)

        logger.debug(f"Retrieved access token for account {account_id}")
        return access_token

    except Exception as e:
        logger.error(f"Failed to get access token: {e}")
        return None


def update_sync_state(
    account_id: int,
    last_sync: datetime.datetime,
    cursor: Optional[str] = None,
    error_msg: Optional[str] = None,
    is_syncing: bool = False
) -> bool:
    """
    Update sync state for a Plaid-linked account.

    Args:
        account_id: Our internal account_id
        last_sync: Timestamp of last sync attempt
        cursor: Plaid cursor for incremental updates
        error_msg: Error message if sync failed
        is_syncing: Whether sync is currently in progress

    Returns:
        True if successful, False otherwise
    """
    try:
        with sqlite3.connect(db.DATABASE_DIRECTORY) as conn:
            cursor_db = conn.cursor()

            # Check if record exists
            cursor_db.execute("""
                SELECT id FROM plaid_sync_state WHERE account_id = ?
            """, (account_id,))

            exists = cursor_db.fetchone() is not None

            if exists:
                # Update existing record
                if error_msg is None:
                    # Successful sync
                    cursor_db.execute("""
                        UPDATE plaid_sync_state
                        SET last_successful_sync = ?,
                            last_attempted_sync = ?,
                            cursor = ?,
                            sync_count = sync_count + 1,
                            last_error_message = NULL,
                            is_syncing = ?
                        WHERE account_id = ?
                    """, (last_sync, last_sync, cursor, is_syncing, account_id))
                else:
                    # Failed sync
                    cursor_db.execute("""
                        UPDATE plaid_sync_state
                        SET last_attempted_sync = ?,
                            last_error_message = ?,
                            is_syncing = ?
                        WHERE account_id = ?
                    """, (last_sync, error_msg, is_syncing, account_id))
            else:
                # Insert new record
                cursor_db.execute("""
                    INSERT INTO plaid_sync_state
                    (account_id, last_successful_sync, last_attempted_sync,
                     cursor, sync_count, last_error_message, is_syncing)
                    VALUES (?, ?, ?, ?, 1, ?, ?)
                """, (account_id, last_sync if error_msg is None else None,
                      last_sync, cursor, error_msg, is_syncing))

            conn.commit()

        logger.info(f"Updated sync state for account {account_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to update sync state: {e}")
        return False


def get_sync_state(account_id: int) -> Optional[Dict]:
    """
    Get sync state for a Plaid-linked account.

    Args:
        account_id: Our internal account_id

    Returns:
        Dictionary with sync state info, or None if not found
    """
    try:
        with sqlite3.connect(db.DATABASE_DIRECTORY) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT last_successful_sync, last_attempted_sync,
                       last_error_message, sync_count, cursor, is_syncing
                FROM plaid_sync_state
                WHERE account_id = ?
            """, (account_id,))

            result = cursor.fetchone()

        if result is None:
            return None

        state = {
            'last_successful_sync': result[0],
            'last_attempted_sync': result[1],
            'last_error_message': result[2],
            'sync_count': result[3],
            'cursor': result[4],
            'is_syncing': bool(result[5])
        }

        return state

    except Exception as e:
        logger.error(f"Failed to get sync state: {e}")
        return None


def check_transaction_by_plaid_id(plaid_transaction_id: str) -> bool:
    """
    Check if a transaction with this Plaid ID already exists.

    Args:
        plaid_transaction_id: Plaid transaction identifier

    Returns:
        True if exists, False otherwise
    """
    try:
        with sqlite3.connect(db.DATABASE_DIRECTORY) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM transactions
                WHERE plaid_transaction_id = ?
            """, (plaid_transaction_id,))

            count = cursor.fetchone()[0]

        return count > 0

    except Exception as e:
        logger.error(f"Failed to check transaction: {e}")
        return False


def get_plaid_linked_accounts() -> List[Dict]:
    """
    Get all Plaid-linked accounts with their metadata.

    Returns:
        List of dictionaries with account information
    """
    try:
        with sqlite3.connect(db.DATABASE_DIRECTORY) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT a.account_id, a.name, a.institution_name,
                       a.plaid_account_id, a.plaid_institution_id,
                       a.access_token_synced,
                       COUNT(t.id) as transaction_count
                FROM account a
                LEFT JOIN transactions t ON a.account_id = t.account_id
                    AND t.transaction_source = 'PLAID'
                WHERE a.is_plaid_linked = 1
                GROUP BY a.account_id
            """)

            results = cursor.fetchall()

        accounts = []
        for row in results:
            # Get sync state
            sync_state = get_sync_state(row[0])

            account = {
                'account_id': row[0],
                'name': row[1],
                'institution_name': row[2],
                'plaid_account_id': row[3],
                'plaid_institution_id': row[4],
                'last_synced': row[5],
                'transaction_count': row[6],
                'sync_state': sync_state
            }
            accounts.append(account)

        logger.info(f"Retrieved {len(accounts)} Plaid-linked accounts")
        return accounts

    except Exception as e:
        logger.error(f"Failed to get Plaid-linked accounts: {e}")
        return []


def revoke_access_token(account_id: int) -> bool:
    """
    Remove Plaid link from an account.

    Args:
        account_id: Our internal account_id

    Returns:
        True if successful, False otherwise
    """
    try:
        with sqlite3.connect(db.DATABASE_DIRECTORY) as conn:
            cursor = conn.cursor()

            # Update account table
            cursor.execute("""
                UPDATE account
                SET plaid_account_id = NULL,
                    plaid_institution_id = NULL,
                    access_token_encrypted = NULL,
                    access_token_synced = NULL,
                    is_plaid_linked = 0
                WHERE account_id = ?
            """, (account_id,))

            # Delete sync state
            cursor.execute("""
                DELETE FROM plaid_sync_state
                WHERE account_id = ?
            """, (account_id,))

            conn.commit()

        logger.info(f"Revoked access token for account {account_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to revoke access token: {e}")
        return False


def get_plaid_transaction_count(account_id: int) -> int:
    """
    Get count of Plaid transactions for an account.

    Args:
        account_id: Our internal account_id

    Returns:
        Number of Plaid transactions
    """
    try:
        with sqlite3.connect(db.DATABASE_DIRECTORY) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM transactions
                WHERE account_id = ? AND transaction_source = 'PLAID'
            """, (account_id,))

            count = cursor.fetchone()[0]

        return count

    except Exception as e:
        logger.error(f"Failed to get transaction count: {e}")
        return 0
