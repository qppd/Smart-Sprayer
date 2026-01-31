# RPI to ESP32 Communication Architecture

## Overview
The Raspberry Pi Smart Sprayer system has been refactored to communicate with ESP32 for all hardware operations. The RPI now serves as a GUI interface and controller, while ESP32 handles all physical hardware components.

## Architecture Changes

### Previous Architecture
- RPI directly controlled GPIO pins for buttons, LEDs, LCD, buzzer, relays, sensors
- Hardware-specific configuration files for each component
- Direct RPi.GPIO usage throughout the codebase

### New Architecture
- **RPI Role**: GUI interface, scheduling logic, data management
- **ESP32 Role**: All hardware control (relays, sensors, buzzer, GSM, WiFi, etc.)
- **Communication**: Serial UART communication between RPI and ESP32
- **Hardware Abstraction**: `hardware_interface.py` with pluggable implementations

## File Structure

### Removed Files
The following hardware-specific CONFIG files have been removed as ESP32 handles these:
- `BUTTON_CONFIG.py` - Button handling (removed from ESP32)
- `LED_CONFIG.py` - LED control (removed from ESP32)
- `LCD_CONFIG.py` - LCD display (removed from ESP32)
- `BUZZER_CONFIG.py` - Buzzer control (now via ESP32)
- `GSM_CONFIG.py` - GSM communication (now via ESP32)
- `RELAY_CONFIG.py` - Relay control (now via ESP32)
- `RTC_CONFIG.py` - RTC operations (now via ESP32)
- `SR04_CONFIG.py` - Ultrasonic sensors (now via ESP32)
- `NTP_CONFIG.py` - NTP time sync (now via ESP32)
- `GSM_RECIPIENTS.py` - SMS recipients (now via ESP32)
- `FIREBASE_CONFIG.py` - Firebase functions (not used in current implementation)
- `WEATHER_CONFIG.py` - Weather API functions (ESP32 handles weather checks)
- `WIFI_CONFIG.py` - WiFi functions (ESP32 handles WiFi)
- `mock_hardware.py` - Mock hardware for PC testing (no longer needed)
- `.idea/` - IDE configuration folder (added to .gitignore)

### Kept Files
- `PINS_CONFIG.py` - Reference only (describes ESP32 pin assignments and container height)

### New Files
- `hardware/esp32_hardware.py` - ESP32 USB serial communication implementation
  
### Modified Files
- `hardware/hardware_interface.py` - Simplified to only support ESP32 mode
- `SmartSprayer.py` - Simplified to CLI stub, removed unused imports
- `requirements.txt` - Added pyserial for ESP32 communication
- `.gitignore` - Added Python, IDE, and OS-specific entries

## Hardware Interface

The system uses `hardware_interface.py` with ESP32 serial communication:

### ESP32 Communication Mode
- Uses `ESP32Hardware` class
- Communicates with ESP32 via USB serial port
- Sends text commands, parses responses
- Default serial port: `/dev/ttyUSB0` (Raspberry Pi/Linux)
- Common ports:
  - Linux/Raspberry Pi: `/dev/ttyUSB0`, `/dev/ttyACM0`
  - Windows: `COM3`, `COM4`, `COM5`
  - macOS: `/dev/cu.usbserial-XXXX`
- Baudrate: 9600 (matches ESP32 configuration)

## ESP32 Serial Commands

The RPI sends these commands to ESP32:

### Relay Control
- `operate-relay1_on` - Turn relay 1 ON
- `operate-relay1_off` - Turn relay 1 OFF
- `operate-relay2_on` - Turn relay 2 ON
- `operate-relay2_off` - Turn relay 2 OFF

### Sensor Reading
- `get-distance1` - Read ultrasonic sensor 1 (returns distance in cm)
- `get-distance2` - Read ultrasonic sensor 2 (returns distance in cm)
- `get-level` - Get full level information (distance, filled level, percentage)

### Buzzer
- `buzzer-on` - Turn buzzer ON
- `buzzer-off` - Turn buzzer OFF
- `buzzer-beep` - Single beep

### Weather & Network
- `check-weather` - Check weather forecast for rain
- `check-network` - Check GSM network status
- `wifi-reset` - Reset WiFi settings

