# firebase_credentials_template.py
# Firebase configuration template
# Copy this file to firebase_credentials.py and add your Firebase project credentials

FIREBASE_CONFIG = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
    "databaseURL": "https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com",
    "storageBucket": "YOUR_PROJECT_ID.appspot.com",
    "serviceAccount": "path/to/serviceAccountKey.json"  # Optional: for admin SDK
}

# Firebase Authentication (Optional)
FIREBASE_USER = {
    "email": "your-email@example.com",
    "password": "your-password"
}

# Weather API configuration (for weather check via RPI)
WEATHER_API_KEY = "64812e322c3f4b42af7135146252012"
WEATHER_LOCATION = "Manila"
WEATHER_API_URL = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={WEATHER_LOCATION}&aqi=no"

# Optional: 5-day forecast URL (for advanced weather prediction)
WEATHER_FORECAST_URL = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={WEATHER_LOCATION}&days=5&aqi=no"
