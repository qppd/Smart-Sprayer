# esp32_hardware.py
# Hardware implementation that communicates with ESP32 via USB serial
# ESP32 handles all physical hardware components
#
# Serial transport is managed by hardware.esp32_connection.ESP32Connection
# which handles auto-detection, auto-reconnect, and port persistence.

import serial
import time
import threading
import sys
import os
from hardware.hardware_interface import HardwareInterface
from hardware.esp32_connection import (
    ESP32Connection,
    STATE_CONNECTED,
    _list_serial_ports,
)

# Import container configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PINS_CONFIG import CONTAINER_EMPTY_DISTANCE, CONTAINER_FULL_DISTANCE, CONTAINER_CAPACITY_LITERS

# ============================================
# FRAMED PROTOCOL FUNCTIONS
# ============================================

def calculate_checksum(data: str) -> int:
    """Calculate XOR checksum for framed protocol"""
    checksum = 0
    for char in data:
        checksum ^= ord(char)
    return checksum

def validate_frame(frame: str) -> tuple:
    """
    Validate and parse framed response
    Returns: (valid, command, data_dict)
    """
    if not frame or not frame.startswith('<') or not frame.endswith('>'):
        return (False, None, None)
    
    # Remove < and >
    content = frame[1:-1]
    
    # Split by colons
    parts = content.split(':')
    if len(parts) != 3:
        return (False, None, None)
    
    command, data, checksum_str = parts
    
    # Validate checksum
    try:
        received_checksum = int(checksum_str, 16)
        payload = f"{command}:{data}"
        calculated_checksum = calculate_checksum(payload)
        
        if received_checksum != calculated_checksum:
            print(f"[FRAME ERROR] Checksum mismatch: expected {calculated_checksum:X}, got {received_checksum:X}")
            return (False, None, None)
    except ValueError:
        print(f"[FRAME ERROR] Invalid checksum format: {checksum_str}")
        return (False, None, None)
    
    # Parse data based on command
    if command == "LEVELS":
        # Format: dist1,pct1,dist2,pct2
        data_parts = data.split(',')
        if len(data_parts) == 4:
            try:
                data_dict = {
                    'dist1': int(data_parts[0]),
                    'pct1': float(data_parts[1]),
                    'dist2': int(data_parts[2]),
                    'pct2': float(data_parts[3])
                }
                return (True, command, data_dict)
            except ValueError as e:
                print(f"[FRAME ERROR] Failed to parse LEVELS data: {e}")
                return (False, None, None)
    
    return (False, None, None)

