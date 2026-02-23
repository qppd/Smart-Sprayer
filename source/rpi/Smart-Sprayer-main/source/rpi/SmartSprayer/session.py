# session.py
# User session and account data management

import json
import os
from pathlib import Path
from datetime import datetime

class SessionManager:
    """Manages user session and account data"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.account_file = self.data_dir / "account.json"
        
        # Initialize account file if it doesn't exist
        if not self.account_file.exists():
            self._save_account({
                "username": "",
                "phone": "",
                "created_at": "",
                "last_login": ""
            })
    
    def _load_account(self):
        """Load account data from file"""
        try:
            with open(self.account_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "username": "",
                "phone": "",
                "created_at": "",
                "last_login": ""
            }
    
    def _save_account(self, data):
        """Save account data to file"""
        with open(self.account_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def set_user(self, username):
        """Set username"""
        data = self._load_account()
        data["username"] = username
        if not data.get("created_at"):
            data["created_at"] = datetime.now().isoformat()
        self._save_account(data)
        print(f"✓ Username set: {username}")
    
    def get_username(self):
        """Get username"""
        data = self._load_account()
        return data.get("username", "")
    
    def set_phone(self, phone):
        """Set phone number"""
        data = self._load_account()
        data["phone"] = phone
        self._save_account(data)
        print(f"✓ Phone number set: {phone}")
    
    def get_phone(self):
        """Get phone number"""
        data = self._load_account()
        return data.get("phone", "")
    
    def update_last_login(self):
        """Update last login timestamp"""
        data = self._load_account()
        data["last_login"] = datetime.now().isoformat()
        self._save_account(data)
        print(f"✓ Last login updated")
    
    def get_last_login(self):
        """Get last login timestamp"""
        data = self._load_account()
        login_str = data.get("last_login", "")
        if login_str:
            try:
                dt = datetime.fromisoformat(login_str)
                return dt.strftime("%b %d, %Y • %I:%M %p")
            except:
                return "Unknown"
        return "Never"
    
    def get_created_at(self):
        """Get account creation timestamp"""
        data = self._load_account()
        created_str = data.get("created_at", "")
        if created_str:
            try:
                dt = datetime.fromisoformat(created_str)
                return dt.strftime("%b %d, %Y")
            except:
                return "Unknown"
        return "Unknown"
    
    def clear_session(self):
        """Clear session data (logout)"""
        self._save_account({
            "username": "",
            "phone": "",
            "created_at": "",
            "last_login": ""
        })
        print("✓ Session cleared")


# Global session manager instance
_session_manager = None

def get_session_manager():
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

# Convenience functions
def set_user(username):
    """Set username"""
    return get_session_manager().set_user(username)

def get_username():
    """Get username"""
    return get_session_manager().get_username()

def set_phone(phone):
    """Set phone number"""
    return get_session_manager().set_phone(phone)

def get_phone():
    """Get phone number"""
    return get_session_manager().get_phone()

def update_last_login():
    """Update last login timestamp"""
    return get_session_manager().update_last_login()

def get_last_login():
    """Get last login timestamp"""
    return get_session_manager().get_last_login()

def get_created_at():
    """Get account creation date"""
    return get_session_manager().get_created_at()

def clear_session():
    """Clear session data"""
    return get_session_manager().clear_session()