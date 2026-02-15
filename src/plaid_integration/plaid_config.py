"""
Plaid Configuration Management

Handles loading and saving Plaid API credentials from configuration file.
Config file stored in ~/.financial-analyzer/plaid_config.json (NOT in Git).
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from loguru import logger


# Configuration directory and file paths
CONFIG_DIR = Path.home() / ".financial-analyzer"
CONFIG_FILE = CONFIG_DIR / "plaid_config.json"


def ensure_config_directory():
    """Create configuration directory if it doesn't exist"""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created configuration directory at {CONFIG_DIR}")


def load_credentials() -> Optional[Dict[str, str]]:
    """
    Load Plaid API credentials from config file.

    Returns:
        Dictionary with keys: client_id, secret, environment
        Returns None if config file doesn't exist or is invalid
    """
    if not CONFIG_FILE.exists():
        logger.warning(f"Plaid config file not found at {CONFIG_FILE}")
        return None

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        # Validate required fields
        required_fields = ['client_id', 'secret', 'environment']
        if not all(field in config for field in required_fields):
            logger.error(f"Invalid config file: missing required fields {required_fields}")
            return None

        # Validate environment value
        if config['environment'] not in ['development', 'sandbox', 'production']:
            logger.error(f"Invalid environment: {config['environment']}")
            return None

        logger.info(f"Loaded Plaid credentials (environment: {config['environment']})")
        return config

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse config file: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return None


def save_credentials(client_id: str, secret: str, environment: str) -> bool:
    """
    Save Plaid API credentials to config file.

    Args:
        client_id: Plaid client ID
        secret: Plaid secret key
        environment: 'development', 'sandbox', or 'production'

    Returns:
        True if saved successfully, False otherwise
    """
    # Validate environment
    if environment not in ['development', 'sandbox', 'production']:
        logger.error(f"Invalid environment: {environment}. Must be 'development', 'sandbox', or 'production'")
        return False

    # Ensure directory exists
    ensure_config_directory()

    # Create config dictionary
    config = {
        'client_id': client_id,
        'secret': secret,
        'environment': environment
    }

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        # Set restrictive permissions (owner read/write only)
        os.chmod(CONFIG_FILE, 0o600)

        logger.info(f"Saved Plaid credentials to {CONFIG_FILE}")
        return True

    except Exception as e:
        logger.error(f"Failed to save credentials: {e}")
        return False


def get_config_path() -> Path:
    """Return path to config file (for display purposes)"""
    return CONFIG_FILE


def config_exists() -> bool:
    """Check if config file exists"""
    return CONFIG_FILE.exists()


def delete_credentials() -> bool:
    """
    Delete the credentials file.

    Returns:
        True if deleted successfully or file doesn't exist, False on error
    """
    if not CONFIG_FILE.exists():
        logger.info("Config file doesn't exist, nothing to delete")
        return True

    try:
        CONFIG_FILE.unlink()
        logger.info(f"Deleted credentials file at {CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete credentials: {e}")
        return False
