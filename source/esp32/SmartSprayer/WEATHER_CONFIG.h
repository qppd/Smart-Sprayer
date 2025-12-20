#ifndef WEATHER_CONFIG_H
#define WEATHER_CONFIG_H

#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "WEATHER_CREDENTIALS.h"

// Function to check if it's raining currently
bool checkWeatherForRain() {
  HTTPClient http;
  http.begin(WEATHER_API_URL);
  int httpCode = http.GET();

  if (httpCode == 200) {
    String payload = http.getString();
    DynamicJsonDocument doc(2048);  // Adjust size for WeatherAPI response
    DeserializationError error = deserializeJson(doc, payload);

    if (error) {
      Serial.println("JSON parsing failed: " + String(error.c_str()));
      http.end();
      return false;
    }

    // Get current precipitation in mm
    float precip_mm = doc["current"]["precip_mm"] | 0.0;

    // Get weather condition text
    String condition = doc["current"]["condition"]["text"];

    // Check if it's raining currently (precip > 0 or condition indicates rain)
    if (precip_mm > 0.0 || condition.indexOf("rain") >= 0 || condition.indexOf("Rain") >= 0) {
      Serial.println("Currently raining: " + String(precip_mm) + "mm, condition: " + condition);
      http.end();
      return true;  // It's raining, don't spray
    }

    Serial.println("No rain currently: " + String(precip_mm) + "mm, condition: " + condition);
    http.end();
    return false;  // No rain
  } else {
    Serial.println("Weather API request failed with code: " + String(httpCode));
    http.end();
    return false;  // Assume no rain if API fails
  }
}

#endif // WEATHER_CONFIG_H