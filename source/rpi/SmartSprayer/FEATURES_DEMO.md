# FEATURES_DEMO.md
# Smart Sprayer GUI - Feature Demonstration Guide

This guide demonstrates all key features of the Smart Sprayer GUI.

---

## 🎯 FEATURE 1: Dashboard Overview

**What it does:** Real-time system monitoring

**Try this:**
1. Launch GUI: `python run_gui.py`
2. Click **"📊 Dashboard"**
3. Observe:
   - Tank 1 level (updates every 2 seconds)
   - Tank 2 level (updates every 2 seconds)
   - Color changes: Green (>50%) → Orange (20-50%) → Red (<20%)
   - System status (IDLE/SCHEDULED/RESCHEDULED/EXECUTING)
   - Next scheduled spray info
   - Countdown timer
   - Live date/time

**Expected behavior:**
- Tank levels fluctuate slightly (simulated usage)
- All elements update automatically
- No UI freezing

---

## 🎯 FEATURE 2: Simple Schedule Creation

**What it does:** Create a single spray schedule

**Try this:**
1. Click **"📅 Scheduling"**
2. Click **"📅 Pick Date"**
3. Select tomorrow's date
4. Set time to **08:00**
5. Select **Fertilizer**
6. Select **Container 1**
7. Click **"✓ CREATE SCHEDULE"**

**Expected behavior:**
- Success message appears
- Schedule appears in "ACTIVE SCHEDULES" list
- Dashboard updates to show new schedule
- Log entry created

---

## 🎯 FEATURE 3: Recurring Schedule

**What it does:** Create multiple schedules with fixed interval

**Try this:**
1. Go to **"📅 Scheduling"**
2. Pick a date (3 days from now)
3. Set time to **09:00**
4. Select **Pesticide**
5. Select **Container 2**
6. Check **"Enable Recurring Schedule"**
7. Enter interval: **5** (days)
8. Enter count: **4** (occurrences)
9. Click **"✓ CREATE SCHEDULE"**

**Expected behavior:**
- Success message: "Created 4 recurring schedules with 5-day interval"
- 4 schedules appear in list:
  - Day 3 at 09:00
  - Day 8 at 09:00
  - Day 13 at 09:00
  - Day 18 at 09:00
- All have same series_id
- Interval = 5 days maintained

---

## 🎯 FEATURE 4: Reschedule (Simple)

**What it does:** Change date/time of existing schedule

**Try this:**
1. Find any schedule in "ACTIVE SCHEDULES"
2. Click **"Reschedule"** button
3. Pick a new date (different from original)
4. Pick a new time
5. Click **"✓ Confirm Reschedule"**

**Expected behavior:**
- Schedule updated with new date/time
- Reschedule count increments (shown as "Reschedules: 1/3")
- Log entry created
- Status changes to "RESCHEDULED"

---

## 🎯 FEATURE 5: Auto-Adjust (Conflict Resolution)

**What it does:** Automatically resolve date conflicts

**Setup:**
1. Create Schedule A: Tomorrow at 08:00 (Fertilizer, Container 1)
2. Create Schedule B: Day after tomorrow at 08:00 (Pesticide, Container 2)

**Test auto-adjust:**
1. Reschedule Schedule A to "day after tomorrow" (same as B)
2. Confirm reschedule

**Expected behavior:**
- Schedule A moves to day after tomorrow
- Schedule B **automatically moves** to one day later
- Success message shows: "1 other schedule(s) auto-adjusted"
- Both schedules visible in list with new dates
- Log shows auto-adjustment

---

## 🎯 FEATURE 6: Auto-Adjust (Interval Preservation)

**What it does:** Maintain interval consistency in recurring series

**Setup:**
1. Create recurring schedule:
   - Start: 5 days from now
   - Time: 07:00
   - Type: Fertilizer
   - Container: Container 1
   - Interval: **7 days**
   - Count: **3**
2. This creates schedules on Day 5, Day 12, Day 19

