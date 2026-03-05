# logger.py
# Comprehensive logging system for Smart Sprayer

import logging
import os
from datetime import datetime
from pathlib import Path

class SmartSprayerLogger:
    """Custom logger for Smart Sprayer system"""
    
    def __init__(self, log_dir="logs", log_file="smartsprayer.log"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.log_file = self.log_dir / log_file
        
        # Configure logging
        self.logger = logging.getLogger("SmartSprayer")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_info("Smart Sprayer Logger initialized")
    
    def log_info(self, message):
        """Log info level message"""
        self.logger.info(message)
    
    def log_warning(self, message):
        """Log warning level message"""
        self.logger.warning(message)
    
    def log_error(self, message):
        """Log error level message"""
        self.logger.error(message)
    
    def log_debug(self, message):
        """Log debug level message"""
        self.logger.debug(message)
    
    def log_schedule_created(self, schedule_data):
        """Log schedule creation"""
        msg = (f"SCHEDULE CREATED - Date: {schedule_data['date']}, "
               f"Time: {schedule_data['time']}, Type: {schedule_data['spray_type']}, "
               f"Container: {schedule_data['container']}")
        self.log_info(msg)
    
    def log_schedule_rescheduled(self, old_date, new_date, reschedule_count,
                                  spray_type='Unknown', max_reschedule=3):
        """Log schedule reschedule"""
        remaining = max_reschedule - reschedule_count
        if remaining > 0:
            detail = "Remaining schedule adjusted."
        else:
            detail = "No remaining reschedules."
        msg = (
            f"Spraying session rescheduled: {reschedule_count}/{max_reschedule}. "
            f"Spray type: {spray_type}. {detail} "
            f"Date: {new_date}."
        )
        self.log_warning(msg)
    
    def log_schedule_cancelled(self, schedule_id, reason='User cancelled',
                                spray_type='Unknown', max_reschedule=3, date=''):
        """Log schedule cancellation"""
        date_part = f" Date: {date}." if date else ''
        msg = (
            f"Spraying session for {spray_type} has been cancelled. "
            f"All {max_reschedule} reschedules have been used.{date_part} "
            f"ID: {schedule_id}."
        )
        self.log_warning(msg)
    
    def log_auto_adjust(self, affected_schedules):
        """Log auto-adjustment of schedules"""
        msg = f"AUTO-ADJUST triggered - {len(affected_schedules)} schedule(s) adjusted"
        self.log_info(msg)
        for sched in affected_schedules:
            self.log_debug(f"  - Schedule {sched['id']} moved from {sched['old_date']} to {sched['new_date']}")
    
    def log_spray_executed(self, schedule_data, volume_ml=None, duration_sec=None):
        """Log spray execution start"""
        spray_type  = schedule_data.get('spray_type', 'Unknown')
        vol         = volume_ml  if volume_ml  is not None else schedule_data.get('volume_ml', '--')
        dur         = f"{duration_sec:.1f}" if duration_sec is not None else '--'
        date        = schedule_data.get('date', '--')
        msg = (
            f"Spraying started: {vol} mL of {spray_type} "
            f"for {dur} seconds. "
            f"Date: {date}."
        )
        self.log_info(msg)
    
    def log_spray_completed(self, schedule_id, duration, spray_type='Unknown', volume_ml=None):
        """Log spray completion"""
        vol = f"{int(volume_ml)}" if volume_ml is not None else '--'
        msg = (
            f"Spraying completed: {vol} mL of {spray_type} applied. "
            f"ID: {schedule_id}, Duration: {duration:.1f} seconds."
        )
        self.log_info(msg)
    
    def log_system_status(self, status):
        """Log system status change"""
        msg = f"SYSTEM STATUS: {status}"
        self.log_info(msg)
    
    def log_tank_level(self, container_num, level_percent):
        """Log tank level"""
        msg = f"TANK {container_num} LEVEL: {level_percent}%"
        self.log_debug(msg)
    
    def log_hardware_action(self, action, component):
        """Log hardware action"""
        msg = f"HARDWARE ACTION - {component}: {action}"
        self.log_debug(msg)
    
    def read_logs(self, num_lines=100):
        """Read recent log entries"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return lines[-num_lines:] if len(lines) > num_lines else lines
        except FileNotFoundError:
            return []
    
    def clear_logs(self):
        """Clear log file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")
            self.log_info("Log file cleared")
        except Exception as e:
            self.log_error(f"Failed to clear logs: {e}")


# Global logger instance
_logger_instance = None

def get_logger():
    """Get global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SmartSprayerLogger()
    return _logger_instance
