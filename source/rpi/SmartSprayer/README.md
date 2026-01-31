# Smart Sprayer - Raspberry Pi GUI Application

## Overview

This is the Raspberry Pi GUI application for the Smart Sprayer system. The RPI communicates with ESP32 via USB serial for all hardware operations.

## System Architecture

- **Raspberry Pi**: GUI interface, scheduling logic, data management
- **ESP32**: All hardware control (relays, sensors, buzzer, GSM, WiFi, etc.)
- **Communication**: USB serial (9600 baud)

## Quick Start

### 1. Hardware Setup

1. Connect ESP32 to Raspberry Pi via USB cable
2. Verify ESP32 is detected:
   ```bash
   ls /dev/ttyUSB* /dev/ttyACM*
   ```
3. Grant serial port permissions:
   ```bash
   sudo usermod -a -G dialout $USER
   # Logout and login again
   ```

### 2. Software Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Verify installation:
   ```bash
   python -c "import customtkinter, serial; print('Dependencies OK')"
   ```

### 3. Running the Application

```bash
python run_gui.py
```

## Features

### Dashboard
- Real-time tank level monitoring (2 containers)
- System status display
- Current schedule overview

### Spray Scheduling
- Create automated spray schedules
- Set date, time, duration, and pump selection
- Enable/disable schedules
- Weather-based automatic rescheduling

### Previous Data
- View spray history
- Filter by date range
- Export data to CSV
- Statistics and analytics

### Spraying Events Logs
- Real-time log viewer
- Filter by log level (INFO, WARNING, ERROR)
- Auto-refresh
- Clear logs functionality

### Notifications
- Low water alerts
- Schedule reminders
- System status notifications

## Configuration

### Serial Port Configuration

If your ESP32 is on a different port, edit `hardware/hardware_interface.py`:

```python
def get_hardware(port='/dev/ttyUSB0', baudrate=9600, timeout=1):
```

Common ports:
- Raspberry Pi: `/dev/ttyUSB0` or `/dev/ttyACM0`
- Windows: `COM3`, `COM4`, etc.
- macOS: `/dev/cu.usbserial-XXXX`

### Container Height

Edit `PINS_CONFIG.py`:

```python
CONTAINER_HEIGHT = 100.0  # cm
```

## File Structure

```
SmartSprayer/
├── run_gui.py                    # Main application launcher
├── requirements.txt              # Python dependencies
├── PINS_CONFIG.py                # Configuration
├── hardware/                     # Hardware abstraction
│   ├── hardware_interface.py     # Base interface
│   └── esp32_hardware.py         # ESP32 serial communication
├── core/                         # Core logic
│   ├── data_store.py             # Data persistence
│   ├── logger.py                 # Logging system
│   ├── scheduler.py              # Scheduling engine
│   └── reschedule_logic.py       # Weather-based rescheduling
├── ui/                           # GUI components
│   ├── main_ui.py                # Main window
│   ├── dashboard.py              # Dashboard panel
│   ├── scheduling.py             # Scheduling panel
│   ├── previous_data.py          # History viewer
│   ├── notifications.py          # Notifications
│   └── spraying_events_logs_viewer.py  # Log viewer
├── data/                         # Application data
│   ├── schedules.json            # Spray schedules
│   └── history.json              # Spray history
└── logs/                         # Log files
    └── smart_sprayer.log         # Application logs
```

## ESP32 Commands

The RPI sends these serial commands to ESP32:

### Hardware Control
- `operate-relay1_on` / `operate-relay1_off` - Control pump 1
- `operate-relay2_on` / `operate-relay2_off` - Control pump 2
- `buzzer-on` / `buzzer-off` / `buzzer-beep` - Buzzer control

### Sensor Reading
- `get-distance1` - Read tank 1 level
- `get-distance2` - Read tank 2 level
- `get-level` - Get full level information

### System Functions
- `check-weather` - Check weather forecast
- `check-network` - Check GSM network status
- `get-time` - Get current time from ESP32

## Troubleshooting

### Serial Port Issues

**Problem**: Cannot connect to ESP32

**Solutions**:
1. Check USB connection
2. Verify correct port: `ls /dev/ttyUSB* /dev/ttyACM*`
3. Check permissions: `sudo usermod -a -G dialout $USER`
4. Try different USB cable or port
5. Check ESP32 is powered on and running firmware

### GUI Issues

**Problem**: GUI won't start

**Solutions**:
1. Install dependencies: `pip install -r requirements.txt`
2. Check Python version: `python --version` (3.8+ required)
3. Check display: `echo $DISPLAY`
4. For headless Raspberry Pi, enable VNC or use X11 forwarding

### Data Issues

**Problem**: Schedules or history not saving

**Solutions**:
1. Check `data/` directory exists
2. Check file permissions: `ls -la data/`
3. Check disk space: `df -h`

## Development

### Testing without ESP32

The system requires ESP32 hardware. For development without hardware:
1. Modify ESP32 connection timeout
2. Use the serial port simulator for testing

### Debug Mode

Enable debug logging in `core/logger.py`:

```python
logger.setLevel(logging.DEBUG)
```

## Documentation

- [RPI_ESP32_ARCHITECTURE.md](RPI_ESP32_ARCHITECTURE.md) - Detailed architecture documentation
- ESP32 firmware repository - For ESP32 code and configuration

## License

See main project LICENSE file.

## Support

For issues and questions, please refer to the main project repository.