**Test interval preservation:**
1. Find first schedule (Day 5)
2. Click "Reschedule"
3. Change to **Day 6** (shift by +1 day)
4. Confirm

**Expected behavior:**
- First schedule: Day 5 → Day 6
- Second schedule: Day 12 → Day 13 (auto-adjusted +1)
- Third schedule: Day 19 → Day 20 (auto-adjusted +1)
- **Interval still 7 days** (6→13→20)
- Success message shows affected schedules
- All changes logged

---

## 🎯 FEATURE 7: Maximum Reschedule Enforcement

**What it does:** Enforce 3-reschedule limit

**Try this:**
1. Create a simple schedule
2. Reschedule it (count = 1)
3. Reschedule it again (count = 2)
4. Reschedule it again (count = 3)
5. Try to reschedule it one more time (count = 4)

**Expected behavior:**
- First 3 reschedules work normally
- 4th reschedule attempt:
  - Error message: "Maximum 3 reschedules reached. All schedules cancelled."
  - Schedule is cancelled
  - If part of series, ALL series schedules cancelled
  - Must create new schedule from scratch

---

## 🎯 FEATURE 8: Previous Data Viewer

**What it does:** View completed spray history

**Setup:**
1. Run: `python sample_data_generator.py` (if not done)

**Try this:**
1. Click **"📋 Previous Data"**
2. Observe:
   - Statistics: Total, Fertilizer, Pesticide counts
   - Complete history list
3. Try filters:
   - Click **"Fertilizer"** radio button
   - Only fertilizer sprays shown
   - Click **"Pesticide"**
   - Only pesticide sprays shown
   - Click **"All"** to see everything
4. Click **"📥 Export"**
5. Choose save location
6. JSON file created with all data

**Expected behavior:**
- History cards show date, time, type, container
- Color badges: Blue (Fertilizer), Orange (Pesticide)
- Statistics update with filters
- Export creates valid JSON file

---

## 🎯 FEATURE 9: Notifications Panel

**What it does:** Display system status and alerts

**Try this:**
1. Click **"🔔 Notifications"**
2. Observe:
   - System status (IDLE/SCHEDULED/etc.)
   - Tank 1 status with color indicator
   - Tank 2 status with color indicator
   - Upcoming schedules (next 5)
   - Recent activity (last 5 completed)

**Test tank alerts:**
1. Note current tank levels
2. Wait a few seconds
3. Observe level changes
4. When level drops below 50%: Orange color + "⚠ Low"
5. If drops below 20%: Red color + "✕ Critical"

**Expected behavior:**
- All sections update every 3 seconds
- Color-coded alerts
- Real-time status changes

---

## 🎯 FEATURE 10: System Logs Viewer

**What it does:** View all system events

**Try this:**
1. Click **"📝 System Logs"**
2. Observe color-coded logs:
   - Green: INFO
   - Orange: WARNING
   - Red: ERROR
   - Blue: DEBUG
3. Try filtering:
   - Select "WARNING" from dropdown
   - Only warnings shown
   - Select "ERROR"
   - Only errors shown
4. Uncheck "Auto-refresh" to pause updates
5. Click "🔄 Refresh" to manually update
6. Click "🗑 Clear Logs" to erase all logs

**Expected behavior:**
- Logs update every 5 seconds (if auto-refresh on)
- Filtering works correctly
- Clear logs empties the file
- Scrolls to bottom automatically

---

## 🎯 FEATURE 11: Mock Hardware Simulation

**What it does:** Simulate hardware without GPIO

**Observe:**
1. Tank levels change gradually
2. Console shows mock hardware actions:
   - `[MOCK] Relay 1 turned ON`
   - `[MOCK] Buzzer beeped`
   - `[MOCK] LED 'status' set to ON`
3. All hardware operations logged

**Expected behavior:**
- No errors even without Raspberry Pi
- Realistic simulation
- All actions logged
- Safe for development

---

