# Firebase Integration Guide

## Overview
The Smart Sprayer system now uses **Raspberry Pi** for all internet connectivity, including Firebase and Weather API. The ESP32 focuses solely on hardware control via serial communication.

## Architecture Changes

### ESP32 (Hardware Controller)
- **Removed**: WiFi, Firebase, NTP, Weather API
- **Retained**: GSM, Relay control, Ultrasonic sensors, Buzzer, RTC
- **Communication**: USB Serial with RPI
- **Purpose**: Execute hardware commands from RPI

### Raspberry Pi (System Controller & GUI)
- **Added**: Firebase integration via Pyrebase4
- **Added**: Weather API integration
- **Handles**: All internet connectivity, data storage, scheduling, GUI
- **Communication**: USB Serial with ESP32, Firebase cloud sync

## Setup Instructions

### 1. Install Dependencies

```bash
cd source/rpi/SmartSprayer
pip install -r requirements.txt
```

This will install:
- customtkinter (GUI)
- pyserial (ESP32 communication)
- Pyrebase4 (Firebase)
- requests (Weather API)

### 2. Firebase Configuration

#### Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing one
3. Enable **Realtime Database**
4. Enable **Authentication** (Email/Password)
5. Get your Firebase configuration

#### Configure Firebase Credentials
1. Copy the template:
   ```bash
   cp firebase_credentials_template.py firebase_credentials.py
   ```

2. Edit `firebase_credentials.py`:
   ```python
   FIREBASE_CONFIG = {
       "apiKey": "YOUR_API_KEY",
       "authDomain": "your-project.firebaseapp.com",
       "databaseURL": "https://your-project-default-rtdb.firebaseio.com",
       "storageBucket": "your-project.appspot.com"
   }
   
   FIREBASE_USER = {
       "email": "your-email@example.com",
       "password": "your-password"
   }
   ```

3. Create a user in Firebase Authentication with the email/password above

### 3. Weather API Configuration

