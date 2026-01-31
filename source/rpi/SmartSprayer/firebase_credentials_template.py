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
WEATHER_API_KEY = "YOUR_WEATHER_API_KEY"
WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json?key=YOUR_WEATHER_API_KEY&q=YOUR_LOCATION&aqi=no"
