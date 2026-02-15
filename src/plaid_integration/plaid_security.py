"""
Plaid Security Module

Handles encryption/decryption of Plaid access tokens before database storage.
Uses Fernet (symmetric encryption) from the cryptography library.
"""

import os
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Optional
from loguru import logger


# Encryption key storage
KEY_DIR = Path.home() / ".financial-analyzer"
KEY_FILE = KEY_DIR / "plaid_encryption.key"


def ensure_key_directory():
    """Create key directory if it doesn't exist"""
    if not KEY_DIR.exists():
        KEY_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created key directory at {KEY_DIR}")


def generate_encryption_key() -> bytes:
    """
    Generate a new encryption key for Fernet.

    Returns:
        Encryption key as bytes
    """
    key = Fernet.generate_key()
    logger.info("Generated new encryption key")
    return key


def save_encryption_key(key: bytes) -> bool:
    """
    Save encryption key to file.

    Args:
        key: Encryption key bytes

    Returns:
        True if saved successfully, False otherwise
    """
    ensure_key_directory()

    try:
        with open(KEY_FILE, 'wb') as f:
            f.write(key)

        # Set restrictive permissions (owner read/write only)
        os.chmod(KEY_FILE, 0o600)

        logger.info(f"Saved encryption key to {KEY_FILE}")
        return True

    except Exception as e:
        logger.error(f"Failed to save encryption key: {e}")
        return False


def load_encryption_key() -> Optional[bytes]:
    """
    Load encryption key from file.

    Returns:
        Encryption key as bytes, or None if file doesn't exist
    """
    if not KEY_FILE.exists():
        logger.warning(f"Encryption key file not found at {KEY_FILE}")
        return None

    try:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
        logger.debug("Loaded encryption key")
        return key

    except Exception as e:
        logger.error(f"Failed to load encryption key: {e}")
        return None


def get_or_create_key() -> bytes:
    """
    Get existing encryption key or create a new one.

    Returns:
        Encryption key as bytes
    """
    key = load_encryption_key()

    if key is None:
        logger.info("No encryption key found, generating new one")
        key = generate_encryption_key()
        if not save_encryption_key(key):
            raise RuntimeError("Failed to save encryption key")

    return key


def encrypt_token(token: str) -> bytes:
    """
    Encrypt a Plaid access token.

    Args:
        token: Plain text access token

    Returns:
        Encrypted token as bytes

    Raises:
        RuntimeError: If encryption fails
    """
    try:
        key = get_or_create_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(token.encode())
        logger.debug("Successfully encrypted access token")
        return encrypted

    except Exception as e:
        logger.error(f"Failed to encrypt token: {e}")
        raise RuntimeError(f"Encryption failed: {e}")


def decrypt_token(encrypted_token: bytes) -> str:
    """
    Decrypt a Plaid access token.

    Args:
        encrypted_token: Encrypted token as bytes

    Returns:
        Plain text access token

    Raises:
        RuntimeError: If decryption fails
    """
    try:
        key = get_or_create_key()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_token)
        logger.debug("Successfully decrypted access token")
        return decrypted.decode()

    except Exception as e:
        logger.error(f"Failed to decrypt token: {e}")
        raise RuntimeError(f"Decryption failed: {e}")


def delete_encryption_key() -> bool:
    """
    Delete the encryption key file.

    WARNING: This will make all encrypted tokens unrecoverable!

    Returns:
        True if deleted successfully or doesn't exist, False on error
    """
    if not KEY_FILE.exists():
        logger.info("Encryption key doesn't exist, nothing to delete")
        return True

    try:
        KEY_FILE.unlink()
        logger.warning(f"Deleted encryption key at {KEY_FILE} - all encrypted tokens are now unrecoverable!")
        return True

    except Exception as e:
        logger.error(f"Failed to delete encryption key: {e}")
        return False