### Messaging
- `send-sms` - Send test SMS
- `send-sms-to-all` - Send SMS to all configured recipients

### Time
- `get-time` - Get current RTC time
- `get-timestamp` - Get NTP timestamp
- `check-ntp` - Check if NTP is synced
- `update-ntp` - Update NTP time

## Usage

### Connecting ESP32

1. Connect ESP32 to Raspberry Pi via USB cable
2. Verify the serial port:
   ```bash
   # On Raspberry Pi/Linux
   ls /dev/ttyUSB* /dev/ttyACM*
   # Common ports: /dev/ttyUSB0 or /dev/ttyACM0
   ```
3. Grant serial port permissions (if needed):
   ```bash
   sudo usermod -a -G dialout $USER
   # Then logout and login again
   ```

### Running the GUI

```bash
# Ensure ESP32 is connected to serial port
# Default: /dev/ttyUSB0

# Run the GUI application
python run_gui.py
```

### Configuring Serial Port

If your ESP32 is on a different serial port, you can configure it when getting hardware:

```python
from hardware.hardware_interface import get_hardware

# Default usage (uses /dev/ttyUSB0)
hardware = get_hardware()

# Custom serial port
hardware = get_hardware(port='/dev/ttyACM0', baudrate=9600, timeout=1)

# Windows example
hardware = get_hardware(port='COM3', baudrate=9600, timeout=1)
```

## Core Files Structure

```
SmartSprayer/
├── run_gui.py                    # Main GUI launcher
├── SmartSprayer.py               # Deprecated CLI (use run_gui.py instead)
├── PINS_CONFIG.py                # Pin reference (for ESP32)
├── requirements.txt              # Python dependencies
├── RPI_ESP32_ARCHITECTURE.md     # This documentation
├── hardware/
│   ├── __init__.py
│   ├── hardware_interface.py     # Hardware abstraction layer
│   └── esp32_hardware.py         # ESP32 USB serial communication
├── core/
│   ├── __init__.py
│   ├── data_store.py             # JSON data storage
│   ├── logger.py                 # Logging system
│   ├── scheduler.py              # Spray scheduling
│   └── reschedule_logic.py       # Reschedule logic
├── ui/
│   ├── __init__.py
│   ├── main_ui.py                # Main GUI window
│   ├── dashboard.py              # Dashboard panel
│   ├── scheduling.py             # Scheduling panel
│   ├── previous_data.py          # History panel
│   ├── notifications.py          # Notifications panel
│   └── spraying_events_logs_viewer.py  # Logs panel
├── data/
│   ├── schedules.json            # Spray schedules
│   └── history.json              # Spray history
└── logs/
    └── smart_sprayer.log         # Application logs
```

## GUI Features Preserved

All GUI functionality remains intact:
- ✅ Dashboard with tank level monitoring
- ✅ Spray scheduling system
- ✅ Previous spray history
- ✅ Logs viewer
- ✅ Notifications panel
- ✅ Manual spray control

## Components Removed from RPI

The following components are NO LONGER directly controlled by RPI:
- ❌ Physical buttons (removed from ESP32 firmware)
- ❌ LCD display (removed from ESP32 firmware)
- ❌ Status LEDs (removed from ESP32 firmware)
- ❌ Direct GPIO access for hardware

## Benefits of New Architecture

1. **Direct Communication**: RPI talks directly to ESP32 via serial
2. **Separation of Concerns**: RPI handles UI/logic, ESP32 handles hardware
3. **Better Reliability**: ESP32 is purpose-built for real-time hardware control
4. **Simplified RPI Code**: No GPIO dependencies, cleaner codebase
5. **Easy Configuration**: Serial port and baudrate easily configurable
6. **Safety**: Hardware abstraction prevents direct GPIO conflicts

## Migration Notes

- Old `SmartSprayer.py` CLI is deprecated - use `run_gui.py` instead
- All hardware operations now go through `hardware_interface`
- UI code unchanged - uses hardware interface as before
- No RPi.GPIO dependency in production (serial communication only)

## Future Enhancements

Potential improvements:
- Bi-directional communication protocol with acknowledgments
- Binary protocol for faster communication
- Watchdog/heartbeat between RPI and ESP32
- Error recovery and reconnection logic
- Configuration sync between RPI and ESP32
