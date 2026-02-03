# scheduler.py
# Main scheduler logic with background execution

import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from core.data_store import get_data_store
from core.logger import get_logger
from core.reschedule_logic import get_reschedule_manager

try:
    from core.weather_service import get_weather_service
    WEATHER_AVAILABLE = True
except ImportError:
    WEATHER_AVAILABLE = False
    print("Weather service not available")

class Scheduler:
    """Main scheduler for spray operations"""
    
    # Pump specifications
    PUMP_RATE_ML_PER_MIN = 5000  # 5L/min = 5000 mL/min
    
    def __init__(self, hardware_interface=None):
        self.data_store = get_data_store()
        self.logger = get_logger()
        self.reschedule_mgr = get_reschedule_manager()
        self.hardware = hardware_interface
        
        # Initialize weather service
        self.weather = None
        if WEATHER_AVAILABLE:
            self.weather = get_weather_service()
        
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
        
        # Check weather before executing
        if self.weather and self.weather.available:
            self.logger.log_info("Checking weather before spray...")
            
            # Check current weather
            is_raining = self.weather.check_weather_for_rain()
            
            if is_raining:
                self.logger.log_warning(f"Rain detected! Checking reschedule count for schedule {schedule['id']}")
                self._handle_weather_reschedule(schedule)
                return
            
            # Check forecast for next 24 hours
            rain_forecast = self.weather.check_forecast_for_rain(hours_ahead=24)
            
            if rain_forecast:
                self.logger.log_warning(f"Rain expected in forecast! Checking reschedule count for schedule {schedule['id']}")
                self._handle_weather_reschedule(schedule)
                return
            
            self.logger.log_info("Weather check passed - safe to spray")
        
        self.logger.log_spray_executed(schedule)
        
        # Update status to executing
        self.data_store.update_schedule(schedule['id'], {'status': 'executing'})
        
        if self.on_schedule_due_callback:
            self.on_schedule_due_callback(schedule)
        
        # Perform spray operation via ESP32
        try:
            container = schedule['container']
            spray_type = schedule['spray_type']
            volume_ml = schedule.get('volume_ml', 1000)  # Default 1000 mL
            
            # Determine which relay to activate based on container
            relay_num = 1 if container == "Container 1" else 2
            
            # Calculate spray duration based on volume
            spray_duration = self.calculate_spray_duration(volume_ml)
            
            self.logger.log_info(
                f"Executing spray: {spray_type} using {container}, "
                f"{volume_ml}mL for {spray_duration:.1f} seconds"
            )
            
            # Execute spray via ESP32
            if self.hardware:
                # Use ESP32's spray command (ESP32 handles relay, SMS, buzzer)
                self.hardware.spray(relay_num, spray_duration, volume_ml)
                
                # Wait for spray to complete (ESP32 is blocking during spray)
                # Add a small buffer for SMS sending
                import time
                time.sleep(spray_duration + 2)
            
            # Mark as completed
            self.data_store.update_schedule(schedule['id'], {
                'status': 'completed',
                'completed_at': datetime.now().isoformat()
            })
            
            # Add to history
            self.data_store.add_to_history({
                'date': schedule['date'],
                'time': schedule['time'],
                'spray_type': spray_type,
                'container': container,
                'volume_ml': volume_ml,
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
    
    def _handle_weather_reschedule(self, schedule: Dict):
        """
        Handle weather-based reschedule with 3-attempt limit.
        
        Logic:
        1. If rain detected today → reschedule to tomorrow
        2. If rain again tomorrow → reschedule to day after
        3. After 3 consecutive rain reschedules → CANCEL (user must manually reschedule)
        """
        reschedule_count = schedule.get('reschedule_count', 0)
        
        self.logger.log_info(f"Weather reschedule attempt #{reschedule_count + 1} for schedule {schedule['id']}")
        
        if reschedule_count >= 3:
            # Max reschedules reached - cancel the schedule
            self.logger.log_warning(
                f"Maximum weather reschedules (3) reached for schedule {schedule['id']}. "
                f"Cancelling - user must manually reschedule."
            )
            
            self.data_store.update_schedule(schedule['id'], {
                'status': 'cancelled',
                'cancel_reason': 'weather_max_reschedules',
                'cancelled_at': datetime.now().isoformat(),
                'cancel_message': 'Cancelled after 3 consecutive rain days. Please reschedule manually.'
            })
            
            # Notify via callback
            if self.on_status_change_callback:
                self.on_status_change_callback({
                    'type': 'weather_cancelled',
                    'schedule_id': schedule['id'],
                    'message': 'Schedule cancelled after 3 rain postponements. Please create new schedule.'
                })
            
            return
        
        # Calculate new date (postpone by 1 day)
        current_date = datetime.strptime(schedule['date'], '%Y-%m-%d')
        new_date = current_date + timedelta(days=1)
        new_date_str = new_date.strftime('%Y-%m-%d')
        
        # Keep same time
        time_str = schedule['time']
        
        # Update schedule directly with new date and incremented count
        updates = {
            'date': new_date_str,
            'time': time_str,
            'reschedule_count': reschedule_count + 1,
            'status': 'rescheduled',
            'reschedule_reason': 'weather',
            'weather_checked_at': datetime.now().isoformat(),
            'original_date': schedule.get('original_date', schedule['date']),
            'original_time': schedule.get('original_time', schedule['time'])
        }
        
        self.data_store.update_schedule(schedule['id'], updates)
        
        self.logger.log_info(
            f"Schedule {schedule['id']} rescheduled to {new_date_str} {time_str} "
            f"due to weather (attempt {reschedule_count + 1}/3)"
        )
        
        # Notify via callback
        if self.on_status_change_callback:
            self.on_status_change_callback({
                'type': 'weather_reschedule',
                'schedule_id': schedule['id'],
                'new_date': new_date_str,
                'reschedule_count': reschedule_count + 1,
                'message': f'Schedule postponed due to rain (attempt {reschedule_count + 1}/3)'
            })
    
    def calculate_spray_duration(self, volume_ml: float) -> float:
        """Calculate spray duration in seconds based on volume and pump rate"""
        # Pump rate: 5000 mL/min = 5000/60 mL/sec
        duration_seconds = (volume_ml / self.PUMP_RATE_ML_PER_MIN) * 60
        return duration_seconds
    
    def create_schedule(self, date: str, time: str, spray_type: str, 
                       container: str, volume_ml: float = 1000) -> Dict:
        """Create a single schedule"""
        schedule = {
            'date': date,
            'time': time,
            'spray_type': spray_type,
            'container': container,
            'volume_ml': volume_ml,
            'status': 'scheduled'
        }
        
        schedule = self.data_store.add_schedule(schedule)
        self.logger.log_schedule_created(schedule)
        
        return schedule
    
    def create_recurring_schedules(self, start_date: str, interval_days: int, 
                                  count: int, time: str, spray_type: str, 
                                  container: str, volume_ml: float = 1000) -> List[Dict]:
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
                'volume_ml': volume_ml,
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
    
    def check_weather_for_schedule(self, schedule_id: str) -> Dict:
        """
        Manually check weather for a specific schedule
        Returns weather status and recommendation
        """
        if not self.weather or not self.weather.available:
            return {
                'available': False,
                'message': 'Weather service not configured'
            }
        
        schedule = self.data_store.get_schedule_by_id(schedule_id)
        if not schedule:
            return {
                'available': False,
                'message': 'Schedule not found'
            }
        
        # Check current weather
        is_raining = self.weather.check_weather_for_rain()
        
        # Check forecast
        rain_forecast = self.weather.check_forecast_for_rain(hours_ahead=24)
        
        # Get detailed weather
        weather_data = self.weather.get_weather_data()
        
        return {
            'available': True,
            'schedule_id': schedule_id,
            'is_raining_now': is_raining,
            'rain_forecast': rain_forecast,
            'recommendation': 'Reschedule' if (is_raining or rain_forecast) else 'Safe to spray',
            'weather_data': weather_data,
            'checked_at': datetime.now().isoformat()
        }
    
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
