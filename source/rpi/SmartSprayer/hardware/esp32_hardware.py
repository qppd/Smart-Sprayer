# esp32_hardware.py
# Hardware implementation that communicates with ESP32 via USB serial
# ESP32 handles all physical hardware components
#
# Common serial port names:
#   Linux/Raspberry Pi: /dev/ttyUSB0, /dev/ttyACM0
#   Windows: COM3, COM4, COM5, etc.
#   macOS: /dev/cu.usbserial-XXXX

import serial
import time
import threading
from hardware.hardware_interface import HardwareInterface

class ESP32Hardware(HardwareInterface):
    """Hardware implementation that communicates with ESP32 via USB serial"""
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.connected = False
        
        # Try to connect to ESP32
        self._connect()
        
    def _connect(self):
        """Establish serial connection with ESP32"""
        try:
            self.serial_connection = serial.Serial(
                self.port, 
                self.baudrate, 
                timeout=self.timeout
            )
            time.sleep(2)  # Wait for connection to stabilize
            self.connected = True
            print(f"[ESP32] Connected to ESP32 on {self.port}")
        except Exception as e:
            print(f"[ESP32] Failed to connect to ESP32: {e}")
            print(f"[ESP32] Make sure ESP32 is connected to {self.port}")
            self.connected = False
    
    def _send_command(self, command):
        """Send command to ESP32 and return response"""
        if not self.connected or not self.serial_connection:
            print(f"[ESP32] Not connected. Command '{command}' not sent.")
            return None
        
        try:
            # Send command
            self.serial_connection.write(f"{command}\n".encode())
            time.sleep(0.1)
            
            # Read response
            response = ""
            while self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    response += line + "\n"
            
            return response.strip() if response else None
        except Exception as e:
            print(f"[ESP32] Error sending command '{command}': {e}")
            return None
    
    def relay_on(self, relay_num=1):
        """Turn relay ON via ESP32"""
        command = f"operate-relay{relay_num}_on"
        response = self._send_command(command)
        print(f"[ESP32] Relay {relay_num} turned ON")
        return response
    
    def relay_off(self, relay_num=1):
        """Turn relay OFF via ESP32"""
        command = f"operate-relay{relay_num}_off"
        response = self._send_command(command)
        print(f"[ESP32] Relay {relay_num} turned OFF")
        return response
    
    def read_distance(self, sensor_num=1):
        """Read distance from ultrasonic sensor via ESP32"""
        command = f"get-distance{sensor_num}"
        response = self._send_command(command)
        
        # Parse response: "Distance 1: 45 cm"
        if response:
            try:
                # Extract number from response
                parts = response.split(":")
                if len(parts) > 1:
                    distance_str = parts[1].strip().split()[0]  # Get first number
                    return float(distance_str)
            except Exception as e:
                print(f"[ESP32] Error parsing distance response: {e}")
        
        return 0.0
    
    def get_tank_level_percentage(self, sensor_num=1):
        """Get tank level as percentage via ESP32"""
        command = "get-level" if sensor_num == 1 else f"get-distance{sensor_num}"
        response = self._send_command(command)
        
        # Parse response: "Percentage: 75.5 %"
        if response:
            try:
                if "Percentage:" in response:
                    parts = response.split("Percentage:")
                    if len(parts) > 1:
                        percentage_str = parts[1].strip().split()[0]
                        return float(percentage_str)
                else:
                    # Calculate from distance
                    distance = self.read_distance(sensor_num)
                    container_height = 100.0  # cm (from PINS_CONFIG)
                    percentage = ((container_height - distance) / container_height) * 100
                    return max(0, min(100, percentage))
            except Exception as e:
                print(f"[ESP32] Error parsing level response: {e}")
        
        return 0.0
    
    def buzzer_on(self):
        """Turn buzzer ON via ESP32"""
        response = self._send_command("buzzer-on")
        print("[ESP32] Buzzer turned ON")
        return response
    
    def buzzer_off(self):
        """Turn buzzer OFF via ESP32"""
        response = self._send_command("buzzer-off")
        print("[ESP32] Buzzer turned OFF")
        return response
    
    def buzzer_beep(self, duration=0.5):
        """Beep buzzer via ESP32"""
        self.buzzer_on()
        time.sleep(duration)
        self.buzzer_off()
        print(f"[ESP32] Buzzer beeped for {duration}s")
    
    def set_led(self, led_name, state):
        """LEDs are not available - ESP32 firmware has them removed"""
        print(f"[ESP32] LED functionality not available (removed from ESP32 firmware)")
        pass
    
    def read_button(self, button_name):
        """Buttons are not available - ESP32 firmware has them removed"""
        print(f"[ESP32] Button functionality not available (removed from ESP32 firmware)")
        return False
    
    def check_weather(self):
        """Check weather via ESP32"""
        response = self._send_command("check-weather")
        print(f"[ESP32] Weather check: {response}")
        return response
    
    def send_sms(self, number, message):
        """Send SMS via ESP32 GSM module"""
        # Note: This requires extending ESP32 firmware to accept SMS parameters
        # For now, use the basic command
        response = self._send_command("send-sms")
        print(f"[ESP32] SMS command sent")
        return response
    
    def send_sms_to_all(self, message):
        """Send SMS to all recipients via ESP32"""
        response = self._send_command("send-sms-to-all")
        print(f"[ESP32] SMS sent to all recipients")
        return response
    
    def sync_recipients(self, recipients_list):
        """Sync recipients list to ESP32"""
        if not self.connected:
            print("[ESP32] Not connected. Cannot sync recipients.")
            return False
        
        try:
            # Clear existing recipients on ESP32
            self._send_command("clear-recipients")
            time.sleep(0.2)
            
            # Add each recipient
            for recipient in recipients_list:
                phone = recipient.get('phone', '')
                if phone:
                    self._send_command(f"add-recipient_{phone}")
                    time.sleep(0.1)
            
            print(f"[ESP32] Synced {len(recipients_list)} recipients to ESP32")
            return True
        except Exception as e:
            print(f"[ESP32] Error syncing recipients: {e}")
            return False
    
        response = self._send_command("wifi-reset")
        print("[ESP32] WiFi reset command sent")
        return response
    
    def cleanup(self):
        """Close serial connection"""
        if self.serial_connection and self.connected:
            self.serial_connection.close()
            print("[ESP32] Serial connection closed")
        self.connected = False

