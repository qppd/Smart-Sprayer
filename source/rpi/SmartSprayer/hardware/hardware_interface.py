# hardware_interface.py
# Hardware abstraction interface for Smart Sprayer
# Allows switching between ESP32 communication and PC mock mode

import os
import sys

# Determine if running on PC or with ESP32
# Set to True for PC mock mode (testing without ESP32)
# Set to False for ESP32 communication mode (production)
PC_MODE = True  # Change to False when using real ESP32

class HardwareInterface:
    """Base interface for hardware operations"""
    
    def __init__(self):
        if PC_MODE:
            self.mode = "PC Mock"
        else:
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


def get_hardware():
    """Factory function to get appropriate hardware implementation"""
    if PC_MODE:
        from hardware.mock_hardware import MockHardware
        return MockHardware()
    else:
        from hardware.esp32_hardware import ESP32Hardware
        return ESP32Hardware()

