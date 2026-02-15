"""
Plaid Service Module

Core Plaid API client wrapper. Handles all interactions with Plaid API.
"""

from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.item_remove_request import ItemRemoveRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid import ApiClient, Configuration
from typing import Dict, Optional, List, Tuple
from datetime import datetime, date
from loguru import logger


class PlaidService:
    """
    Plaid API client wrapper.

    Handles authentication and API calls to Plaid services.
    """

    def __init__(self, client_id: str, secret: str, environment: str = 'development'):
        """
        Initialize Plaid client.

        Args:
            client_id: Plaid client ID
            secret: Plaid secret key
            environment: 'development', 'sandbox', or 'production'
        """
        self.client_id = client_id
        self.secret = secret
        self.environment = environment

        # Map environment string to Plaid host
        env_map = {
            'sandbox': 'https://sandbox.plaid.com',
            'development': 'https://development.plaid.com',
            'production': 'https://production.plaid.com'
        }

        # Configure Plaid client
        configuration = Configuration(
            host=env_map.get(environment, 'https://development.plaid.com'),
            api_key={
                'clientId': client_id,
                'secret': secret,
            }
        )

        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

        logger.info(f"Initialized Plaid client (environment: {environment})")

    def create_link_token(self, user_id: str, client_name: str = "Financial Analyzer") -> Optional[str]:
        """
        Create a Link token for Plaid Link flow.

        Args:
            user_id: Unique identifier for the user (can be any string)
            client_name: Name displayed in Plaid Link

        Returns:
            Link token string, or None on error
        """
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id
                ),
                client_name=client_name,
                products=[Products("transactions")],
                country_codes=[CountryCode("US")],
                language='en'
            )

            response = self.client.link_token_create(request)
            link_token = response['link_token']

            logger.info(f"Created Link token for user {user_id}")
            return link_token

        except Exception as e:
            logger.error(f"Failed to create Link token: {e}")
            return None

    def exchange_public_token(self, public_token: str) -> Optional[Tuple[str, str]]:
        """
        Exchange public token for access token.

        Args:
            public_token: Public token from Plaid Link

        Returns:
            Tuple of (access_token, item_id) or None on error
        """
        try:
            request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )

            response = self.client.item_public_token_exchange(request)
            access_token = response['access_token']
            item_id = response['item_id']

            logger.info(f"Exchanged public token for access token (item_id: {item_id})")
            return access_token, item_id

        except Exception as e:
            logger.error(f"Failed to exchange public token: {e}")
            return None

    def get_accounts(self, access_token: str) -> Optional[List[Dict]]:
        """
        Get account information for a linked item.

        Args:
            access_token: Plaid access token

        Returns:
            List of account dictionaries, or None on error
        """
        try:
            request = AccountsGetRequest(
                access_token=access_token
            )

            response = self.client.accounts_get(request)
            accounts = response['accounts']

            logger.info(f"Retrieved {len(accounts)} accounts")
            return [account.to_dict() for account in accounts]

        except Exception as e:
            logger.error(f"Failed to get accounts: {e}")
            return None

    def get_transactions(self, access_token: str, start_date: date, end_date: date) -> Optional[Dict]:
        """
        Get transactions for a date range (legacy method).

        Args:
            access_token: Plaid access token
            start_date: Start date for transactions
            end_date: End date for transactions

        Returns:
            Dictionary with 'transactions' and 'accounts' keys, or None on error
        """
        try:
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date
            )

            response = self.client.transactions_get(request)

            result = {
                'transactions': [t.to_dict() for t in response['transactions']],
                'accounts': [a.to_dict() for a in response['accounts']],
                'total_transactions': response['total_transactions']
            }

            logger.info(f"Retrieved {len(result['transactions'])} transactions")
            return result

        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            return None

    def sync_transactions(self, access_token: str, cursor: Optional[str] = None) -> Optional[Dict]:
        """
        Sync transactions using Transactions Sync API (recommended method).

        Args:
            access_token: Plaid access token
            cursor: Cursor for pagination/incremental updates (None for initial sync)

        Returns:
            Dictionary with 'added', 'modified', 'removed', 'next_cursor', 'has_more'
            or None on error
        """
        try:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor
            )

            response = self.client.transactions_sync(request)

            result = {
                'added': [t.to_dict() for t in response['added']],
                'modified': [t.to_dict() for t in response['modified']],
                'removed': [t.to_dict() for t in response['removed']],
                'next_cursor': response['next_cursor'],
                'has_more': response['has_more']
            }

            logger.info(f"Synced transactions: {len(result['added'])} added, "
                       f"{len(result['modified'])} modified, {len(result['removed'])} removed")
            return result

        except Exception as e:
            logger.error(f"Failed to sync transactions: {e}")
            return None

    def get_balances(self, access_token: str) -> Optional[Dict]:
        """
        Get current account balances.

        Args:
            access_token: Plaid access token

        Returns:
            Dictionary mapping account_id to balance info, or None on error
        """
        try:
            request = AccountsGetRequest(
                access_token=access_token
            )

            response = self.client.accounts_get(request)
            accounts = response['accounts']

            balances = {}
            for account in accounts:
                account_dict = account.to_dict()
                balances[account_dict['account_id']] = {
                    'current': account_dict['balances']['current'],
                    'available': account_dict['balances'].get('available'),
                    'currency': account_dict['balances']['iso_currency_code']
                }

            logger.info(f"Retrieved balances for {len(balances)} accounts")
            return balances

        except Exception as e:
            logger.error(f"Failed to get balances: {e}")
            return None

    def revoke_access(self, access_token: str) -> bool:
        """
        Revoke access token and unlink item.

        Args:
            access_token: Plaid access token

        Returns:
            True if successful, False otherwise
        """
        try:
            request = ItemRemoveRequest(
                access_token=access_token
            )

            self.client.item_remove(request)
            logger.info("Successfully revoked access token")
            return True

        except Exception as e:
            logger.error(f"Failed to revoke access: {e}")
            return False


def initialize_client(client_id: str, secret: str, environment: str = 'development') -> Optional[PlaidService]:
    """
    Factory function to create and test Plaid client.

    Args:
        client_id: Plaid client ID
        secret: Plaid secret key
        environment: 'development', 'sandbox', or 'production'

    Returns:
        PlaidService instance or None on error
    """
    try:
        service = PlaidService(client_id, secret, environment)
        logger.info("Successfully initialized Plaid service")
        return service

    except Exception as e:
        logger.error(f"Failed to initialize Plaid service: {e}")
        return None
