# firebase_service.py
# Firebase integration service for Smart Sprayer
# Handles all Firebase operations for schedules, history, and system status

import pyrebase
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
import json
import sys
import os

# Add parent directory to path to ensure firebase_credentials can be imported
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from firebase_credentials import FIREBASE_CONFIG, FIREBASE_USER
    # Verify that credentials are actually loaded
    if FIREBASE_CONFIG and FIREBASE_USER:
        FIREBASE_AVAILABLE = True
    else:
        print("Warning: Firebase credentials are empty or None")
        FIREBASE_AVAILABLE = False
except ImportError as e:
    print(f"Warning: firebase_credentials.py not found - {e}")
    FIREBASE_AVAILABLE = False
    FIREBASE_CONFIG = None
    FIREBASE_USER = None
except Exception as e:
    print(f"Warning: Error loading Firebase credentials - {e}")
    FIREBASE_AVAILABLE = False
    FIREBASE_CONFIG = None
    FIREBASE_USER = None


class FirebaseService:
    """Firebase service for cloud data synchronization"""
    
    def __init__(self, device_id="SmartSprayer_001"):
        self.device_id = device_id
        self.firebase = None
        self.db = None
        self.auth = None
        self.user = None
        self.connected = False
        self.sync_enabled = False
        
        # Sync callbacks
        self.on_schedule_updated = None
        self.on_remote_command = None
        
        # Thread for background sync
        self.sync_thread = None
        self.running = False
        
        if FIREBASE_AVAILABLE and FIREBASE_CONFIG:
            self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            # Initialize Pyrebase
            self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
            self.db = self.firebase.database()
            self.auth = self.firebase.auth()
            
            # Authenticate if credentials provided
            if FIREBASE_USER and FIREBASE_USER.get('email') and FIREBASE_USER.get('password'):
                self.user = self.auth.sign_in_with_email_and_password(
                    FIREBASE_USER['email'],
                    FIREBASE_USER['password']
                )
                print(f"Firebase authenticated as: {FIREBASE_USER['email']}")
            
            self.connected = True
            print("Firebase initialized successfully")
            
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            self.connected = False
    
    def enable_sync(self):
        """Enable background synchronization"""
        if not self.connected:
            print("Firebase not connected. Cannot enable sync.")
            return False
        
        self.sync_enabled = True
        self.running = True
        
        # Start background sync thread
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        
        print("Firebase sync enabled")
        return True
    
    def disable_sync(self):
        """Disable background synchronization"""
        self.sync_enabled = False
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2)
        print("Firebase sync disabled")
    
    def _sync_loop(self):
        """Background sync loop"""
        while self.running:
            try:
                # Check for remote commands
                self._check_remote_commands()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"Sync loop error: {e}")
                time.sleep(10)
    
    def _check_remote_commands(self):
        """Check for remote commands from Firebase"""
        if not self.sync_enabled:
            return
        
        try:
            # Get remote commands for this device
            commands = self.db.child("devices").child(self.device_id).child("commands").get()
            
            if commands.val() and self.on_remote_command:
                for cmd_id, cmd_data in commands.val().items():
                    if not cmd_data.get('executed', False):
                        # Execute command
                        self.on_remote_command(cmd_data)
                        
                        # Mark as executed
                        self.db.child("devices").child(self.device_id).child("commands").child(cmd_id).update({
                            'executed': True,
                            'executed_at': datetime.now().isoformat()
                        })
        except Exception as e:
            print(f"Error checking remote commands: {e}")
    
    # Schedule Management
    def upload_schedule(self, schedule: Dict) -> bool:
        """Upload a schedule to Firebase"""
        if not self.connected:
            return False
        
        try:
            schedule_id = schedule.get('id')
            path = f"devices/{self.device_id}/schedules/{schedule_id}"
            
            # Add timestamp
            schedule_data = schedule.copy()
            schedule_data['synced_at'] = datetime.now().isoformat()
            
            self.db.child("devices").child(self.device_id).child("schedules").child(schedule_id).set(schedule_data)
            return True
        except Exception as e:
            print(f"Error uploading schedule: {e}")
            return False
    
    def upload_schedules(self, schedules: List[Dict]) -> bool:
        """Upload multiple schedules to Firebase"""
        if not self.connected:
            return False
        
        try:
            schedules_data = {}
            for schedule in schedules:
                schedule_data = schedule.copy()
                schedule_data['synced_at'] = datetime.now().isoformat()
                schedules_data[schedule['id']] = schedule_data
            
            self.db.child("devices").child(self.device_id).child("schedules").set(schedules_data)
            return True
        except Exception as e:
            print(f"Error uploading schedules: {e}")
            return False
    
    def get_schedules(self) -> List[Dict]:
        """Get all schedules from Firebase"""
        if not self.connected:
            return []
        
        try:
            schedules = self.db.child("devices").child(self.device_id).child("schedules").get()
            
            if schedules.val():
                return list(schedules.val().values())
            return []
        except Exception as e:
            print(f"Error getting schedules: {e}")
            return []
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule from Firebase"""
        if not self.connected:
            return False
        
        try:
            self.db.child("devices").child(self.device_id).child("schedules").child(schedule_id).remove()
            return True
        except Exception as e:
            print(f"Error deleting schedule: {e}")
            return False
    
    # History Management
    def upload_history_entry(self, entry: Dict) -> bool:
        """Upload a spray history entry to Firebase"""
        if not self.connected:
            return False
        
        try:
            entry_id = entry.get('id', f"HIST_{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            entry_data = entry.copy()
            entry_data['synced_at'] = datetime.now().isoformat()
            
            self.db.child("devices").child(self.device_id).child("history").child(entry_id).set(entry_data)
            return True
        except Exception as e:
            print(f"Error uploading history: {e}")
            return False
    
    def upload_history(self, history: List[Dict]) -> bool:
        """Upload multiple history entries to Firebase"""
        if not self.connected:
            return False
        
        try:
            history_data = {}
            for entry in history:
                entry_id = entry.get('id', f"HIST_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                entry_data = entry.copy()
                entry_data['synced_at'] = datetime.now().isoformat()
                history_data[entry_id] = entry_data
            
            self.db.child("devices").child(self.device_id).child("history").set(history_data)
            return True
        except Exception as e:
            print(f"Error uploading history: {e}")
            return False
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get spray history from Firebase"""
        if not self.connected:
            return []
        
        try:
            if limit:
                history = self.db.child("devices").child(self.device_id).child("history").limit_to_last(limit).get()
            else:
                history = self.db.child("devices").child(self.device_id).child("history").get()
            
            if history.val():
                return list(history.val().values())
            return []
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    # System Status
    def update_device_status(self, status: Dict) -> bool:
        """Update device status in Firebase"""
        if not self.connected:
            return False
        
        try:
            status_data = status.copy()
            status_data['last_update'] = datetime.now().isoformat()
            
            self.db.child("devices").child(self.device_id).child("status").set(status_data)
            return True
        except Exception as e:
            print(f"Error updating device status: {e}")
            return False
    
    def update_tank_levels(self, tank1_percent: float, tank2_percent: float) -> bool:
        """Update tank levels in Firebase"""
        if not self.connected:
            return False
        
        try:
            self.db.child("devices").child(self.device_id).child("status").update({
                'tank1_level': tank1_percent,
                'tank2_level': tank2_percent,
                'last_update': datetime.now().isoformat()
            })
            return True
        except Exception as e:
            print(f"Error updating tank levels: {e}")
            return False
    
    # Weather Data (stored by RPI)
    def upload_weather_data(self, weather_data: Dict) -> bool:
        """Upload weather data to Firebase"""
        if not self.connected:
            return False
        
        try:
            weather_data['timestamp'] = datetime.now().isoformat()
            self.db.child("devices").child(self.device_id).child("weather").set(weather_data)
            return True
        except Exception as e:
            print(f"Error uploading weather data: {e}")
            return False
    
    def get_weather_data(self) -> Optional[Dict]:
        """Get latest weather data from Firebase"""
        if not self.connected:
            return None
        
        try:
            weather = self.db.child("devices").child(self.device_id).child("weather").get()
            return weather.val()
        except Exception as e:
            print(f"Error getting weather data: {e}")
            return None
    
    # Recipients Management
    def update_recipients(self, recipients: List[Dict]) -> bool:
        """Upload recipients list to Firebase"""
        if not self.connected:
            return False
        
        try:
            data = {
                'recipients': recipients,
                'updated_at': datetime.now().isoformat()
            }
            
            self.db.child("devices").child(self.device_id).child("recipients").set(
                data, 
                self.user['idToken'] if self.user else None
            )
            print(f"Recipients synced to Firebase: {len(recipients)} recipients")
            return True
        except Exception as e:
            print(f"Error updating recipients: {e}")
            return False
    
    def get_recipients(self) -> List[Dict]:
        """Get recipients list from Firebase"""
        if not self.connected:
            return []
        
        try:
            data = self.db.child("devices").child(self.device_id).child("recipients").get(
                self.user['idToken'] if self.user else None
            ).val()
            
            if data and 'recipients' in data:
                return data['recipients']
            return []
        except Exception as e:
            print(f"Error getting recipients: {e}")
            return []
    
            return {}
        
        try:
            history = self.get_history()
            
            total_sprays = len(history)
            fertilizer_count = len([h for h in history if h.get('spray_type') == 'Fertilizer'])
            pesticide_count = len([h for h in history if h.get('spray_type') == 'Pesticide'])
            total_volume = sum([h.get('volume_ml', 0) for h in history])
            
            return {
                'total_sprays': total_sprays,
                'fertilizer_count': fertilizer_count,
                'pesticide_count': pesticide_count,
                'total_volume_ml': total_volume,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return {}


# Global Firebase service instance
_firebase_service = None

def get_firebase_service(device_id="SmartSprayer_001") -> FirebaseService:
    """Get the global Firebase service instance"""
    global _firebase_service
    if _firebase_service is None:
        _firebase_service = FirebaseService(device_id)
    return _firebase_service
