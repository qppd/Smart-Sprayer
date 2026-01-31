# Weather-Based Smart Scheduling

## Overview
The Smart Sprayer system now automatically checks weather conditions before executing spray schedules. If rain is detected or forecasted, schedules are automatically postponed to ensure optimal spraying conditions.

## Features

### 1. Automatic Weather Checking
- **Before Execution**: Every schedule is checked for weather conditions before spraying
- **Current Weather**: Checks if it's currently raining
- **Forecast**: Checks if rain is expected in the next 24 hours
- **Auto-Reschedule**: Automatically postpones sprays if rain detected

### 2. Smart Rescheduling
- Schedules are postponed by 1 day if rain is detected
- Maximum 3 automatic reschedules (configurable)
- After 3 reschedules, schedule is cancelled to prevent indefinite postponement
- All reschedule events are logged

### 3. Weather Data Storage
- Weather data synced to Firebase
- Historical weather records for each spray
- Analytics on weather-based postponements

## Configuration

### Setup Weather API

1. **Get API Key** (Free)
   - Sign up at [WeatherAPI.com](https://www.weatherapi.com/)
   - Free tier: 1 million calls/month
   - Get your API key from dashboard

2. **Configure Credentials**
   
   Copy and edit firebase_credentials_template.py:
   ```python
   # Weather API configuration
   WEATHER_API_KEY = "your_api_key_here"
   WEATHER_LOCATION = "Manila"  # Or your location
   WEATHER_API_URL = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={WEATHER_LOCATION}&aqi=no"
   WEATHER_FORECAST_URL = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={WEATHER_LOCATION}&days=5&aqi=no"
   ```

3. **Location Options**
   - City name: `"Manila"`, `"Quezon City"`, `"Cebu"`
   - Coordinates: `"14.5995,120.9842"` (Lat,Lon)
   - Postal code: `"1000"` (with country)
   - IP address: `"auto:ip"` (auto-detect)

## How It Works

### Weather Check Flow

```
Schedule Due
    ↓
Check Current Weather
    ↓
Is it raining? ──Yes──→ Reschedule (+1 day)
    ↓ No
Check 24h Forecast
    ↓
Rain expected? ──Yes──→ Reschedule (+1 day)
    ↓ No
Execute Spray
```

### Decision Criteria

Rain is detected when **any** of these conditions are met:

**Current Weather:**
- Precipitation > 0 mm
- Weather condition contains "rain"

**Forecast (24h ahead):**
- Rain probability > 50%
- API indicates rain expected
- Total expected precipitation > 1 mm

## Usage Examples

### Automatic Weather Checking (Default)

When scheduler runs, weather is checked automatically:

```python
from core.scheduler import get_scheduler

scheduler = get_scheduler(hardware_interface)
scheduler.start()

# Weather checks happen automatically before each spray
# No manual intervention needed!
```

### Manual Weather Check for Schedule

```python
from core.scheduler import get_scheduler

scheduler = get_scheduler()

# Check weather for specific schedule
result = scheduler.check_weather_for_schedule('SCH_001')

print(f"Currently raining: {result['is_raining_now']}")
print(f"Rain forecast: {result['rain_forecast']}")
print(f"Recommendation: {result['recommendation']}")
print(f"Temperature: {result['weather_data']['temperature_c']}°C")
print(f"Humidity: {result['weather_data']['humidity']}%")
```

### Direct Weather Service Usage

```python
from core.weather_service import get_weather_service

weather = get_weather_service()

# Check current weather
if weather.check_weather_for_rain():
    print("It's raining - don't spray!")
else:
    print("Safe to spray")

# Check forecast
if weather.check_forecast_for_rain(hours_ahead=24):
    print("Rain expected in next 24 hours")

# Get detailed weather
data = weather.get_weather_data()
print(f"Temp: {data['temperature_c']}°C")
print(f"Humidity: {data['humidity']}%")
print(f"Wind: {data['wind_kph']} kph")
print(f"Condition: {data['condition']}")
```

## Reschedule Logic

### Maximum Reschedules
- **Default**: 3 reschedules maximum
- **Configurable**: Change `MAX_RESCHEDULES` in `reschedule_logic.py`
- **Reason**: Prevent infinite postponement during rainy season

### What Happens After Max Reschedules

1. Schedule is **cancelled** (not deleted)
2. Status changed to `'cancelled'`
3. Reason recorded: `'weather_max_reschedules'`
4. Notification sent (if enabled)
5. User can manually create new schedule

### Example Scenario

```
Original Schedule: Feb 1, 8:00 AM
Day 1 (Feb 1): Rain detected → Reschedule to Feb 2 (Attempt 1/3)
Day 2 (Feb 2): Rain detected → Reschedule to Feb 3 (Attempt 2/3)
Day 3 (Feb 3): Rain detected → Reschedule to Feb 4 (Attempt 3/3)
Day 4 (Feb 4): Rain detected → Schedule CANCELLED
```

## Weather Data in Firebase

Weather data is automatically stored in Firebase:

```json
{
  "devices": {
    "SmartSprayer_001": {
      "weather": {
        "temperature_c": 28.5,
        "temperature_f": 83.3,
        "humidity": 75,
        "condition": "Partly cloudy",
        "wind_kph": 12.5,
        "precip_mm": 0.0,
        "cloud": 50,
        "feels_like_c": 31.2,
        "uv": 7,
        "timestamp": "2026-01-31T10:30:00"
      },
      "schedules": {
        "SCH_001": {
          "reschedule_reason": "weather",
          "weather_checked_at": "2026-01-31T08:00:00",
          "reschedule_count": 1
        }
      }
    }
  }
}
```

## Logging

Weather events are automatically logged:

```
[INFO] Checking weather before spray...
[INFO] Weather check passed - safe to spray
```

```
[WARNING] Rain detected! Rescheduling spray schedule SCH_001
[INFO] Schedule SCH_001 rescheduled to 2026-02-02 08:00 due to weather
```

```
[WARNING] Maximum reschedules (3) reached. All related schedules cancelled.
```

## Benefits

### For Farmers/Users
✓ **Prevent Waste**: Don't spray when rain will wash it away
✓ **Save Money**: Optimize fertilizer/pesticide usage
✓ **Better Results**: Spray only in optimal conditions
✓ **Automatic**: No manual monitoring needed
✓ **Peace of Mind**: System handles weather checking

### For Crops
✓ **Better Absorption**: Chemicals applied in dry conditions
✓ **No Runoff**: Prevent environmental contamination
✓ **Optimal Timing**: Maximize effectiveness
✓ **Healthier Growth**: Proper application timing

### For Environment
✓ **Prevent Runoff**: Keep chemicals out of waterways
✓ **Reduce Waste**: Don't overspray due to rain
✓ **Sustainable**: Smart resource management

## Advanced Configuration

### Custom Weather Thresholds

Edit `weather_service.py` to customize thresholds:

```python
# In check_weather_for_rain()
# Default: precip_mm > 0.0
# Custom: precip_mm > 0.5  # Only reschedule if more than 0.5mm

# In check_forecast_for_rain()
# Default: daily_chance_of_rain > 50
# Custom: daily_chance_of_rain > 70  # Higher threshold
```

### Custom Reschedule Interval

Edit `scheduler.py` to change postponement period:

```python
# In _reschedule_due_to_weather()
# Default: timedelta(days=1)
# Custom: timedelta(hours=12)  # Postpone by 12 hours instead
```

### Disable Weather Checking

To temporarily disable weather checking:

```python
# Option 1: Don't configure weather credentials
# Weather service will be unavailable

# Option 2: Set weather to None
scheduler.weather = None
```

## Troubleshooting

### Weather Check Not Working

**Check 1: Credentials**
```python
from core.weather_service import get_weather_service
weather = get_weather_service()
print(f"Weather available: {weather.available}")
```

**Check 2: Internet Connection**
```bash
curl "https://api.weatherapi.com/v1/current.json?key=YOUR_KEY&q=Manila"
```

**Check 3: API Key**
- Verify key is correct in firebase_credentials.py
- Check API quota at weatherapi.com dashboard
- Ensure key is active

### Schedule Not Rescheduling

**Verify weather service in scheduler:**
```python
from core.scheduler import get_scheduler
scheduler = get_scheduler()
print(f"Weather service: {scheduler.weather}")
print(f"Weather available: {scheduler.weather.available if scheduler.weather else False}")
```

**Check logs:**
```
source/rpi/SmartSprayer/logs/
```

### False Positives

If system is too aggressive (rescheduling too often):

1. Increase rain probability threshold (50% → 70%)
2. Increase precipitation threshold (1mm → 2mm)
3. Reduce forecast check window (24h → 12h)

## Weather API Information

### Free Tier Limits
- **1 million calls/month**
- **Current weather data**
- **3-day forecast**
- **No credit card required**

### Estimated Usage
- 1 check per scheduled spray
- ~10-50 sprays per month = ~50 API calls
- Well within free tier limits

### API Endpoints Used

1. **Current Weather**
   ```
   https://api.weatherapi.com/v1/current.json
   ```
   - Real-time weather data
   - Precipitation, temperature, humidity
   - Used for immediate spray decisions

2. **Forecast**
   ```
   https://api.weatherapi.com/v1/forecast.json
   ```
   - Up to 14 days forecast (using 5 days)
   - Rain probability, expected precipitation
   - Used for proactive rescheduling

## Best Practices

1. **Test Weather Integration**
   - Test with manual weather checks first
   - Verify rescheduling works as expected
   - Monitor logs for first few days

2. **Adjust Thresholds**
   - Start conservative (high sensitivity)
   - Adjust based on local conditions
   - Consider seasonal variations

3. **Monitor Reschedules**
   - Track how many schedules get postponed
   - Adjust MAX_RESCHEDULES if needed
   - Review cancelled schedules regularly

4. **Backup Plans**
   - System works without weather service
   - Local storage remains primary
   - Manual override always available

## Future Enhancements

Potential improvements:
- [ ] Wind speed checking (avoid spray drift)
- [ ] Temperature thresholds (optimal spray temp)
- [ ] Humidity considerations
- [ ] UV index for timing
- [ ] Multiple weather sources for reliability
- [ ] Machine learning for local patterns
- [ ] Weather-based spray recommendations
- [ ] Historical weather correlation analysis

---

**Status:** ✅ Fully Implemented
**Weather Service:** WeatherAPI.com
**Auto-Reschedule:** Enabled by default
**Max Reschedules:** 3 (configurable)