## 🎯 FEATURE 12: Schedule Execution (Simulated)

**What it does:** Execute spray when scheduled time arrives

**Test (requires wait):**
1. Create schedule for **current time + 2 minutes**
2. Watch dashboard countdown
3. When time arrives:
   - Status changes to "EXECUTING"
   - Relay activated (console shows)
   - Buzzer beeps (console shows)
   - LED turns on (console shows)
   - Wait 30 seconds (spray duration)
   - Relay deactivated
   - Schedule marked "completed"
   - Moved to history

**Expected behavior:**
- Automatic execution at scheduled time
- All hardware actions logged
- Schedule moves to history
- Notifications updated

---

## 🎯 FEATURE 13: Data Persistence

**What it does:** Save data across sessions

**Test:**
1. Create several schedules
2. Close GUI
3. Reopen GUI: `python run_gui.py`
4. Check Scheduling panel

**Expected behavior:**
- All schedules restored
- History preserved
- No data loss
- Files: `data/schedules.json`, `data/history.json`

---

## 🎯 FEATURE 14: Cancel Operations

**What it does:** Cancel individual or all schedules

**Try this:**

**Cancel Single:**
1. Find any schedule
2. Click "Cancel" button
3. Confirm

**Cancel All:**
1. Click "✕ Cancel All Schedules"
2. Confirm

**Expected behavior:**
- Single cancel: Schedule status → "cancelled"
- Cancel all: All schedules cancelled
- Cancelled schedules don't execute
- Actions logged
- UI updates immediately

---

## 🎯 FEATURE 15: Navigation & UI Responsiveness

**What it does:** Smooth navigation between panels

**Try this:**
1. Click through all 5 navigation buttons quickly
2. Resize window
3. Scroll in panels with content
4. Interact with multiple elements

**Expected behavior:**
- Instant panel switching
- Active panel highlighted (green)
- No lag or freezing
- Responsive to all screen sizes
- Smooth scrolling

---

## 🔍 ADVANCED TESTING SCENARIOS

### Scenario 1: Complex Conflict Chain
1. Create 5 schedules on consecutive days
2. Reschedule day 3 to day 4
3. Observe cascade: day 4→5, day 5→6, etc.

### Scenario 2: Multiple Series Management
1. Create series A: Every 5 days, 3 times
2. Create series B: Every 7 days, 3 times
3. Reschedule one from each series
4. Observe independent auto-adjustments

### Scenario 3: Edge Case - Same Time Different Container
1. Create Schedule A: Tomorrow, 08:00, Container 1
2. Create Schedule B: Tomorrow, 08:00, Container 2
3. Both should execute (no conflict - different containers)

### Scenario 4: Rapid Rescheduling
1. Create schedule
2. Reschedule 3 times rapidly
3. Try 4th reschedule
4. Observe cancellation

---

## 📊 EXPECTED PERFORMANCE

- **Startup time:** < 3 seconds
- **Panel switching:** Instant
- **Tank updates:** Every 2 seconds
- **Log updates:** Every 5 seconds
- **UI responsiveness:** No freezing
- **Memory usage:** < 200 MB
- **CPU usage:** < 5% (idle)

---

## ✅ VERIFICATION CHECKLIST

After testing all features, you should have:
- [ ] Created single schedules
- [ ] Created recurring schedules
- [ ] Rescheduled successfully
- [ ] Seen auto-adjust in action
- [ ] Hit reschedule limit
- [ ] Viewed history
- [ ] Filtered data
- [ ] Exported data
- [ ] Monitored tank levels
- [ ] Viewed logs
- [ ] Cancelled schedules
- [ ] Observed schedule execution
- [ ] Verified data persistence
- [ ] Tested all 5 navigation panels

---

## 🎉 CONCLUSION

If all features work as described:
✅ **Your Smart Sprayer GUI is fully functional!**

Ready for:
- Development testing
- Feature demonstrations
- Raspberry Pi deployment
- Production use

---

**Happy farming! 🌱**
