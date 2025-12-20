#ifndef WEATHER_CONFIG_H
#define WEATHER_CONFIG_H

#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "WEATHER_CREDENTIALS.h"

// Function to check if it's going to rain today
bool checkWeatherForRain() {
  HTTPClient http;
  http.begin(WEATHER_API_URL);
  int httpCode = http.GET();

  if (httpCode == 200) {
    String payload = http.getString();
    DynamicJsonDocument doc(4096);  // Adjust size if needed for full response
    DeserializationError error = deserializeJson(doc, payload);

    if (error) {
      Serial.println("JSON parsing failed: " + String(error.c_str()));
      http.end();
      return false;
    }

    // Get current date in YYYY-MM-DD format using NTP
    time_t now = time(nullptr);
    struct tm *timeinfo = localtime(&now);
    char dateStr[11];
    strftime(dateStr, sizeof(dateStr), "%Y-%m-%d", timeinfo);
    String todayDate = String(dateStr);

    // Parse the forecast list
    JsonArray list = doc["list"];
    for (JsonObject forecast : list) {
      String dt_txt = forecast["dt_txt"];
      if (dt_txt.startsWith(todayDate)) {
        // Check for rain (mm in last 3 hours) or probability of precipitation (pop > 0.5 means >50% chance)
        float rainAmount = forecast["rain"]["3h"] | 0.0;  // Default to 0 if no rain key
        float pop = forecast["pop"] | 0.0;  // Probability of precipitation

        if (rainAmount > 0.0 || pop > 0.5) {
          Serial.println("Rain expected today: " + String(rainAmount) + "mm or " + String(pop * 100) + "% chance");
          http.end();
          return true;  // It's going to rain
        }
      }
    }
    Serial.println("No rain expected today");
  } else {
    Serial.println("Weather API request failed with code: " + String(httpCode));
  }
  http.end();
  return false;  // No rain
}

#endif // WEATHER_CONFIG_H