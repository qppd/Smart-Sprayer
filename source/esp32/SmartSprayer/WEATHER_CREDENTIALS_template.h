#ifndef WEATHER_CREDENTIALS_H
#define WEATHER_CREDENTIALS_H

// Replace with your actual OpenWeatherMap API key (get it from https://openweathermap.org/api)
#define WEATHER_API_KEY ""

// Location for Philippines (e.g., Manila). Change to your specific city, e.g., "Cebu,PH" or use lat/lon like "10.3157,123.8854"
#define WEATHER_LOCATION ""

// API URL for 5-day forecast (includes rain data). Units in metric (Celsius, mm)
// Note: This is constructed using the API key and location above. Do not modify unless you know what you're doing.
#define WEATHER_API_URL "http://api.openweathermap.org/data/2.5/forecast?appid=" WEATHER_API_KEY "&q=" WEATHER_LOCATION "&units=metric"

#endif // WEATHER_CREDENTIALS_H