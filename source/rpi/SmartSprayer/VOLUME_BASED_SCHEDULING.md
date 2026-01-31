# Volume-Based Spray Scheduling

## Overview
The Smart Sprayer system now supports volume-based spray scheduling. Users can specify the exact amount of liquid (in mL) they want to spray, and the system automatically calculates the required spray duration based on the pump specifications.

## Pump Specifications
- **Flow Rate**: 5 L/min (5000 mL/min)
- **Calculation**: Duration (seconds) = (Volume in mL / 5000) × 60

## Changes Made

### 1. Scheduler Core (`core/scheduler.py`)
- Added `PUMP_RATE_ML_PER_MIN` constant (5000 mL/min)
- Added `calculate_spray_duration(volume_ml)` method to calculate spray duration
- Updated `create_schedule()` to accept `volume_ml` parameter instead of `duration`
- Updated `create_recurring_schedules()` to accept `volume_ml` parameter
- Modified `_execute_schedule()` to calculate spray duration from stored volume
- Schedule data now stores `volume_ml` instead of `duration`
- History logs now include both `volume_ml` and calculated `duration`

### 2. Scheduling UI (`ui/scheduling.py`)
- Added "SPRAY VOLUME (mL)" input field with default value of 1000 mL
- Added info label showing pump rate (5L/min)
- Volume validation ensures positive values
- Success message now displays volume and calculated duration
- Schedule cards display both volume and calculated duration
- Form clearing resets volume to default 1000 mL

### 3. Dashboard (`ui/dashboard.py`)
- Next schedule display now shows:
  - Volume (mL)
  - Calculated duration (seconds)

### 4. Previous Data (`ui/previous_data.py`)
- History cards now display:
  - Volume (mL) for each spray event
  - Duration (seconds)

## Usage Examples

### Example 1: 1000 mL Spray
- **Volume**: 1000 mL
- **Calculated Duration**: 12 seconds
- **Calculation**: (1000 / 5000) × 60 = 12 seconds

### Example 2: 500 mL Spray
- **Volume**: 500 mL
- **Calculated Duration**: 6 seconds
- **Calculation**: (500 / 5000) × 60 = 6 seconds

### Example 3: 2500 mL Spray
- **Volume**: 2500 mL
- **Calculated Duration**: 30 seconds
- **Calculation**: (2500 / 5000) × 60 = 30 seconds

## Creating a Schedule with Volume

1. Open the **Scheduling** panel in the GUI
2. Select date and time
3. Choose spray type (Fertilizer/Pesticide)
4. Select container (Container 1/2)
5. **Enter volume in mL** (default: 1000 mL)
6. Optionally enable recurring schedule
7. Click "CREATE SCHEDULE"

The system will:
- Validate the volume input
- Calculate the spray duration automatically
- Store the volume in the schedule
- Display both volume and duration in confirmations

## Data Structure

### Schedule Object
```json
{
  "id": "SCHED_20260131123045_1234",
  "date": "2026-02-01",
  "time": "08:00",
  "spray_type": "Fertilizer",
  "container": "Container 1",
  "volume_ml": 1000,
  "status": "scheduled",
  "reschedule_count": 0
}
```

### History Object
```json
{
  "id": "HIST_20260131123045_5678",
  "date": "2026-01-31",
  "time": "08:00",
  "spray_type": "Fertilizer",
  "container": "Container 1",
  "volume_ml": 1000,
  "duration": 12.0,
  "schedule_id": "SCHED_20260131123045_1234",
  "completed_at": "2026-01-31T08:00:15"
}
```

## Benefits

1. **Precision**: Spray exactly the amount needed
2. **Efficiency**: No waste from over-spraying
3. **Flexibility**: Different volumes for different schedules
4. **Automation**: Duration calculated automatically
5. **Consistency**: Same volume = same duration every time

## Notes

- Default volume is 1000 mL if not specified
- Minimum volume is greater than 0 mL
- Volume input accepts decimal values (e.g., 1250.5 mL)
- All existing schedules without volume will use 1000 mL default
- The pump rate (5L/min) is configurable in the code if needed

## Future Enhancements

Potential improvements:
- Volume presets (common amounts)
- Tank level tracking to prevent over-scheduling
- Volume suggestions based on field size
- Pump calibration feature to adjust flow rate
- Multiple pump profiles support
