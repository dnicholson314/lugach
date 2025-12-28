import os
import json
import platform
from typing import cast
import dotenv as dv
from cryptography.fernet import Fernet
from pathlib import Path
from warnings import warn

from playwright.sync_api import StorageState

try:
    import keyring
    import keyring.errors
except ImportError:
    keyring = None

ROOT_DIR = Path.home() / ".lugach"
ROOT_DIR.mkdir(parents=True, exist_ok=True)

ENV_PATH = ROOT_DIR / ".env"

KEYRING_SERVICE_NAME = "lugach"
ENCRYPTION_KEY_USERNAME = "LUGACH_ENCRYPTION_KEY"
FALLBACK_KEY_FILE = ROOT_DIR / ".encryption_key"


def _running_in_wsl() -> bool:
    """Detect if running inside Windows Subsystem for Linux."""
    return "microsoft" in platform.uname().release.lower()


def _get_or_create_encryption_key() -> bytes:
    """Get encryption key from keyring or fallback to file-based storage."""
    # Primary: use keyring if available and usable
    if keyring and not _running_in_wsl():
        try:
            key_str = keyring.get_password(
                KEYRING_SERVICE_NAME, ENCRYPTION_KEY_USERNAME
            )
            if key_str:
                return key_str.encode("utf-8")

            key = Fernet.generate_key()
            keyring.set_password(
                KEYRING_SERVICE_NAME, ENCRYPTION_KEY_USERNAME, key.decode("utf-8")
            )
            return key
        except keyring.errors.KeyringError:
            pass  # Fall back if no backend is available

    warn(
        "Warning: falling back to file-based storage for authentication credentials. "
        "This is inherently insecure, so proceed with caution.",
        UserWarning,
    )

    # Fallback: secure file
    if FALLBACK_KEY_FILE.exists():
        return FALLBACK_KEY_FILE.read_bytes()

    key = Fernet.generate_key()
    FALLBACK_KEY_FILE.write_bytes(key)
    try:
        FALLBACK_KEY_FILE.chmod(0o600)
    except PermissionError:
        pass  # Some filesystems (e.g. Windows mounts) may not support chmod
    return key


def _fernet() -> Fernet:
    return Fernet(_get_or_create_encryption_key())


def _encrypt_token(value: str) -> str:
    token = _fernet().encrypt(value.encode("utf-8")).decode("utf-8")
    return token


def _decrypt_token(token: str) -> str:
    value = _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    return value


def update_env_file(**kwargs: str) -> None:
    ENV_PATH.touch()
    for key, value in kwargs.items():
        token = _encrypt_token(value)
        dv.set_key(dotenv_path=ENV_PATH, key_to_set=key, value_to_set=token)


def get_secret(key: str) -> str:
    ENV_PATH.touch()
    dv.load_dotenv(dotenv_path=ENV_PATH, override=True)

    token = os.getenv(key)
    if not token:
        raise NameError(f"Failed to load key ({key}) from .env file")

    value = _decrypt_token(token)

    return value


def get_credentials(id: str) -> tuple[str, str]:
    """
    Retrieve stored credentials (username/password) for a given id
    from the encrypted .env file.
    Returns a (username, password) tuple or raises an error if not found.
    """
    ENV_PATH.touch()
    dv.load_dotenv(dotenv_path=ENV_PATH, override=True)

    username_token = os.getenv(f"{id}_USERNAME")
    password_token = os.getenv(f"{id}_PASSWORD")

    if not username_token or not password_token:
        raise NameError(f"Failed to load credentials for id {id}")

    username = _decrypt_token(username_token)
    password = _decrypt_token(password_token)
    return username, password


def set_credentials(id: str, username: str, password: str) -> None:
    """
    Store credentials (username/password) for a given id
    in the encrypted .env file.
    """
    ENV_PATH.touch()

    update_env_file(
        **{
            f"{id}_USERNAME": username,
            f"{id}_PASSWORD": password,
        }
    )


def save_encrypted_storage_state(name: str, storage_state: StorageState) -> None:
    """
    Encrypts and stores a Playwright storage state under a given name.
    """
    state_json = json.dumps(storage_state)
    encrypted_state = _encrypt_token(state_json)
    storage_file = ROOT_DIR / f"{name}.state"
    storage_file.write_text(encrypted_state, encoding="utf-8")


def load_encrypted_storage_state(name: str) -> StorageState:
    """
    Loads and decrypts a Playwright storage state by name.
    Returns the storage state as a dictionary.
    """
    storage_file = ROOT_DIR / f"{name}.state"
    if not storage_file.exists():
        raise FileNotFoundError(f"No storage state found for '{name}'")

    encrypted_state = storage_file.read_text(encoding="utf-8")
    state_json = _decrypt_token(encrypted_state)
    return cast(StorageState, json.loads(state_json))
