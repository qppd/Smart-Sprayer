# session.py
# User session and account data management

import json
import os
from pathlib import Path
from datetime import datetime

class SessionManager:
    """Manages user session and account data"""

    _DEFAULTS = {
        "username": "sprayer",
        "password": "1234",
        "phone": "",
        "status": "Active",
        "created_at": "",
        "last_login": "",
    }

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.account_file = self.data_dir / "account.json"

        # Initialize / migrate account file
        self._load_account()   # will write defaults if fields are missing

    def _load_account(self):
        """Load account data from file, seeding any missing fields with defaults."""
        try:
            with open(self.account_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        # Seed missing fields with defaults (non-destructive migration)
        changed = False
        for key, default_val in self._DEFAULTS.items():
            if key not in data:
                data[key] = default_val
                changed = True

        if changed:
            self._save_account(data)

        return data
    
    def _save_account(self, data):
        """Save account data to file"""
        with open(self.account_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── Username ──────────────────────────────────────

    def set_user(self, username):
        data = self._load_account()
        data["username"] = username
        if not data.get("created_at"):
            data["created_at"] = datetime.now().isoformat()
        self._save_account(data)
        print(f"✓ Username set: {username}")

    def get_username(self):
        return self._load_account().get("username", "sprayer")

    # ── Password ──────────────────────────────────────

    def get_password(self):
        return self._load_account().get("password", "1234")

    def set_password(self, new_password):
        data = self._load_account()
        data["password"] = new_password
        self._save_account(data)
        print("✓ Password updated")

    def verify_password(self, password):
        """Return True if password matches stored password."""
        return self.get_password() == password

    # ── Phone ─────────────────────────────────────────

    def set_phone(self, phone):
        data = self._load_account()
        data["phone"] = phone
        self._save_account(data)
        print(f"✓ Phone number set: {phone}")

    def get_phone(self):
        return self._load_account().get("phone", "")

    # ── Status ────────────────────────────────────────

    def get_status(self):
        return self._load_account().get("status", "Active")

    def set_status(self, status):
        data = self._load_account()
        data["status"] = status
        self._save_account(data)
        print(f"✓ Status set: {status}")

    # ── Login timestamps ──────────────────────────────

    def update_last_login(self):
        data = self._load_account()
        data["last_login"] = datetime.now().isoformat()
        self._save_account(data)
        print("✓ Last login updated")

    def get_last_login(self):
        login_str = self._load_account().get("last_login", "")
        if login_str:
            try:
                dt = datetime.fromisoformat(login_str)
                return dt.strftime("%b %d, %Y • %I:%M %p")
            except Exception:
                return "Unknown"
        return "Never"

    def get_created_at(self):
        created_str = self._load_account().get("created_at", "")
        if created_str:
            try:
                dt = datetime.fromisoformat(created_str)
                return dt.strftime("%b %d, %Y")
            except Exception:
                return "Unknown"
        return "Unknown"

    # ── Session control ───────────────────────────────

    def clear_session(self):
        """Mark the user as logged out (preserves credentials and profile data)."""
        data = self._load_account()
        data["last_login"] = data.get("last_login", "")   # keep timestamp intact
        self._save_account(data)
        print("✓ Session cleared")
    def clear_session(self):
        """Mark the user as logged out (preserves credentials and profile data)."""
        data = self._load_account()
        data["last_login"] = data.get("last_login", "")   # keep timestamp intact
        self._save_account(data)
        print("✓ Session cleared")


# ─────────────────────────────────────────────────────────────
# Global session manager instance
# ─────────────────────────────────────────────────────────────
_session_manager = None

def get_session_manager():
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

# Convenience functions
def set_user(username):        return get_session_manager().set_user(username)
def get_username():            return get_session_manager().get_username()

def get_password():            return get_session_manager().get_password()
def set_password(new_pass):    return get_session_manager().set_password(new_pass)
def verify_password(password): return get_session_manager().verify_password(password)

def set_phone(phone):          return get_session_manager().set_phone(phone)
def get_phone():               return get_session_manager().get_phone()

def get_status():              return get_session_manager().get_status()
def set_status(status):        return get_session_manager().set_status(status)

def update_last_login():       return get_session_manager().update_last_login()
def get_last_login():          return get_session_manager().get_last_login()
def get_created_at():          return get_session_manager().get_created_at()

def clear_session():           return get_session_manager().clear_session()