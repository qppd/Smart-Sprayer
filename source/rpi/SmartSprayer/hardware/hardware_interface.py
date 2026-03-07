# hardware_interface.py
# Hardware abstraction interface for Smart Sprayer
# RPI communicates with ESP32 via serial for all hardware operations

import os
import sys

class HardwareInterface:
    """Base interface for hardware operations"""
    
    def __init__(self):
        self.mode = "ESP32"
        print(f"Hardware Interface initialized in {self.mode} mode")
    
    # Relay Controls
    def relay_on(self, relay_num=1):
        raise NotImplementedError
    
    def relay_off(self, relay_num=1):
        raise NotImplementedError
    
    # Ultrasonic Sensors (2 containers)
    def read_distance(self, sensor_num=1):
        raise NotImplementedError
    
    def get_tank_level_percentage(self, sensor_num=1):
        raise NotImplementedError

    def get_both_tank_levels(self):
        """Return dict with keys 'tank1' and/or 'tank2' as float percentages.
        Default implementation calls get_tank_level_percentage for each sensor."""
        levels = {}
        t1 = self.get_tank_level_percentage(1)
        if t1 is not None:
            levels['tank1'] = t1
        t2 = self.get_tank_level_percentage(2)
        if t2 is not None:
            levels['tank2'] = t2
        return levels
    
    # Buzzer
    def buzzer_on(self):
        raise NotImplementedError
    
    def buzzer_off(self):
        raise NotImplementedError
    
    def buzzer_beep(self, duration=0.5):
        raise NotImplementedError
    
    # LEDs - Deprecated (removed from ESP32)
    def set_led(self, led_name, state):
        """LEDs removed from ESP32 firmware"""
        pass
    
    # Buttons - Deprecated (removed from ESP32)
    def read_button(self, button_name):
        """Buttons removed from ESP32 firmware"""
        return False
    
    # System
    def cleanup(self):
        raise NotImplementedError


_hardware_instance = None

def get_hardware(port='/dev/ttyUSB0', baudrate=9600, timeout=1):
    """Singleton factory — always returns the same ESP32Hardware instance.

    The first call creates the instance. Subsequent calls (e.g. from settings.py
    when run standalone) return the existing object, ensuring all parts of the
    application share one serial connection.
    """
    global _hardware_instance
    if _hardware_instance is None:
        from hardware.esp32_hardware import ESP32Hardware
        _hardware_instance = ESP32Hardware(port=port, baudrate=baudrate, timeout=timeout)
    return _hardware_instance

