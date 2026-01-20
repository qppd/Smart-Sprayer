# reschedule_logic.py
# Implements complex reschedule and auto-adjust logic

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from core.data_store import get_data_store
from core.logger import get_logger

class RescheduleManager:
    """Manages reschedule logic with auto-adjustment"""
    
    MAX_RESCHEDULES = 3
    
    def __init__(self):
        self.data_store = get_data_store()
        self.logger = get_logger()
    
    def reschedule(self, schedule_id: str, new_date: str, new_time: str) -> Tuple[bool, str, List[Dict]]:
        """
        Reschedule a spray and auto-adjust dependent schedules
        
        Returns:
            (success: bool, message: str, affected_schedules: List[Dict])
        """
        schedule = self.data_store.get_schedule_by_id(schedule_id)
        
        if not schedule:
            return False, "Schedule not found", []
        
        # Check reschedule count
        reschedule_count = schedule.get('reschedule_count', 0)
        
        if reschedule_count >= self.MAX_RESCHEDULES:
            # Cancel all schedules in the series
            self._cancel_all_related_schedules(schedule)
            self.logger.log_warning(
                f"Maximum reschedules ({self.MAX_RESCHEDULES}) reached. "
                f"All related schedules cancelled."
            )
            return False, f"Maximum {self.MAX_RESCHEDULES} reschedules reached. All schedules cancelled.", []
        
        old_date = schedule['date']
        old_time = schedule['time']
        
        # Calculate date shift
        date_shift = self._calculate_date_shift(old_date, new_date)
        
        # Update the main schedule
        updates = {
            'date': new_date,
            'time': new_time,
            'reschedule_count': reschedule_count + 1,
            'status': 'rescheduled',
            'original_date': schedule.get('original_date', old_date),
            'original_time': schedule.get('original_time', old_time)
        }
        
        self.data_store.update_schedule(schedule_id, updates)
        self.logger.log_schedule_rescheduled(old_date, new_date, reschedule_count + 1)
        
        # Auto-adjust dependent schedules
        affected_schedules = self._auto_adjust_schedules(
            schedule, 
            old_date, 
            new_date, 
            date_shift
        )
        
        if affected_schedules:
            self.logger.log_auto_adjust(affected_schedules)
        
        return True, "Schedule rescheduled successfully", affected_schedules
    
    def _calculate_date_shift(self, old_date_str: str, new_date_str: str) -> int:
        """Calculate number of days shifted"""
        old_date = datetime.strptime(old_date_str, '%Y-%m-%d')
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d')
        delta = new_date - old_date
        return delta.days
    
    def _auto_adjust_schedules(self, changed_schedule: Dict, old_date: str, 
                               new_date: str, date_shift: int) -> List[Dict]:
        """
        Auto-adjust all schedules that are affected by the reschedule
        
        Rules:
        1. If rescheduled date conflicts with another schedule, move that schedule forward
        2. If part of an interval-based series, adjust all future schedules by same shift
        """
        affected = []
        all_schedules = self.data_store.get_active_schedules()
        
        # Check for conflicts on the new date
        conflicting_schedules = [
            s for s in all_schedules 
            if s['date'] == new_date and s['id'] != changed_schedule['id']
        ]
        
        for conflict in conflicting_schedules:
            # Move conflicting schedule forward by 1 day
            conflict_date = datetime.strptime(conflict['date'], '%Y-%m-%d')
            new_conflict_date = conflict_date + timedelta(days=1)
            new_conflict_date_str = new_conflict_date.strftime('%Y-%m-%d')
            
            self.data_store.update_schedule(conflict['id'], {
                'date': new_conflict_date_str,
                'status': 'rescheduled'
            })
            
            affected.append({
                'id': conflict['id'],
                'old_date': conflict['date'],
                'new_date': new_conflict_date_str,
                'reason': 'Conflict resolution'
            })
            
            self.logger.log_info(
                f"Auto-adjusted schedule {conflict['id']} from {conflict['date']} "
                f"to {new_conflict_date_str} due to conflict"
            )
        
        # Check if part of an interval-based series
        if 'series_id' in changed_schedule:
            series_id = changed_schedule['series_id']
            series_schedules = [
                s for s in all_schedules 
                if s.get('series_id') == series_id and s['id'] != changed_schedule['id']
            ]
            
            # Sort by date
            series_schedules.sort(key=lambda x: x['date'])
            
            # Find schedules after the changed one
            changed_date = datetime.strptime(old_date, '%Y-%m-%d')
            
            for sched in series_schedules:
                sched_date = datetime.strptime(sched['date'], '%Y-%m-%d')
                
                if sched_date > changed_date:
                    # Apply the same date shift
                    new_sched_date = sched_date + timedelta(days=date_shift)
                    new_sched_date_str = new_sched_date.strftime('%Y-%m-%d')
                    
                    self.data_store.update_schedule(sched['id'], {
                        'date': new_sched_date_str,
                        'status': 'rescheduled'
                    })
                    
                    affected.append({
                        'id': sched['id'],
                        'old_date': sched['date'],
                        'new_date': new_sched_date_str,
                        'reason': 'Series interval preservation'
                    })
                    
                    self.logger.log_info(
                        f"Auto-adjusted schedule {sched['id']} from {sched['date']} "
                        f"to {new_sched_date_str} to preserve series interval"
                    )
        
        return affected
    
    def _cancel_all_related_schedules(self, schedule: Dict):
        """Cancel all schedules in the same series"""
        if 'series_id' in schedule:
            series_id = schedule['series_id']
            all_schedules = self.data_store.get_active_schedules()
            
            for sched in all_schedules:
                if sched.get('series_id') == series_id:
                    self.data_store.update_schedule(sched['id'], {
                        'status': 'cancelled',
                        'cancel_reason': 'Max reschedules exceeded'
                    })
                    self.logger.log_schedule_cancelled(
                        sched['id'], 
                        "Max reschedules exceeded in series"
                    )
        else:
            # Just cancel this single schedule
            self.data_store.update_schedule(schedule['id'], {
                'status': 'cancelled',
                'cancel_reason': 'Max reschedules exceeded'
            })
            self.logger.log_schedule_cancelled(
                schedule['id'], 
                "Max reschedules exceeded"
            )
    
    def cancel_schedule(self, schedule_id: str, reason: str = "User cancelled") -> bool:
        """Cancel a single schedule"""
        schedule = self.data_store.get_schedule_by_id(schedule_id)
        
        if not schedule:
            return False
        
        self.data_store.update_schedule(schedule_id, {
            'status': 'cancelled',
            'cancel_reason': reason
        })
        
        self.logger.log_schedule_cancelled(schedule_id, reason)
        return True
    
    def cancel_all_schedules(self):
        """Cancel all active schedules"""
        all_schedules = self.data_store.get_active_schedules()
        
        for sched in all_schedules:
            self.cancel_schedule(sched['id'], "User cancelled all")
        
        self.logger.log_info(f"Cancelled all {len(all_schedules)} active schedules")


# Global reschedule manager instance
_reschedule_manager_instance = None

def get_reschedule_manager():
    """Get global reschedule manager instance"""
    global _reschedule_manager_instance
    if _reschedule_manager_instance is None:
        _reschedule_manager_instance = RescheduleManager()
    return _reschedule_manager_instance
