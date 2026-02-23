#!/usr/bin/env python3
"""Test script for weather caching functionality"""

from core.weather_service import get_weather_service

print("=" * 60)
print("WEATHER CACHE TEST")
print("=" * 60)

# Get weather service
ws = get_weather_service()

print(f"\n1. Weather service available: {ws.available}")

if ws.available:
    # Get cached weather
    print("\n2. Fetching weather data (with hourly cache)...")
    weather = ws.get_current_weather_cached()
    
    if weather:
        print("\n✓ Weather data retrieved successfully:")
        print(f"   Temperature: {weather.get('temperature_c')}°C")
        print(f"   Feels like: {weather.get('feels_like_c')}°C")
        print(f"   Condition: {weather.get('condition')}")
        print(f"   Humidity: {weather.get('humidity')}%")
        print(f"   Wind: {weather.get('wind_kph')} kph")
        print(f"   Rain: {weather.get('precip_mm')} mm")
        print(f"   UV Index: {weather.get('uv')}")
        
        print(f"\n3. Cache information:")
        print(f"   Cache age: {ws.get_cache_age()}")
        print(f"   Cached at hour: {ws.last_cache_hour}")
        print(f"   Cache timestamp: {ws.cache_timestamp}")
        
        print("\n4. Testing cache persistence (should use cached data)...")
        weather2 = ws.get_current_weather_cached()
        print(f"   Second call returned data: {weather2 is not None}")
        print(f"   Still using same cache: {ws.get_cache_age()}")
    else:
        print("✗ Failed to retrieve weather data")
else:
    print("\n✗ Weather service not available")
    print("   Make sure firebase_credentials.py has WEATHER_API_KEY configured")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
