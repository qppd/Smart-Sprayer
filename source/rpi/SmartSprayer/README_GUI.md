# Smart Sprayer GUI - README

## Overview
A beautiful, farmer-friendly GUI for the Smart Sprayer system built with CustomTkinter. This application provides comprehensive control over automated agricultural spraying operations.

## Features

### 1. Dashboard
- Real-time tank level monitoring (2 containers)
- System status display
- Next scheduled spray countdown
- Live date/time display

### 2. Scheduling
- **Date picker** with calendar popup
- **Time selection** (hour and minute)
- **Spray type** selection (Fertilizer/Pesticide)
- **Container selection** (Container 1/2)
- **Recurring schedules** with custom intervals
- **Reschedule functionality** (max 3 times)
- **Auto-adjust logic** for conflict resolution and interval preservation

### 3. Previous Data
- Complete spray history
- Filter by spray type
- Statistics (total, fertilizer, pesticide counts)
- Export functionality

### 4. Notifications & Status
- System status overview
- Tank level alerts
- Upcoming schedules list
- Recent activity feed

### 5. System Logs
- Real-time log viewing
- Auto-refresh option
- Log level filtering
- Color-coded entries
- Clear logs functionality

## Installation

### Requirements
- Python 3.8 or higher
- Windows (tested), Linux, or macOS

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install customtkinter tkcalendar requests
```

### Step 2: Run the Application
```bash
python run_gui.py
```

Or run directly:
```bash
python ui/main_ui.py
```

## Project Structure

```
SmartSprayer/
├── run_gui.py                 # Main launcher
├── requirements.txt           # Dependencies
├── SmartSprayer.py           # Original hardware code (preserved)
├── hardware/
│   ├── hardware_interface.py # Hardware abstraction
│   └── mock_hardware.py      # PC mock implementation
├── core/
│   ├── logger.py             # Logging system
│   ├── data_store.py         # Data persistence
│   ├── scheduler.py          # Main scheduler
│   └── reschedule_logic.py   # Reschedule & auto-adjust
├── ui/
│   ├── main_ui.py            # Main application
│   ├── dashboard.py          # Dashboard panel
│   ├── scheduling.py         # Scheduling panel
│   ├── previous_data.py      # History viewer
│   ├── notifications.py      # Notifications panel
│   └── logs_viewer.py        # Logs viewer
├── data/                      # JSON data storage
├── logs/                      # Log files
└── config files...           # Various hardware configs
```

## Usage Guide

### Creating a Schedule

1. Navigate to **Scheduling** panel
2. Click **"Pick Date"** and select a date from calendar
3. Set the **time** using dropdowns
4. Select **spray type** (Fertilizer/Pesticide)
5. Choose **container** (Container 1/2)
6. For recurring schedules:
   - Check **"Enable Recurring Schedule"**
   - Enter **interval** in days (e.g., 7 for weekly)
   - Enter **number of occurrences**
7. Click **"CREATE SCHEDULE"**

### Rescheduling

1. Find the schedule in the **Active Schedules** list
2. Click **"Reschedule"** button
3. Pick new date and time
4. Click **"Confirm Reschedule"**
5. System will automatically adjust conflicting schedules

**Important Rules:**
- Maximum **3 reschedules** per schedule
- On 4th cancellation → all related schedules cancelled
- Auto-adjust maintains interval consistency
- Conflicting dates are automatically resolved

### Monitoring

- **Dashboard**: View real-time tank levels and system status
- **Notifications**: Check upcoming schedules and recent activity
- **Previous Data**: Review completed spray history
- **Logs**: Monitor all system events

## Hardware Modes

### PC Mode (Current)
- Mock hardware simulation
- No GPIO required
- Perfect for development and testing
- Simulated tank levels with gradual changes

### Raspberry Pi Mode
To deploy on actual Raspberry Pi:

1. Install additional dependencies:
   ```bash
   pip install RPi.GPIO pyserial
   ```

2. Set `PC_MODE = False` in `hardware/hardware_interface.py`

3. Ensure proper wiring according to `PINS_CONFIG.py`:
   - Ultrasonic sensors on pins 6/13 and 19/26
   - Relays on pins 4 and 5
   - Buzzer on pin 12
   - LEDs on pins 20 and 21

## Scheduling Logic Details

### Auto-Adjust Examples

**Example 1: Conflict Resolution**
```
Before:
- Fertilizer: Jan 6
- Pesticide: Jan 7

Reschedule Fertilizer to Jan 7:

After:
- Fertilizer: Jan 7
- Pesticide: Jan 8 (auto-adjusted)
```

**Example 2: Interval Preservation**
```
Before:
- Fertilizer: Jan 6, Jan 12 (6-day interval)

Reschedule Jan 6 to Jan 7:

After:
- Fertilizer: Jan 7, Jan 13 (6-day interval maintained)
```

## Troubleshooting

### GUI doesn't start
- Ensure all dependencies are installed
- Check Python version (3.8+)
- Run from correct directory

### Mock hardware not updating
- Check if background threads are running
- Restart application

### Schedules not executing
- Verify system date/time is correct
- Check scheduler is started (Dashboard shows status)
- Review logs for errors

### Import errors
```bash
# Re-install dependencies
pip install --upgrade -r requirements.txt
```

## Configuration

### Tank Capacity
Edit `CONTAINER_HEIGHT` in `PINS_CONFIG.py` (default: 100cm)

### Spray Duration
Edit duration parameter when creating schedules (default: 30 seconds)

### Log Settings
Logs stored in `logs/smartsprayer.log`
Adjust retention in `core/logger.py`

## Data Storage

### Schedules
Stored in `data/schedules.json`

### History
Stored in `data/history.json`

### Export
Use "Export" button in Previous Data panel to save complete history

## Support

For issues or questions:
1. Check logs in System Logs panel
2. Review console output
3. Verify all files are present
4. Ensure dependencies are current

## License

See LICENSE file in project root.

## Credits

Developed for agricultural automation with focus on farmer-friendly interface and reliable operation.
