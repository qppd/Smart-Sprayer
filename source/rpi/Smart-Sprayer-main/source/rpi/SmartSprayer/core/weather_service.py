# weather_service.py
# Weather checking service for Smart Sprayer (RPI handles weather API calls)

import requests
from typing import Dict, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path to ensure firebase_credentials can be imported
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from firebase_credentials import WEATHER_API_KEY, WEATHER_API_URL, WEATHER_FORECAST_URL, WEATHER_LOCATION
    # Verify that credentials are actually loaded (not None or empty)
    if WEATHER_API_KEY and WEATHER_API_URL and WEATHER_FORECAST_URL:
        WEATHER_AVAILABLE = True
    else:
        print("Warning: Weather API credentials are empty or None")
        WEATHER_AVAILABLE = False
        WEATHER_LOCATION = None
except ImportError as e:
    print(f"Warning: Weather API credentials not found - {e}")
    WEATHER_AVAILABLE = False
    WEATHER_API_KEY = None
    WEATHER_API_URL = None
    WEATHER_FORECAST_URL = None
    WEATHER_LOCATION = None
except Exception as e:
    print(f"Warning: Error loading Weather API credentials - {e}")
    WEATHER_AVAILABLE = False
    WEATHER_API_KEY = None
    WEATHER_API_URL = None
    WEATHER_FORECAST_URL = None
    WEATHER_LOCATION = None


class WeatherService:
    """Weather service to check rain conditions"""
    
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.api_url = WEATHER_API_URL
        self.forecast_url = WEATHER_FORECAST_URL
        self.available = WEATHER_AVAILABLE and self.api_key and self.api_url
        self.last_check = None
        self.last_result = None
        
        # Hourly cache for dashboard display
        self.cached_weather = None
        self.cache_timestamp = None
        self.last_cache_hour = None
    
    def check_weather_for_rain(self) -> bool:
        """
        Check if it's currently raining or rain is expected
        Returns True if rain detected (should avoid spraying)
        Returns False if no rain (safe to spray)
        """
        if not self.available:
            print("Weather API not configured")
            return False  # Assume safe to spray if weather check unavailable
        
        try:
            response = requests.get(self.api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get current precipitation
                current = data.get('current', {})
                precip_mm = current.get('precip_mm', 0.0)
                condition = current.get('condition', {}).get('text', '')
                
                # Check if it's raining
                is_raining = precip_mm > 0.0 or 'rain' in condition.lower()
                
                self.last_check = datetime.now().isoformat()
                self.last_result = {
                    'is_raining': is_raining,
                    'precip_mm': precip_mm,
                    'condition': condition,
                    'timestamp': self.last_check
                }
                
                if is_raining:
                    print(f"Weather: Raining ({precip_mm}mm, {condition})")
                else:
                    print(f"Weather: No rain ({condition})")
                
                return is_raining
            else:
                print(f"Weather API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Weather check failed: {e}")
            return False  # Assume safe to spray if check fails
    
    def get_weather_data(self) -> Optional[Dict]:
        """Get detailed weather data"""
        if not self.available:
            return None
        
        try:
            response = requests.get(self.api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current', {})
                
                weather_data = {
                    'temperature_c': current.get('temp_c'),
                    'temperature_f': current.get('temp_f'),
                    'humidity': current.get('humidity'),
                    'condition': current.get('condition', {}).get('text'),
                    'wind_kph': current.get('wind_kph'),
                    'precip_mm': current.get('precip_mm'),
                    'cloud': current.get('cloud'),
                    'feels_like_c': current.get('feelslike_c'),
                    'uv': current.get('uv'),
                    'timestamp': datetime.now().isoformat()
                }
                
                return weather_data
            else:
                return None
                
        except Exception as e:
            print(f"Error getting weather data: {e}")
            return None
    
    def get_last_result(self) -> Optional[Dict]:
        """Get last weather check result"""
        return self.last_result
    
    def check_forecast_for_rain(self, hours_ahead: int = 24) -> bool:
        """
        Check if rain is expected in the next X hours
        Returns True if rain expected (should reschedule)
        Returns False if no rain (safe to spray)
        """
        if not self.available or not self.forecast_url:
            print("Weather forecast API not configured")
            return False
        
        try:
            response = requests.get(self.forecast_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecast = data.get('forecast', {}).get('forecastday', [])
                
                if not forecast:
                    return False
                
                # Check current day and next day
                for day in forecast[:2]:  # Check today and tomorrow
                    day_data = day.get('day', {})
                    
                    # Check for rain probability
                    daily_chance_of_rain = day_data.get('daily_chance_of_rain', 0)
                    daily_will_it_rain = day_data.get('daily_will_it_rain', 0)
                    total_precip_mm = day_data.get('totalprecip_mm', 0.0)
                    
                    # Rain expected if:
                    # - High chance of rain (>50%)
                    # - API says it will rain
                    # - Expected precipitation > 1mm
                    if daily_chance_of_rain > 50 or daily_will_it_rain == 1 or total_precip_mm > 1.0:
                        print(f"Rain forecast: {daily_chance_of_rain}% chance, {total_precip_mm}mm expected")
                        return True
                
                print("Forecast: No significant rain expected")
                return False
            else:
                print(f"Weather forecast API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Forecast check failed: {e}")
            return False
    
    def should_update_cache(self) -> bool:
        """Check if cache should be updated (every hour on the hour)"""
        now = datetime.now()
        current_hour = now.hour
        
        # Update if no cache exists or if we've moved to a new hour
        if self.last_cache_hour is None or current_hour != self.last_cache_hour:
            return True
        return False
    
    def get_current_weather_cached(self) -> Optional[Dict]:
        """
        Get current weather data with hourly caching
        Updates only at the top of each hour (7am, 8am, 9am, etc.)
        """
        if not self.available:
            return None
        
        # Check if we need to update the cache
        if self.should_update_cache():
            weather_data = self.get_weather_data()
            if weather_data:
                self.cached_weather = weather_data
                self.cache_timestamp = datetime.now()
                self.last_cache_hour = self.cache_timestamp.hour
                print(f"Weather cache updated at {self.cache_timestamp.strftime('%I:%M %p')}")
        
        return self.cached_weather
    
    def get_cache_age(self) -> Optional[str]:
        """Get the age of the cached data in human-readable format"""
        if self.cache_timestamp is None:
            return None
        
        delta = datetime.now() - self.cache_timestamp
        minutes = int(delta.total_seconds() / 60)
        
        if minutes < 1:
            return "Just now"
        elif minutes == 1:
            return "1 minute ago"
        elif minutes < 60:
            return f"{minutes} minutes ago"
        else:
            hours = minutes // 60
            if hours == 1:
                return "1 hour ago"
            else:
                return f"{hours} hours ago"


# Global weather service instance
_weather_service = None

def get_weather_service() -> WeatherService:
    """Get the global weather service instance"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
        # Log status
        if _weather_service.available:
            print("✓ Weather service initialized successfully")
            print(f"  API Key: {WEATHER_API_KEY[:20]}..." if WEATHER_API_KEY else "  API Key: None")
            print(f"  Location: {WEATHER_LOCATION if WEATHER_LOCATION else 'Not specified'}")
        else:
            print("✗ Weather service initialized but API not available")
    return _weather_service
