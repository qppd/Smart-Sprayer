# data_store.py
# Data persistence for schedules and spray history with Firebase sync

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

try:
    from core.firebase_service import get_firebase_service
    FIREBASE_ENABLED = True
except ImportError:
    FIREBASE_ENABLED = False
    print("Warning: Firebase service not available")

class DataStore:
    """Manages persistent storage of schedules and history with Firebase sync"""
    
    def __init__(self, data_dir="data", enable_firebase=True):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.schedules_file = self.data_dir / "schedules.json"
        self.history_file = self.data_dir / "history.json"
        
        # Initialize files if they don't exist
        self._init_files()
        
        # Firebase integration
        self.firebase = None
        if FIREBASE_ENABLED and enable_firebase:
            self.firebase = get_firebase_service()
            if self.firebase.connected:
                print("DataStore: Firebase sync enabled")
    
    def _init_files(self):
        """Initialize data files"""
        if not self.schedules_file.exists():
            self._save_json(self.schedules_file, [])
        
        if not self.history_file.exists():
            self._save_json(self.history_file, [])
    
    def _load_json(self, file_path):
        """Load JSON from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_json(self, file_path, data):
        """Save data to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Schedule Management
    def get_all_schedules(self) -> List[Dict]:
        """Get all schedules"""
        return self._load_json(self.schedules_file)
    
    def add_schedule(self, schedule: Dict) -> Dict:
        """Add new schedule"""
        schedules = self.get_all_schedules()
        
        # Generate ID if not present
        if 'id' not in schedule:
            schedule['id'] = self._generate_schedule_id(schedules)
        
        # Add metadata
        schedule['created_at'] = datetime.now().isoformat()
        schedule['reschedule_count'] = schedule.get('reschedule_count', 0)
        schedule['status'] = schedule.get('status', 'scheduled')
        
        schedules.append(schedule)
        self._save_json(self.schedules_file, schedules)
        
        # Sync to Firebase
        if self.firebase and self.firebase.connected:
            self.firebase.upload_schedule(schedule)
        
        return schedule
    
    def update_schedule(self, schedule_id: str, updates: Dict) -> Optional[Dict]:
        """Update existing schedule"""
        schedules = self.get_all_schedules()
        
        for i, sched in enumerate(schedules):
            if sched['id'] == schedule_id:
                schedules[i].update(updates)
                schedules[i]['updated_at'] = datetime.now().isoformat()
                self._save_json(self.schedules_file, schedules)
                
                # Sync to Firebase
                if self.firebase and self.firebase.connected:
                    self.firebase.upload_schedule(schedules[i])
                
                return schedules[i]
        
        return None
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete schedule"""
        schedules = self.get_all_schedules()
        original_count = len(schedules)
        
        schedules = [s for s in schedules if s['id'] != schedule_id]
        
        if len(schedules) < original_count:
            self._save_json(self.schedules_file, schedules)
            
            # Sync to Firebase
            if self.firebase and self.firebase.connected:
                self.firebase.delete_schedule(schedule_id)
            
            return True
        
        return False
    
    def get_schedule_by_id(self, schedule_id: str) -> Optional[Dict]:
        """Get schedule by ID"""
        schedules = self.get_all_schedules()
        
        for sched in schedules:
            if sched['id'] == schedule_id:
                return sched
        
        return None
    
    def get_active_schedules(self) -> List[Dict]:
        """Get all active (not completed/cancelled) schedules"""
        schedules = self.get_all_schedules()
        return [s for s in schedules if s['status'] in ['scheduled', 'rescheduled']]
    
    def clear_all_schedules(self):
        """Clear all schedules"""
        self._save_json(self.schedules_file, [])
    
    # History Management
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get spray history"""
        history = self._load_json(self.history_file)
        
        if limit:
            return history[-limit:]
        return history
    
    def add_to_history(self, spray_data: Dict):
        """Add completed spray to history"""
        history = self.get_history()
        
        spray_data['completed_at'] = datetime.now().isoformat()
        if 'id' not in spray_data:
            spray_data['id'] = f"HIST_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        history.append(spray_data)
        self._save_json(self.history_file, history)
        
        # Sync to Firebase
        if self.firebase and self.firebase.connected:
            self.firebase.upload_history_entry(spray_data)
    
    def clear_history(self):
        """Clear history"""
        self._save_json(self.history_file, [])
    
    # Helper Methods
    def _generate_schedule_id(self, existing_schedules: List[Dict]) -> str:
        """Generate unique schedule ID"""
        if not existing_schedules:
            return "SCH_001"
        
        # Extract numeric part of last ID
        last_id = existing_schedules[-1].get('id', 'SCH_000')
        try:
            num = int(last_id.split('_')[1]) + 1
            return f"SCH_{num:03d}"
        except (IndexError, ValueError):
            return f"SCH_{len(existing_schedules) + 1:03d}"
    
    def get_schedules_by_date(self, date_str: str) -> List[Dict]:
        """Get all schedules for a specific date"""
        schedules = self.get_active_schedules()
        return [s for s in schedules if s['date'] == date_str]
    
    def export_data(self, export_path: str):
        """Export all data to a single JSON file"""
        data = {
            'schedules': self.get_all_schedules(),
            'history': self.get_history(),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def sync_all_to_firebase(self):
        """Manually sync all local data to Firebase"""
        if not self.firebase or not self.firebase.connected:
            print("Firebase not available for sync")
            return False
        
        try:
            # Sync all schedules
            schedules = self.get_all_schedules()
            self.firebase.upload_schedules(schedules)
            
            # Sync all history
            history = self.get_history()
            self.firebase.upload_history(history)
            
            print("All data synced to Firebase successfully")
            return True
        except Exception as e:
            print(f"Error syncing to Firebase: {e}")
            return False


# Global data store instance
_data_store_instance = None

def get_data_store():
    """Get global data store instance"""
    global _data_store_instance
    if _data_store_instance is None:
        _data_store_instance = DataStore()
    return _data_store_instance
# Convenience functions for recipients management
def get_recipients():
    """Get all SMS recipients"""
    store = get_data_store()
    recipients_file = store.data_dir / "recipients.json"
    
    if not recipients_file.exists():
        store._save_json(recipients_file, [])
        return []
    
    recipients = store._load_json(recipients_file)
    return recipients

def add_recipient(phone: str, name: str = None) -> bool:
    """Add a new SMS recipient"""
    try:
        store = get_data_store()
        recipients_file = store.data_dir / "recipients.json"
        
        recipients = get_recipients()
        
        # Check if already exists
        for recipient in recipients:
            if recipient['phone'] == phone:
                print(f"Recipient {phone} already exists")
                return False
        
        # Add new recipient
        new_recipient = {
            'phone': phone,
            'name': name if name else phone,
            'added_at': datetime.now().isoformat()
        }
        recipients.append(new_recipient)
        
        # Save locally
        store._save_json(recipients_file, recipients)
        
        # Sync to Firebase
        if store.firebase and store.firebase.connected:
            try:
                store.firebase.update_recipients(recipients)
                print(f"Recipient {phone} synced to Firebase")
            except Exception as e:
                print(f"Failed to sync recipient to Firebase: {e}")
        
        print(f"Recipient {phone} added successfully")
        return True
    except Exception as e:
        print(f"Error adding recipient: {e}")
        return False

def delete_recipient(phone: str) -> bool:
    """Delete an SMS recipient"""
    try:
        store = get_data_store()
        recipients_file = store.data_dir / "recipients.json"
        
        recipients = get_recipients()
        
        # Find and remove
        updated_recipients = [r for r in recipients if r['phone'] != phone]
        
        if len(updated_recipients) == len(recipients):
            print(f"Recipient {phone} not found")
            return False
        
        # Save locally
        store._save_json(recipients_file, updated_recipients)
        
        # Sync to Firebase
        if store.firebase and store.firebase.connected:
            try:
                store.firebase.update_recipients(updated_recipients)
                print(f"Recipient deletion synced to Firebase")
            except Exception as e:
                print(f"Failed to sync deletion to Firebase: {e}")
        
        print(f"Recipient {phone} deleted successfully")
        return True
    except Exception as e:
        print(f"Error deleting recipient: {e}")
        return False

def update_recipient(phone: str, new_name: str) -> bool:
    """Update recipient name"""
    try:
        store = get_data_store()
        recipients_file = store.data_dir / "recipients.json"
        
        recipients = get_recipients()
        
        # Find and update
        found = False
        for recipient in recipients:
            if recipient['phone'] == phone:
                recipient['name'] = new_name
                found = True
                break
        
        if not found:
            print(f"Recipient {phone} not found")
            return False
        
        # Save locally
        store._save_json(recipients_file, recipients)
        
        # Sync to Firebase
        if store.firebase and store.firebase.connected:
            try:
                store.firebase.update_recipients(recipients)
                print(f"Recipient update synced to Firebase")
            except Exception as e:
                print(f"Failed to sync update to Firebase: {e}")
        
        print(f"Recipient {phone} updated successfully")
        return True
    except Exception as e:
        print(f"Error updating recipient: {e}")
        return False