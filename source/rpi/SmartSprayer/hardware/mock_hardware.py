# mock_hardware.py
# Mock hardware implementation for PC testing
# Simulates all hardware components without requiring GPIO

import random
import time
import threading
from hardware.hardware_interface import HardwareInterface

class MockHardware(HardwareInterface):
    """Mock hardware for PC testing"""
    
    def __init__(self):
        super().__init__()
        # Simulate tank levels (distance in cm from sensor to liquid surface)
        self.tank1_distance = 20.0  # 20cm from top = 80% full (if tank is 100cm)
        self.tank2_distance = 50.0  # 50cm from top = 50% full
        self.container_height = 100.0  # cm
        
        # Relay states
        self.relay1_state = False
        self.relay2_state = False
        
        # Buzzer state
        self.buzzer_state = False
        
        # LED states
        self.leds = {
            'status': False,
            'warning': False,
            'ok': False,
            'error': False
        }
        
        # Button states
        self.buttons = {
            'up': False,
            'down': False,
            'select': False,
            'reset': False
        }
        
        # Start simulation thread
        self.running = True
        self.sim_thread = threading.Thread(target=self._simulate_tank_changes, daemon=True)
        self.sim_thread.start()
        
        print("Mock Hardware initialized - All sensors simulated")
    
    def _simulate_tank_changes(self):
        """Simulate gradual tank level changes"""
        while self.running:
            # Randomly adjust tank levels slightly (simulate usage/evaporation)
            self.tank1_distance += random.uniform(-0.5, 0.2)
            self.tank2_distance += random.uniform(-0.5, 0.2)
            
            # Keep within reasonable bounds
            self.tank1_distance = max(5, min(95, self.tank1_distance))
            self.tank2_distance = max(5, min(95, self.tank2_distance))
            
            time.sleep(5)  # Update every 5 seconds
    
    def relay_on(self, relay_num=1):
        """Turn relay ON"""
        if relay_num == 1:
            self.relay1_state = True
            print(f"[MOCK] Relay {relay_num} turned ON")
        elif relay_num == 2:
            self.relay2_state = True
            print(f"[MOCK] Relay {relay_num} turned ON")
    
    def relay_off(self, relay_num=1):
        """Turn relay OFF"""
        if relay_num == 1:
            self.relay1_state = False
            print(f"[MOCK] Relay {relay_num} turned OFF")
        elif relay_num == 2:
            self.relay2_state = False
            print(f"[MOCK] Relay {relay_num} turned OFF")
    
    def read_distance(self, sensor_num=1):
        """Read distance from ultrasonic sensor in cm"""
        if sensor_num == 1:
            distance = self.tank1_distance
        else:
            distance = self.tank2_distance
        
        # Add small random noise to simulate real sensor
        distance += random.uniform(-0.5, 0.5)
        return max(0, distance)
    
    def get_tank_level_percentage(self, sensor_num=1):
        """Calculate tank level as percentage (0-100%)"""
        distance = self.read_distance(sensor_num)
        
        # Convert distance to percentage
        # Distance measured from top: smaller distance = more liquid = higher percentage
        percentage = ((self.container_height - distance) / self.container_height) * 100
        percentage = max(0, min(100, percentage))
        
        return round(percentage, 1)
    
    def buzzer_on(self):
        """Turn buzzer ON"""
        self.buzzer_state = True
        print("[MOCK] Buzzer turned ON")
    
    def buzzer_off(self):
        """Turn buzzer OFF"""
        self.buzzer_state = False
        print("[MOCK] Buzzer turned OFF")
    
    def buzzer_beep(self, duration=0.5):
        """Beep buzzer for specified duration"""
        print(f"[MOCK] Buzzer beeped for {duration}s")
        self.buzzer_on()
        time.sleep(duration)
        self.buzzer_off()
    
    def set_led(self, led_name, state):
        """Set LED state"""
        if led_name in self.leds:
            self.leds[led_name] = bool(state)
            print(f"[MOCK] LED '{led_name}' set to {'ON' if state else 'OFF'}")
    
    def read_button(self, button_name):
        """Read button state"""
        return self.buttons.get(button_name, False)
    
    def set_tank_level(self, sensor_num, distance):
        """Manually set tank level for testing"""
        if sensor_num == 1:
            self.tank1_distance = distance
        else:
            self.tank2_distance = distance
        print(f"[MOCK] Tank {sensor_num} level set to {distance}cm (distance from top)")
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
        if hasattr(self, 'sim_thread'):
            self.sim_thread.join(timeout=1)
        print("[MOCK] Hardware cleanup completed")
