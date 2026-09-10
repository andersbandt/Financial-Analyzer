"""
@file app_settings.py
@brief Simple persisted app-wide settings, stored as JSON alongside the DB.

Follows the same lazy-load-into-memory / write-through pattern used for
price_cache.json and price_override.json in analysis/investment_helper.py.
"""

import json
import os

# Persistent settings file (gitignored) - survives program restarts
APP_SETTINGS_FILE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_settings.json"))

# Defaults applied when a key is missing from the file (e.g. first run, or a
# setting added after the file already existed)
_DEFAULTS = {
    "ml_categorization_on_load": True,
    # Multi-machine safety checks run at startup (see db/db_guard.py):
    # conflict-copy detection, integrity check, local backup, open-elsewhere lock.
    "db_guard_on_startup": True,
}

_settings = {}
_settings_loaded = False


def _ensure_loaded():
    global _settings_loaded
    if _settings_loaded:
        return
    _settings_loaded = True
    _settings.update(_DEFAULTS)
    if not os.path.exists(APP_SETTINGS_FILE):
        return
    try:
        with open(APP_SETTINGS_FILE, 'r') as f:
            data = json.load(f)
        _settings.update(data)
    except Exception as e:
        print(f"⚠️  Could not load app settings file: {e}")


def _save():
    try:
        with open(APP_SETTINGS_FILE, 'w') as f:
            json.dump(_settings, f, indent=2)
    except Exception as e:
        print(f"⚠️  Could not save app settings file: {e}")


def get_setting(key):
    _ensure_loaded()
    return _settings.get(key, _DEFAULTS.get(key))


def set_setting(key, value):
    _ensure_loaded()
    _settings[key] = value
    _save()


def get_ml_categorization_on_load():
    return get_setting("ml_categorization_on_load")


def set_ml_categorization_on_load(enabled: bool):
    set_setting("ml_categorization_on_load", bool(enabled))


def get_db_guard_on_startup():
    return get_setting("db_guard_on_startup")


def set_db_guard_on_startup(enabled: bool):
    set_setting("db_guard_on_startup", bool(enabled))
