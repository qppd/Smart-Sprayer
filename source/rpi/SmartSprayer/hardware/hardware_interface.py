# hardware_interface.py
# Hardware abstraction interface for Smart Sprayer
# Allows switching between real Raspberry Pi hardware and PC mock mode

import os
import sys

# Determine if running on PC or Raspberry Pi
PC_MODE = os.name == 'nt' or not os.path.exists('/sys/class/gpio')

class HardwareInterface:
    """Base interface for hardware operations"""
    
    def __init__(self):
        self.mode = "PC" if PC_MODE else "Raspberry Pi"
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
    
    # LEDs
    def set_led(self, led_name, state):
        raise NotImplementedError
    
    # Buttons
    def read_button(self, button_name):
        raise NotImplementedError
    
    # System
    def cleanup(self):
        raise NotImplementedError


def get_hardware():
    """Factory function to get appropriate hardware implementation"""
    if PC_MODE:
        from hardware.mock_hardware import MockHardware
        return MockHardware()
    else:
        from hardware.real_hardware import RealHardware
        return RealHardware()
