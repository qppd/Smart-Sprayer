#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#include <WiFi.h>
#include <WiFiManager.h>
#include "NTP_CONFIG.h"

void initWIFI() {
    WiFiManager wifiManager;
    // Try to connect to saved WiFi, else start AP for config
    if (!wifiManager.autoConnect("SmartSprayer-ESP32", "smartsprayer123")) {
        Serial.println("Failed to connect and hit timeout");
        delay(3000);
        ESP.restart();
        delay(5000);
    }
    Serial.println("WiFi connected successfully!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());

    // Initialize NTP after successful WiFi connection
    initNTP();
}

#endif // WIFI_CONFIG_H