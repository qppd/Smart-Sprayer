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
import sys
import os
from hardware.hardware_interface import HardwareInterface

# Import container configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PINS_CONFIG import CONTAINER_EMPTY_DISTANCE, CONTAINER_FULL_DISTANCE, CONTAINER_CAPACITY_LITERS

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
        
        # Parse response: "Distance 1: 45 cm" or "[SR04] ... Dist=45cm ..."
        if response:
            try:
                # Filter out command echoes and acknowledgments
                lines = [line for line in response.split('\n') if line and 
                        not line.startswith('get-') and 
                        not line.startswith('[CMD]')]
                if not lines:
                    return 0.0
                
                response = ' '.join(lines)
                
                # Try to extract distance from various formats
                # Format 1: "Distance 1: 45 cm"
                if ":" in response:
                    parts = response.split(":")
                    if len(parts) > 1:
                        distance_str = parts[1].strip().split()[0]
                        return float(distance_str)
                
                # Format 2: "Dist=45cm"
                if "Dist=" in response:
                    parts = response.split("Dist=")
                    if len(parts) > 1:
                        distance_str = parts[1].split()[0].replace("cm", "")
                        return float(distance_str)
            except Exception as e:
                print(f"[ESP32] Error parsing distance response: {e}")
                print(f"[ESP32] Response was: {response}")
        
        return 0.0
    
    def get_tank_level_percentage(self, sensor_num=1):
        """Get tank level as percentage via ESP32
        
        Tank configuration (from PINS_CONFIG.py):
        - 22cm distance = 100% FULL (liquid close to sensor, 16L)
        - 50cm distance = 0% EMPTY (liquid far from sensor, 0L)
        """
        command = "get-level" if sensor_num == 1 else f"get-distance{sensor_num}"
        response = self._send_command(command)
        
        if response:
            try:
                # Filter out command echoes and acknowledgments
                lines = [line for line in response.split('\n') if line and 
                        not line.startswith('get-') and 
                        not line.startswith('[CMD]')]
                if not lines:
                    return 0.0
                
                response = ' '.join(lines)
                
                # Try to parse percentage from response (ESP32 calculates it)
                if "%" in response:
                    # Extract percentage value from various formats
                    # Format 1: "(85.0%)" or "85.0%"
                    for part in response.split():
                        if "%" in part:
                            percentage_str = part.replace("(", "").replace(")", "").replace("%", "")
                            # Handle "Tank1=100.00%" format
                            if "=" in percentage_str:
                                percentage_str = percentage_str.split("=")[1]
                            
                            # Check if reading is INVALID before converting to float
                            if percentage_str == "INVALID" or percentage_str.upper() == "INVALID":
                                return None  # Return None to keep previous value displayed
                            
                            percentage = float(percentage_str)
                            
                            # Filter out invalid readings (-1.0 from ESP32)
                            if percentage < 0:
                                return None  # Return None to keep previous value displayed
                            
                            return max(0.0, min(100.0, percentage))
                
                # Fallback: calculate from distance if percentage not found
                distance = self.read_distance(sensor_num)
                if distance > 0:
                    # Use configured values from PINS_CONFIG.py
                    # Smaller distance = more full (liquid closer to sensor)
                    if distance <= CONTAINER_FULL_DISTANCE:
                        return 100.0
                    elif distance >= CONTAINER_EMPTY_DISTANCE:
                        return 0.0
                    else:
                        # Interpolate between 22cm (100%) and 50cm (0%)
                        percentage = ((CONTAINER_EMPTY_DISTANCE - distance) / (CONTAINER_EMPTY_DISTANCE - CONTAINER_FULL_DISTANCE)) * 100
                        return max(0.0, min(100.0, percentage))
            except Exception as e:
                print(f"[ESP32] Error parsing level response: {e}")
                print(f"[ESP32] Response was: {response}")
        
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
    
    def sync_time(self, dt=None):
        """Sync RPI time to ESP32 RTC
        
        Args:
            dt: datetime object to sync. If None, uses current time.
        """
        if not self.connected:
            print("[ESP32] Not connected. Cannot sync time.")
            return False
        
        from datetime import datetime
        if dt is None:
            dt = datetime.now()
        
        # Format: sync-time_YY_MM_DD_HH_MM_SS
        command = f"sync-time_{dt.year % 100}_{dt.month}_{dt.day}_{dt.hour}_{dt.minute}_{dt.second}"
        response = self._send_command(command)
        print(f"[ESP32] Time synced: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        return response
    
    def get_status(self):
        """Get complete ESP32 status including time, tank levels, recipient count"""
        response = self._send_command("get-status")
        
        if response:
            print(f"[ESP32] Status: {response}")
            # Parse response: [STATUS] Time=2026/01/20 15:30:45 Tank1=85.0% Tank2=90.0% Recipients=3
            status = {}
            if "[STATUS]" in response:
                try:
                    parts = response.split("[STATUS]")[1].strip().split()
                    for part in parts:
                        if "=" in part:
                            key, value = part.split("=", 1)
                            status[key] = value
                except Exception as e:
                    print(f"[ESP32] Error parsing status: {e}")
            return status
        return None
    
    def get_both_tank_levels(self):
        """Get both tank levels as percentages
        
        Returns dict with tank levels. Keys only present if valid reading obtained.
        If a tank has INVALID reading, its key won't be in the returned dict,
        allowing UI to keep displaying the previous value.
        """
        response = self._send_command("get-levels")
        
        levels = {}  # Don't initialize with default values
        if response:
            try:
                # Filter out command echoes and acknowledgments
                lines = [line for line in response.split('\n') if line and 
                        not line.startswith('get-') and 
                        not line.startswith('[CMD]')]
                if not lines:
                    return levels
                
                response = ' '.join(lines)
                
                # Parse: [LEVELS] Tank1=85.0% Tank2=90.0% or Tank1=INVALID Tank2=INVALID
                if "[LEVELS]" in response:
                    parts = response.split("[LEVELS]")[1].strip().split()
                    for part in parts:
                        if "Tank1=" in part:
                            value_str = part.split("=")[1].replace("%", "")
                            # Check if reading is INVALID before converting to float
                            if value_str.upper() != "INVALID":
                                try:
                                    levels['tank1'] = float(value_str)
                                except ValueError:
                                    pass  # Skip invalid values, keep previous display
                            # If INVALID: don't set the key, caller will keep previous value
                        elif "Tank2=" in part:
                            value_str = part.split("=")[1].replace("%", "")
                            # Check if reading is INVALID before converting to float
                            if value_str.upper() != "INVALID":
                                try:
                                    levels['tank2'] = float(value_str)
                                except ValueError:
                                    pass  # Skip invalid values, keep previous display
                            # If INVALID: don't set the key, caller will keep previous value
            except Exception as e:
                print(f"[ESP32] Error parsing tank levels: {e}")
                print(f"[ESP32] Response was: {response}")
        
        return levels
    
    def spray(self, relay_num, duration_seconds, volume_ml):
        """Execute spray operation on ESP32
        
        Args:
            relay_num: Which relay to use (1 or 2)
            duration_seconds: How long to spray in seconds
            volume_ml: Volume being sprayed in mL (for logging/SMS)
        
        Returns:
            Response from ESP32
        """
        if not self.connected:
            print("[ESP32] Not connected. Cannot execute spray.")
            return None
        
        command = f"spray_{relay_num}_{int(duration_seconds)}_{int(volume_ml)}"
        response = self._send_command(command)
        
        print(f"[ESP32] Spray executed: Relay {relay_num}, {duration_seconds}s, {volume_ml}mL")
        return response
    
    def sync_recipients_bulk(self, phone_numbers):
        """Sync all recipients to ESP32 in one command
        
        Args:
            phone_numbers: List of phone number strings
        """
        if not self.connected:
            print("[ESP32] Not connected. Cannot sync recipients.")
            return False
        
        if not phone_numbers:
            # Just clear recipients if empty list
            response = self._send_command("clear-recipients")
            return True
        
        # Format: sync-recipients_+639123456789,+639987654321
        numbers_str = ",".join(phone_numbers)
        command = f"sync-recipients_{numbers_str}"
        response = self._send_command(command)
        
        print(f"[ESP32] Bulk synced {len(phone_numbers)} recipients")
        return response

        if self.serial_connection and self.connected:
            self.serial_connection.close()
            print("[ESP32] Serial connection closed")
        self.connected = False

