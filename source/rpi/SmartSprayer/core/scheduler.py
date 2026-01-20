# scheduler.py
# Main scheduler logic with background execution

import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from core.data_store import get_data_store
from core.logger import get_logger
from core.reschedule_logic import get_reschedule_manager

class Scheduler:
    """Main scheduler for spray operations"""
    
    def __init__(self, hardware_interface=None):
        self.data_store = get_data_store()
        self.logger = get_logger()
        self.reschedule_mgr = get_reschedule_manager()
        self.hardware = hardware_interface
        
        self.running = False
        self.scheduler_thread = None
        
        # Callbacks for UI updates
        self.on_schedule_due_callback = None
        self.on_schedule_completed_callback = None
        self.on_status_change_callback = None
        
        self.logger.log_info("Scheduler initialized")
    
    def start(self):
        """Start scheduler background thread"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            self.logger.log_info("Scheduler started")
    
    def stop(self):
        """Stop scheduler"""
        if self.running:
            self.running = False
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=2)
            self.logger.log_info("Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop - runs in background"""
        while self.running:
            try:
                self._check_due_schedules()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                self.logger.log_error(f"Scheduler error: {e}")
    
    def _check_due_schedules(self):
        """Check for schedules that are due"""
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')
        
        active_schedules = self.data_store.get_active_schedules()
        
        for schedule in active_schedules:
            if schedule['date'] == current_date:
                # Check if time matches (within 1 minute window)
                schedule_time = datetime.strptime(schedule['time'], '%H:%M')
                current_datetime = datetime.strptime(current_time, '%H:%M')
                
                time_diff = abs((schedule_time - current_datetime).total_seconds())
                
                if time_diff < 60 and schedule.get('status') != 'executing':
                    # Schedule is due!
                    self._execute_schedule(schedule)
    
    def _execute_schedule(self, schedule: Dict):
        """Execute a spray schedule"""
        self.logger.log_spray_executed(schedule)
        
        # Update status to executing
        self.data_store.update_schedule(schedule['id'], {'status': 'executing'})
        
        if self.on_schedule_due_callback:
            self.on_schedule_due_callback(schedule)
        
        # Perform spray operation
        try:
            container = schedule['container']
            spray_type = schedule['spray_type']
            
            self.logger.log_info(
                f"Executing spray: {spray_type} using {container}"
            )
            
            # Determine which relay to activate based on container
            relay_num = 1 if container == "Container 1" else 2
            
            # Turn on relay
            if self.hardware:
                self.hardware.relay_on(relay_num)
                self.hardware.buzzer_beep(0.5)
                self.hardware.set_led('status', 1)
            
            # Spray for configured duration (e.g., 30 seconds)
            spray_duration = schedule.get('duration', 30)
            time.sleep(spray_duration)
            
            # Turn off relay
            if self.hardware:
                self.hardware.relay_off(relay_num)
                self.hardware.set_led('status', 0)
            
            # Mark as completed
            self.data_store.update_schedule(schedule['id'], {'status': 'completed'})
            
            # Add to history
            self.data_store.add_to_history({
                'date': schedule['date'],
                'time': schedule['time'],
                'spray_type': spray_type,
                'container': container,
                'duration': spray_duration,
                'schedule_id': schedule['id']
            })
            
            self.logger.log_spray_completed(schedule['id'], spray_duration)
            
            if self.on_schedule_completed_callback:
                self.on_schedule_completed_callback(schedule)
        
        except Exception as e:
            self.logger.log_error(f"Error executing schedule {schedule['id']}: {e}")
            self.data_store.update_schedule(schedule['id'], {
                'status': 'failed',
                'error': str(e)
            })
    
    def create_schedule(self, date: str, time: str, spray_type: str, 
                       container: str, duration: int = 30) -> Dict:
        """Create a single schedule"""
        schedule = {
            'date': date,
            'time': time,
            'spray_type': spray_type,
            'container': container,
            'duration': duration,
            'status': 'scheduled'
        }
        
        schedule = self.data_store.add_schedule(schedule)
        self.logger.log_schedule_created(schedule)
        
        return schedule
    
    def create_recurring_schedules(self, start_date: str, interval_days: int, 
                                  count: int, time: str, spray_type: str, 
                                  container: str, duration: int = 30) -> List[Dict]:
        """Create multiple schedules with fixed interval"""
        schedules = []
        series_id = f"SERIES_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(count):
            date_str = current_date.strftime('%Y-%m-%d')
            
            schedule = {
                'date': date_str,
                'time': time,
                'spray_type': spray_type,
                'container': container,
                'duration': duration,
                'status': 'scheduled',
                'series_id': series_id,
                'series_interval': interval_days
            }
            
            schedule = self.data_store.add_schedule(schedule)
            self.logger.log_schedule_created(schedule)
            schedules.append(schedule)
            
            # Move to next date
            current_date += timedelta(days=interval_days)
        
        self.logger.log_info(
            f"Created recurring series: {count} schedules with {interval_days}-day interval"
        )
        
        return schedules
    
    def get_next_schedule(self) -> Optional[Dict]:
        """Get the next upcoming schedule"""
        active_schedules = self.data_store.get_active_schedules()
        
        if not active_schedules:
            return None
        
        # Sort by date and time
        sorted_schedules = sorted(
            active_schedules,
            key=lambda x: f"{x['date']} {x['time']}"
        )
        
        now = datetime.now()
        
        for schedule in sorted_schedules:
            schedule_dt = datetime.strptime(
                f"{schedule['date']} {schedule['time']}",
                '%Y-%m-%d %H:%M'
            )
            
            if schedule_dt > now:
                return schedule
        
        return None
    
    def get_time_until_next_spray(self) -> Optional[str]:
        """Get countdown to next spray"""
        next_schedule = self.get_next_schedule()
        
        if not next_schedule:
            return None
        
        schedule_dt = datetime.strptime(
            f"{next_schedule['date']} {next_schedule['time']}",
            '%Y-%m-%d %H:%M'
        )
        
        now = datetime.now()
        delta = schedule_dt - now
        
        if delta.total_seconds() < 0:
            return "Overdue"
        
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    def set_callbacks(self, on_schedule_due=None, on_schedule_completed=None, 
                     on_status_change=None):
        """Set callback functions for UI updates"""
        self.on_schedule_due_callback = on_schedule_due
        self.on_schedule_completed_callback = on_schedule_completed
        self.on_status_change_callback = on_status_change


# Global scheduler instance
_scheduler_instance = None

def get_scheduler(hardware_interface=None):
    """Get global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = Scheduler(hardware_interface)
    return _scheduler_instance
