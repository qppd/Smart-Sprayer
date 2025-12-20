#include "LCD_CONFIG.h"
#include "GSM_CONFIG.h"
#include "RELAY_CONFIG.h"
#include "SR04_CONFIG.h"
#include "WIFI_CONFIG.h"
#include "FIREBASE_CONFIG.h"
#include "NTP_CONFIG.h"

void setup() {
  Serial.begin(9600);
  initLCD();
  initGSM();
  initRELAY();
  initSR04();
  initWIFI();
  initFIREBASE();
  initNTP();
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "operate-relay1_on") {
      operateRELAY(RELAY_1, true);
      Serial.println("Relay 1 turned ON");
    } else if (command == "operate-relay1_off") {
      operateRELAY(RELAY_1, false);
      Serial.println("Relay 1 turned OFF");
    } else if (command == "operate-relay2_on") {
      operateRELAY(RELAY_2, true);
      Serial.println("Relay 2 turned ON");
    } else if (command == "operate-relay2_off") {
      operateRELAY(RELAY_2, false);
      Serial.println("Relay 2 turned OFF");
    } else if (command == "send-sms") {
      sendSMS("+1234567890", "Test SMS from Smart Sprayer");
      Serial.println("SMS sent");
    } else if (command == "send-sms-to-all") {
      sendSMSToAll("Test SMS to all from Smart Sprayer");
      Serial.println("SMS sent to all");
    } else if (command == "check-network") {
      checkNetwork();
      Serial.println("Network check initiated");
    } else if (command == "get-distance1") {
      long dist = readDistance();
      Serial.print("Distance 1: ");
      Serial.print(dist);
      Serial.println(" cm");
    } else if (command == "get-distance2") {
      long dist = readDistance();
      Serial.print("Distance 2: ");
      Serial.print(dist);
      Serial.println(" cm");
    } else if (command == "test-display") {
      clearLCD();
      setLCDText("Test Display", 0, 0);
      setLCDText("Smart Sprayer", 0, 1);
      Serial.println("LCD test displayed");
    } else {
      Serial.println("Unknown command");
    }
  }
}