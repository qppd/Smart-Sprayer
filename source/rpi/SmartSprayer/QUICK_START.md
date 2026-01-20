# QUICK START GUIDE
# Smart Sprayer GUI - Get Started in 3 Minutes

## Step 1: Install Dependencies (1 minute)

Open terminal/command prompt in the SmartSprayer folder and run:

```bash
pip install customtkinter tkcalendar requests
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

## Step 2: Generate Sample Data (Optional - 30 seconds)

To test with sample schedules and history:

```bash
python sample_data_generator.py
```

This creates:
- 5 upcoming schedules
- 10 historical spray records
- Recurring schedule series

## Step 3: Launch the GUI (30 seconds)

```bash
python run_gui.py
```

The GUI will open with 5 main sections accessible from the left sidebar:

1. **📊 Dashboard** - System overview and tank levels
2. **📅 Scheduling** - Create and manage spray schedules
3. **📋 Previous Data** - View spray history
4. **🔔 Notifications** - System status and alerts
5. **📝 System Logs** - View system logs

## Quick Tasks

### Create Your First Schedule

1. Click **"📅 Scheduling"** in sidebar
2. Click **"📅 Pick Date"** button
3. Select a date from calendar
4. Set time (e.g., 08:00)
5. Choose spray type (Fertilizer/Pesticide)
6. Choose container (1 or 2)
7. Click **"✓ CREATE SCHEDULE"**

Done! Your schedule is created.

### Create Recurring Schedule

1. Follow steps 1-6 above
2. Check **"Enable Recurring Schedule"**
3. Enter interval (e.g., 7 for weekly)
4. Enter count (e.g., 4 for 4 times)
5. Click **"✓ CREATE SCHEDULE"**

Done! Multiple schedules created automatically.

### Reschedule

1. Go to **"📅 Scheduling"**
2. Find schedule in **"ACTIVE SCHEDULES"** list
3. Click **"Reschedule"** button
4. Pick new date and time
5. Click **"✓ Confirm Reschedule"**

System automatically adjusts any conflicting schedules!

### View Tank Levels

1. Click **"📊 Dashboard"**
2. Tank levels update automatically every 2 seconds
3. Green = Good, Orange = Low, Red = Critical

### Check Logs

1. Click **"📝 System Logs"**
2. Logs auto-refresh every 5 seconds
3. Filter by level (All, INFO, WARNING, ERROR)
4. Color-coded for easy reading

## Important Notes

- **PC Mode**: Currently running with mock hardware (safe for testing)
- **Reschedule Limit**: Maximum 3 reschedules per schedule
- **Auto-Adjust**: System automatically resolves schedule conflicts
- **Data Storage**: All data saved in `data/` folder (JSON files)
- **Logs**: Saved in `logs/smartsprayer.log`

## Keyboard Shortcuts

None currently - use mouse/touch

## Troubleshooting

**GUI won't start?**
```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
pip install --upgrade customtkinter tkcalendar
```

**No schedules showing?**
```bash
# Generate sample data
python sample_data_generator.py
```

**Errors in console?**
- Check logs in System Logs panel
- Ensure you're in correct directory
- All project files present

## Next Steps

1. Explore all 5 panels
2. Create test schedules
3. Try rescheduling with auto-adjust
4. Export spray history
5. Monitor system logs

## Ready for Production?

When ready to deploy to Raspberry Pi:

1. Install on Pi: `pip install RPi.GPIO pyserial`
2. Edit `hardware/hardware_interface.py`: Set `PC_MODE = False`
3. Connect hardware according to `PINS_CONFIG.py`
4. Run: `python run_gui.py`

## Need Help?

- Check `README_GUI.md` for detailed documentation
- Review logs in System Logs panel
- Check console for error messages

---

**Enjoy your Smart Sprayer! 🌱**
