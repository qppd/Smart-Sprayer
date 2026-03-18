"""
app_settings.py

Small persistent settings store for app-wide toggles.
Currently used for "Manual Mode" to bypass all weather checking.
"""


import json
import os
from typing import Any, Dict


def _settings_file_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # SmartSprayer/
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "app_settings.json")


def _load_settings() -> Dict[str, Any]:
    path = _settings_file_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
            if isinstance(data, dict):
                return data
    except FileNotFoundError:
        pass
    except Exception:
        # If file is corrupt/unreadable, fall back to defaults silently.
        pass
    return {}


def _save_settings(data: Dict[str, Any]) -> None:
    path = _settings_file_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_manual_mode() -> bool:
    """Return True if Manual Mode is enabled."""
    data = _load_settings()
    return bool(data.get("manual_mode", False))


def set_manual_mode(enabled: bool) -> bool:
    """Persist Manual Mode setting. Returns the stored value."""
    data = _load_settings()
    data["manual_mode"] = bool(enabled)
    _save_settings(data)
    return bool(data["manual_mode"])


def get_semaphore_api_key() -> str:
    """Return the Semaphore SMS API key from the secrets file, or empty string if not set."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # SmartSprayer/
    secrets_file = os.path.join(base_dir, "semaphore_secrets.json")
    
    try:
        with open(secrets_file, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
            if isinstance(data, dict):
                return str(data.get("api_key", ""))
    except FileNotFoundError:
        print(f"[WARNING] {secrets_file} not found. Semaphore SMS disabled.")
    except Exception as e:
        print(f"[WARNING] Error reading Semaphore secrets: {e}")
    
    return ""


def set_semaphore_api_key(api_key: str) -> str:
    """Persist the Semaphore SMS API key to the secrets file. Returns the stored value."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # SmartSprayer/
    secrets_file = os.path.join(base_dir, "semaphore_secrets.json")
    
    try:
        data = {"api_key": str(api_key).strip()}
        with open(secrets_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data["api_key"]
    except Exception as e:
        print(f"[ERROR] Failed to save Semaphore API key: {e}")
        return ""
