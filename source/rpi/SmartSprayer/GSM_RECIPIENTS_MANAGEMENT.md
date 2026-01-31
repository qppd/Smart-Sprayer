# GSM Recipient Management

## Overview
GSM SMS recipients are now managed through the RPI GUI Settings panel instead of being hardcoded in the ESP32 firmware. This provides a more flexible and user-friendly way to add, delete, and sync recipients.

## Architecture

### ESP32 (Firmware)
- **Dynamic Recipients Array**: Stores up to 10 recipients in memory
- **Serial Commands**: Receives recipient management commands from RPI
  - `add-recipient_+639123456789` - Add a recipient
  - `remove-recipient_+639123456789` - Remove a recipient
  - `clear-recipients` - Clear all recipients
  - `list-recipients` - List all current recipients
- **SMS Functions**: 
  - `sendSMS(number, message)` - Send to specific number
  - `sendSMSToAll(message)` - Send to all recipients
  - `sendSMSWithResponse(number, message)` - Send with delivery confirmation

### Raspberry Pi (Python)
- **Data Storage**: Recipients stored in `data/recipients.json`
- **Firebase Sync**: Auto-syncs recipients to Firebase cloud
- **GUI Settings Panel**: User-friendly interface for recipient management
- **Hardware Interface**: Syncs recipients to ESP32 on startup and changes

## Usage Guide

### Adding Recipients via GUI

1. Open Smart Sprayer GUI
2. Navigate to **Settings** tab (⚙️)
3. In the "GSM SMS Recipients" section:
   - Enter phone number (e.g., `+639123456789`)
   - Optionally enter a name (e.g., "John Doe")
   - Click **Add Recipient**
4. The recipient is automatically:
   - Saved to local `data/recipients.json`
   - Synced to Firebase cloud
   - Sent to ESP32 via serial command

### Deleting Recipients

1. In the Settings panel, scroll to the recipient list
2. Click the red **Delete** button next to the recipient
3. Confirm the deletion
4. The recipient is automatically:
   - Removed from local storage
   - Removed from Firebase
   - Removed from ESP32 memory

### Manual Sync to ESP32

If recipients get out of sync with ESP32 (e.g., after ESP32 reset):

1. Click the **Sync to ESP32** button in the Settings panel
2. This will:
   - Clear all recipients on ESP32
   - Re-add all recipients from RPI storage
   - Confirm sync success

### Programmatic Access

#### Python Code Example

```python
from core.data_store import get_recipients, add_recipient, delete_recipient

# Get all recipients
recipients = get_recipients()
for r in recipients:
    print(f"{r['name']}: {r['phone']}")

# Add a recipient
success = add_recipient("+639123456789", "John Doe")

# Delete a recipient
success = delete_recipient("+639123456789")
```

#### ESP32 Serial Commands

```cpp
// Add recipient
Serial.println("add-recipient_+639123456789");

// Remove recipient
Serial.println("remove-recipient_+639123456789");

// Clear all
Serial.println("clear-recipients");

// List all
Serial.println("list-recipients");
```

## Data Structure

### recipients.json Format
```json
[
  {
    "phone": "+639123456789",
    "name": "John Doe",
    "added_at": "2025-01-28T10:30:00"
  },
  {
    "phone": "+639987654321",
    "name": "Jane Smith",
    "added_at": "2025-01-28T11:45:00"
  }
]
```

### Firebase Structure
```
devices/
  SmartSprayer_001/
    recipients/
      recipients: [...]
      updated_at: "2025-01-28T10:30:00"
```

## Migration Notes

### Removed Files from ESP32
The following credential files have been removed from ESP32:
- `FIREBASE_CREDENTIALS.h` ❌ (moved to RPI)
- `GSM_RECIPIENTS.h` ❌ (moved to RPI Settings)
- `GSM_RECIPIENTS_template.h` ❌ (no longer needed)
- `WEATHER_CREDENTIALS.h` ❌ (moved to RPI)

### Updated Files

#### ESP32
- `GSM_CONFIG.h`: Dynamic recipient array, serial command handlers
- `SmartSprayer.ino`: Added recipient management commands

#### RPI
- `ui/settings.py`: New Settings panel with recipient management UI
- `core/data_store.py`: Recipient storage functions
- `core/firebase_service.py`: Recipient sync to Firebase
- `hardware/esp32_hardware.py`: `sync_recipients()` function
- `ui/main_ui.py`: Added Settings tab to navigation

## Troubleshooting

### Recipients Not Sending SMS
1. Check ESP32 serial connection: Settings > Sync to ESP32
2. Verify phone number format: Must start with `+` (e.g., `+639123456789`)
3. Check GSM module: ESP32 serial monitor should show "SMS sent to: +639..."
4. Verify SIM card credit and signal

### Recipients Not Syncing to Firebase
1. Check Firebase credentials in `firebase_credentials.py`
2. Verify internet connection on RPI
3. Check Firebase console for data under `devices/SmartSprayer_001/recipients`

### ESP32 Recipients Lost After Reset
- This is expected behavior (ESP32 only stores in RAM)
- Solution: Click **Sync to ESP32** button in Settings panel
- Future Enhancement: Auto-sync on RPI startup

## Benefits of New System

✅ **User-Friendly**: Add/delete recipients without re-uploading ESP32 firmware  
✅ **Cloud Backup**: Recipients backed up to Firebase automatically  
✅ **Flexible**: No hardcoded limits, easy to modify  
✅ **Secure**: Credentials no longer in ESP32 firmware  
✅ **Centralized**: All configuration managed from RPI GUI  

## Future Enhancements

- [ ] Auto-sync recipients to ESP32 on RPI startup
- [ ] Recipient groups (e.g., "Admins", "Farmers")
- [ ] SMS message templates per recipient
- [ ] SMS delivery status tracking
- [ ] Import/export recipient lists (CSV)
