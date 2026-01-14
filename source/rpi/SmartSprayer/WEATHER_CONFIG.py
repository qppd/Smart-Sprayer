# WEATHER_CONFIG.py
# Weather API configuration for Raspberry Pi version


WEATHER_API_KEY = ""
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
LOCATION = ""

import requests

def get_weather():
	params = {"q": LOCATION, "appid": WEATHER_API_KEY, "units": "metric"}
	response = requests.get(WEATHER_API_URL, params=params)
	if response.status_code == 200:
		return response.json()
	else:
		return None
