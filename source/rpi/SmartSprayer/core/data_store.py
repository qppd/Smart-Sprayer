# data_store.py
# Data persistence for schedules and spray history

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class DataStore:
    """Manages persistent storage of schedules and history"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.schedules_file = self.data_dir / "schedules.json"
        self.history_file = self.data_dir / "history.json"
        
        # Initialize files if they don't exist
        self._init_files()
    
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
        
        return schedule
    
    def update_schedule(self, schedule_id: str, updates: Dict) -> Optional[Dict]:
        """Update existing schedule"""
        schedules = self.get_all_schedules()
        
        for i, sched in enumerate(schedules):
            if sched['id'] == schedule_id:
                schedules[i].update(updates)
                schedules[i]['updated_at'] = datetime.now().isoformat()
                self._save_json(self.schedules_file, schedules)
                return schedules[i]
        
        return None
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete schedule"""
        schedules = self.get_all_schedules()
        original_count = len(schedules)
        
        schedules = [s for s in schedules if s['id'] != schedule_id]
        
        if len(schedules) < original_count:
            self._save_json(self.schedules_file, schedules)
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
        history.append(spray_data)
        
        self._save_json(self.history_file, history)
    
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


# Global data store instance
_data_store_instance = None

def get_data_store():
    """Get global data store instance"""
    global _data_store_instance
    if _data_store_instance is None:
        _data_store_instance = DataStore()
    return _data_store_instance