class ESP32Hardware(HardwareInterface):
    """Hardware implementation that communicates with ESP32 via USB serial.

    Serial transport is delegated to ESP32Connection which handles:
    - Auto-detection of available USB ports
    - Persistent last-port preference
    - Background auto-reconnect
    """

    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        super().__init__()
        self.baudrate = baudrate
        self.timeout  = timeout
        self.use_framed_protocol = True

        # Build connection manager; seed with the caller-supplied port hint
        self._conn = ESP32Connection(
            baudrate=baudrate,
            timeout=float(timeout),
        )
        if port and port != '/dev/ttyUSB0':
            # Honour an explicitly supplied port override
            self._conn.LAST_CONNECTED_PORT = port

        # Start background auto-connect + monitor loop
        self._conn.start()

        # Convenience aliases kept for callers that access them directly
        # (e.g. settings UI probing hardware.connected / hardware.port)

    # ── compatibility shims ──────────────────────────────────────────────
    @property
    def connected(self) -> bool:
        return self._conn.is_connected

    @property
    def port(self) -> str | None:
        return self._conn.port

    @property
    def serial_connection(self):
        """Direct access to the underlying serial.Serial (may be None)."""
        return self._conn.serial_connection

    # ── internal ─────────────────────────────────────────────────────────
    def _connect(self):
        """Legacy method: delegate to connection manager."""
        self._conn.reconnect()
    
    def _send_command(self, command):
        """Send command to ESP32 and return response."""
        if not self.connected:
            print(f"[ESP32] Not connected. Command '{command}' not sent.")
            return None

        try:
            with self._conn._lock:
                ser = self._conn.serial_connection
                if not ser:
                    return None
                ser.write(f"{command}\n".encode())
                response_lines = []
                deadline = time.monotonic() + max(0.5, float(self.timeout))
                last_data_time = None
                idle_grace_seconds = 0.15

                while time.monotonic() < deadline:
                    if ser.in_waiting > 0:
                        raw = ser.readline().decode('utf-8', errors='ignore').strip()
                        if raw:
                            response_lines.append(raw)
                            last_data_time = time.monotonic()
                        continue

                    if response_lines and last_data_time is not None:
                        if (time.monotonic() - last_data_time) >= idle_grace_seconds:
                            break

                    time.sleep(0.01)

            response = "\n".join(response_lines).strip() if response_lines else None

            if any(cmd in command for cmd in ['get-status']) and not command.startswith('<'):
                print(f"[ESP32 DEBUG] Command: '{command}' -> Response: '{response}'")

            return response
        except serial.SerialException as e:
            print(f"[ESP32] Serial error on command '{command}': {e}")
            self._conn._handle_disconnect(str(e))
            return None
        except Exception as e:
            print(f"[ESP32] Error sending command '{command}': {e}")
            return None
    
    def _send_framed_command(self, command: str, data: str = "") -> str:
        """Send framed command with checksum and return response."""
        if not self.connected:
            print(f"[ESP32] Not connected. Framed command '{command}' not sent.")
            return None

        try:
            # Build frame
            payload = f"{command}:{data}"
            checksum = calculate_checksum(payload)
            frame = f"<{payload}:{checksum:X}>"
            
            # Send frame
            with self._conn._lock:
                ser = self._conn.serial_connection
                if not ser:
                    return None
                ser.write(f"{frame}\n".encode())

                # Read framed response with SHORT timeout (UI-friendly)
                # Reduced from 1 second to 0.15 seconds to prevent UI lag
                deadline = time.monotonic() + 0.15

                while time.monotonic() < deadline:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line.startswith('<') and line.endswith('>'):
                            return line
                    time.sleep(0.01)

            return None
        except serial.SerialException as e:
            print(f"[ESP32] Serial error on framed command '{command}': {e}")
            self._conn._handle_disconnect(str(e))
            return None
        except Exception as e:
            print(f"[ESP32] Error sending framed command '{command}': {e}")
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
        - 40cm distance = 0% EMPTY (liquid far from sensor, 0L)
        """
        # Use get-levels so parsing is consistent for both tanks.
        # This also avoids accidentally grabbing Tank2's percentage when Tank1 is INVALID.
        levels = self.get_both_tank_levels()

        key = 'tank1' if sensor_num == 1 else 'tank2'
        if key in levels:
            return levels[key]
        return None
    
    def get_tank1_level(self):
        """Get tank 1 level as percentage"""
        return self.get_tank_level_percentage(1)
    
    def get_tank2_level(self):
        """Get tank 2 level as percentage"""
        return self.get_tank_level_percentage(2)
    
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
        """Send SMS via ESP32 GSM module using send-sms-custom command"""
        if not self.connected:
            print("[ESP32] Not connected. Cannot send SMS.")
            return None
        # Use the custom SMS command: send-sms-custom_{number}_{message}
        command = f"send-sms-custom_{number}_{message}"
        response = self._send_command(command)
        print(f"[ESP32] SMS sent to {number}")
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
                    print(f"[RPI DEBUG] get_status: Parsing parts: {parts}")
                    for part in parts:
                        if "=" in part:
                            key, value = part.split("=", 1)
                            status[key] = value
                            print(f"[RPI DEBUG] get_status: {key} = {value}")
                except Exception as e:
                    print(f"[ESP32] Error parsing status: {e}")
            return status
        return None
    
    def get_both_tank_levels(self):
        """Get both tank levels as percentages
        
        Uses framed protocol (GET_LEVELS) with fallback to old protocol.
        Returns dict with tank levels. Keys only present if valid reading obtained.
        If a tank has INVALID reading, its key won't be in the returned dict,
        allowing UI to keep displaying the previous value.
        """
        levels = {}  # Don't initialize with default values
        
        # Try framed protocol first (but only once - if it fails, disable it)
        if self.use_framed_protocol:
            response = self._send_framed_command("GET_LEVELS")
            
            if response:
                valid, command, data = validate_frame(response)
                
                if valid and command == "LEVELS":
                    # Successfully got framed response
                    # data = {'dist1': int, 'pct1': float, 'dist2': int, 'pct2': float}
                    
                    # Only add keys for valid readings (pct >= 0)
                    if data['pct1'] >= 0:
                        levels['tank1'] = max(0.0, min(100.0, data['pct1']))
                        # print(f"[FRAME] Tank1: {data['dist1']}cm = {levels['tank1']:.1f}%")
                    else:
                        # print(f"[FRAME] Tank1: INVALID ({data['dist1']}cm)")
                        pass
                    
                    if data['pct2'] >= 0:
                        levels['tank2'] = max(0.0, min(100.0, data['pct2']))
                        # print(f"[FRAME] Tank2: {data['dist2']}cm = {levels['tank2']:.1f}%")
                    else:
                        # print(f"[FRAME] Tank2: INVALID ({data['dist2']}cm)")
                        pass
                    
                    return levels
                else:
                    # Framed protocol failed, permanently disable it to avoid future timeouts
                    print("[FRAME] ESP32 not responding to framed protocol - disabling for this session")
                    self.use_framed_protocol = False
        
        # Fallback to old protocol
        response = self._send_command("get-levels")
        
        if response:
            try:
                # Filter out command echoes and acknowledgments
                lines = [line for line in response.split('\n') if line and 
                        not line.startswith('get-') and 
                        not line.startswith('[CMD]')]
                if not lines:
                    # print(f"[RPI DEBUG] get_both_tank_levels: No valid lines after filtering")
                    pass
                
                response = ' '.join(lines)
                # print(f"[RPI DEBUG] get_both_tank_levels: Filtered response: '{response}'")

                # Parse: can be either tagged ([LEVELS] Tank1=.. Tank2=..) or untagged (debug output still contains Tank1=/Tank2=)
                parse_text = response
                if "[LEVELS]" in response:
                    parse_text = response.split("[LEVELS]", 1)[1].strip()

                parts = parse_text.split()
                # print(f"[RPI DEBUG] get_both_tank_levels: Parsing parts: {parts}")
                for part in parts:
                    if "Tank1=" in part:
                        value_str = part.split("=", 1)[1].replace("%", "")
                        # print(f"[RPI DEBUG] get_both_tank_levels: Tank1 value_str: '{value_str}'")
                        if value_str.upper() == "INVALID":
                            # print(f"[RPI DEBUG] get_both_tank_levels: Tank1 is INVALID, not setting key")
                            continue
                        try:
                            value = float(value_str)
                        except ValueError:
                            # print(f"[RPI DEBUG] get_both_tank_levels: Tank1 ValueError for '{value_str}'")
                            continue
                        if value < 0:
                            # print(f"[RPI DEBUG] get_both_tank_levels: Tank1 negative ({value}), not setting key")
                            continue
                        levels['tank1'] = max(0.0, min(100.0, value))
                        # print(f"[RPI DEBUG] get_both_tank_levels: Tank1 set to: {levels['tank1']}%")

                    elif "Tank2=" in part:
                        value_str = part.split("=", 1)[1].replace("%", "")
                        # print(f"[RPI DEBUG] get_both_tank_levels: Tank2 value_str: '{value_str}'")
                        if value_str.upper() == "INVALID":
                            # print(f"[RPI DEBUG] get_both_tank_levels: Tank2 is INVALID, not setting key")
                            continue
                        try:
                            value = float(value_str)
                        except ValueError:
                            # print(f"[RPI DEBUG] get_both_tank_levels: Tank2 ValueError for '{value_str}'")
                            continue
                        if value < 0:
                            # print(f"[RPI DEBUG] get_both_tank_levels: Tank2 negative ({value}), not setting key")
                            continue
                        levels['tank2'] = max(0.0, min(100.0, value))
                        # print(f"[RPI DEBUG] get_both_tank_levels: Tank2 set to: {levels['tank2']}%")
                
                # print(f"[RPI DEBUG] get_both_tank_levels: Final levels dict: {levels}")
            except Exception as e:
                print(f"[ESP32] Error parsing tank levels: {e}")
                print(f"[ESP32] Response was: {response}")
        
        return levels
    
    def spray(self, relay_num, duration_seconds, volume_ml, spray_type='Unknown'):
        """Execute spray operation on ESP32
        
        Args:
            relay_num: Which relay to use (1 or 2)
            duration_seconds: How long to spray in seconds
            volume_ml: Volume being sprayed in mL (for logging/SMS)
            spray_type: Type of spray (Pesticide or Fertilizer) for SMS messages
        
        Returns:
            Response from ESP32
        """
        if not self.connected:
            print("[ESP32] Not connected. Cannot execute spray.")
            return None
        
        command = f"spray_{relay_num}_{int(duration_seconds)}_{int(volume_ml)}_{spray_type}"
        response = self._send_command(command)
        
        print(f"[ESP32] Spray executed: Relay {relay_num}, {duration_seconds}s, {volume_ml}mL, Type: {spray_type}")
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
    
    def cleanup(self):
        """Cleanup serial connection and stop background monitor."""
        self._conn.stop()
        print("[ESP32] Serial connection closed")