#### Get Weather API Key
1. Sign up at [WeatherAPI.com](https://www.weatherapi.com/)
2. Get your free API key

#### Add to Firebase Credentials
Edit `firebase_credentials.py`:
```python
WEATHER_API_KEY = "your_weather_api_key"
WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json?key=your_weather_api_key&q=YourLocation&aqi=no"
```

Replace `YourLocation` with your location (e.g., "Manila", "14.5995,120.9842")

## Firebase Data Structure

The system stores data in Firebase Realtime Database:

```
smart-sprayer/
  devices/
    SmartSprayer_001/
      schedules/
        SCH_001/
          id: "SCH_001"
          date: "2026-02-01"
          time: "08:00"
          spray_type: "Fertilizer"
          container: "Container 1"
          volume_ml: 1000
          status: "scheduled"
          created_at: "2026-01-31T10:30:00"
          synced_at: "2026-01-31T10:30:05"
      
      history/
        HIST_20260131103000/
          id: "HIST_20260131103000"
          date: "2026-01-31"
          time: "08:00"
          spray_type: "Fertilizer"
          container: "Container 1"
          volume_ml: 1000
          duration: 12.0
          completed_at: "2026-01-31T08:00:15"
          synced_at: "2026-01-31T08:00:20"
      
      status/
        tank1_level: 80.5
        tank2_level: 65.0
        last_update: "2026-01-31T10:30:00"
      
      weather/
        temperature_c: 28.5
        humidity: 75
        condition: "Partly cloudy"
        precip_mm: 0.0
        timestamp: "2026-01-31T10:30:00"
      
      commands/
        CMD_001/
          command: "manual-spray"
          container: 1
          volume_ml: 500
          executed: false
          created_at: "2026-01-31T10:30:00"
```

## Usage

### Python API

#### Initialize Firebase Service
```python
from core.firebase_service import get_firebase_service

firebase = get_firebase_service()

# Check connection
if firebase.connected:
    print("Firebase connected!")
    
# Enable background sync
firebase.enable_sync()
```

#### Schedule Management
```python
# Upload a schedule
schedule = {
    'id': 'SCH_001',
    'date': '2026-02-01',
    'time': '08:00',
    'spray_type': 'Fertilizer',
    'container': 'Container 1',
    'volume_ml': 1000,
    'status': 'scheduled'
}
firebase.upload_schedule(schedule)

# Get all schedules
schedules = firebase.get_schedules()

# Delete a schedule
firebase.delete_schedule('SCH_001')
```

#### History Management
```python
# Upload history entry
history_entry = {
    'date': '2026-01-31',
    'time': '08:00',
    'spray_type': 'Fertilizer',
    'volume_ml': 1000,
    'duration': 12.0
}
firebase.upload_history_entry(history_entry)

# Get recent history
history = firebase.get_history(limit=10)
```

#### Tank Levels
```python
# Update tank levels
firebase.update_tank_levels(tank1_percent=80.5, tank2_percent=65.0)
```

#### Weather Data
```python
# Upload weather data
weather_data = {
    'temperature_c': 28.5,
    'humidity': 75,
    'condition': 'Partly cloudy',
    'precip_mm': 0.0
}
firebase.upload_weather_data(weather_data)

# Get weather data
weather = firebase.get_weather_data()
```

### Weather Service

```python
from core.weather_service import get_weather_service

weather = get_weather_service()

# Check if it's raining
if weather.check_weather_for_rain():
    print("It's raining - avoid spraying")
else:
    print("No rain - safe to spray")

# Get detailed weather
weather_data = weather.get_weather_data()
print(f"Temperature: {weather_data['temperature_c']}°C")
print(f"Humidity: {weather_data['humidity']}%")
```

### DataStore with Firebase

The DataStore automatically syncs with Firebase when available:

```python
from core.data_store import get_data_store

data_store = get_data_store()

# Add schedule (automatically syncs to Firebase)
schedule = data_store.add_schedule({
    'date': '2026-02-01',
    'time': '08:00',
    'spray_type': 'Fertilizer',
    'container': 'Container 1',
    'volume_ml': 1000
})

# Manual sync all data
data_store.sync_all_to_firebase()
```

## Features

### Automatic Sync
- All schedules are automatically synced to Firebase when created/updated/deleted
- All spray history is automatically uploaded to Firebase
- Local JSON files serve as backup if Firebase is unavailable

### Remote Commands
- Send commands to the device via Firebase
- Commands are checked every 5 seconds
- Supports remote spray operations

### Weather Integration
- RPI checks weather conditions before spraying
- Weather data stored in Firebase for monitoring
- Automatic rain detection to avoid spraying in bad weather

### Multi-Device Support
- Each device has a unique ID (e.g., "SmartSprayer_001")
- Multiple devices can be managed under one Firebase project
- Each device has isolated data

## Security

### Firebase Security Rules

Add these rules to your Firebase Realtime Database:

```json
{
  "rules": {
    "smart-sprayer": {
      "devices": {
        "$deviceId": {
          ".read": "auth != null",
          ".write": "auth != null"
        }
      }
    }
  }
}
```

### Best Practices
1. Never commit `firebase_credentials.py` (already in .gitignore)
2. Use environment-specific credentials
3. Regularly rotate passwords
4. Use Firebase Authentication for access control
5. Monitor Firebase usage quotas

## Troubleshooting

### Firebase Connection Issues
```python
firebase = get_firebase_service()
if not firebase.connected:
    print("Check firebase_credentials.py configuration")
```

### Weather API Issues
```python
weather = get_weather_service()
if not weather.available:
    print("Check WEATHER_API_KEY in firebase_credentials.py")
```

### Sync Issues
- Check internet connection on RPI
- Verify Firebase credentials
- Check Firebase console for errors
- Review local logs

## Benefits of This Architecture

1. **Centralized Internet**: RPI handles all web connectivity
2. **ESP32 Simplicity**: Focuses only on hardware control
3. **Cloud Backup**: All data backed up to Firebase
4. **Remote Access**: Monitor and control from anywhere
5. **Multi-Device**: Scale to multiple sprayers
6. **Weather Integration**: Smart scheduling based on weather
7. **Offline Support**: Works without internet, syncs when available

## Migration from Old System

If you have existing ESP32 code with WiFi/Firebase:

1. Flash updated ESP32 firmware (WiFi/Firebase removed)
2. Install updated RPI software with Firebase
3. Configure firebase_credentials.py
4. Existing schedules will continue working (local storage)
5. Firebase sync happens automatically once configured

## ESP32 Changes

The ESP32 firmware has been simplified:
- **Removed files**: WIFI_CONFIG.h, FIREBASE_CONFIG.h, NTP_CONFIG.h, WEATHER_CONFIG.h
- **Removed commands**: wifi-reset, check-ntp, update-ntp, check-weather, etc.
- **Retained commands**: All hardware commands (relay, buzzer, distance, GSM)
- **Time sync**: RPI can send time via `set-time` command if needed

## Next Steps

1. Set up Firebase project
2. Configure credentials
3. Test Firebase connection
4. Enable automatic sync
5. Monitor data in Firebase console
6. Build mobile app or web dashboard (optional)
