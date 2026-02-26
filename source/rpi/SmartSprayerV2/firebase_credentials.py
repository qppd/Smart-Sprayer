# firebase_credentials.py
# Firebase configuration for Smart Sprayer
# DO NOT COMMIT THIS FILE - Already in .gitignore

FIREBASE_CONFIG = {
    "apiKey": "AIzaSyB8MpkxNgJHCGGB8MtXne1fkPhspF7lpfw",
    "authDomain": "smart-sprayer-154fa.firebaseapp.com",
    "databaseURL": "https://smart-sprayer-154fa-default-rtdb.firebaseio.com",
    "storageBucket": "smart-sprayer-154fa.appspot.com"
}

# Firebase Authentication credentials
FIREBASE_USER = {
    "email": "quezon.province.pd@gmail.com",
    "password": "Admin1+"
}

# Weather API configuration
WEATHER_API_KEY = "64812e322c3f4b42af7135146252012"
WEATHER_LOCATION = "Kulapi, Lucban, Quezon"
WEATHER_API_URL = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={WEATHER_LOCATION}&aqi=no"
WEATHER_FORECAST_URL = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={WEATHER_LOCATION}&days=5&aqi=no"

# Note: To get your apiKey:
# 1. Go to Firebase Console: https://console.firebase.google.com/
# 2. Select project: smart-sprayer-154fa
# 3. Go to Project Settings (gear icon)
# 4. Scroll down to "Your apps" section
# 5. If no web app exists, click "Add app" and select Web (</>) 
# 6. Copy the apiKey from the config object
