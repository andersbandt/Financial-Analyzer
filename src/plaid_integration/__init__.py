"""
Plaid Integration Module

This module provides Plaid API integration for automated transaction syncing.
It maintains architectural separation from the CSV loading system while sharing
the downstream Transaction/Ledger/Database pipeline.

Modules:
- plaid_service: Core Plaid API client wrapper
- plaid_adapter: Converts Plaid API responses to Transaction objects
- plaid_config: Configuration and credential management
- plaid_security: Encryption utilities for access token storage
"""

from . import plaid_service
from . import plaid_adapter
from . import plaid_config
from . import plaid_security

__all__ = [
    'plaid_service',
    'plaid_adapter',
    'plaid_config',
    'plaid_security',
]
