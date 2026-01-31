#include "GSM_CONFIG.h"
#include "RELAY_CONFIG.h"
#include "PINS_CONFIG.h"
#include "BUZZER_CONFIG.h"
#include "RTC_CONFIG.h"

void setup() {
  Serial.begin(9600);
  initGSM();
  initRELAY();
  initSR04();
  initBuzzer();
  initRTC();
}

void loop() {
  // Handle alarms
  Alarm.delay(10); // Allow alarms to trigger

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
      long dist = readDistance2();
      Serial.print("Distance 2: ");
      Serial.print(dist);
      Serial.println(" cm");
    } else if (command == "buzzer-on") {
      buzzerOn();
      Serial.println("Buzzer turned ON");
    } else if (command == "buzzer-off") {
      buzzerOff();
      Serial.println("Buzzer turned OFF");
    } else if (command == "buzzer-beep") {
      buzzerBeep();
      Serial.println("Buzzer beeped");
    } else if (command == "get-time") {
      String timeStr = getFormattedDateTime();
      Serial.print("Current time: ");
      Serial.println(timeStr);
    } else if (command == "set-time") {
      // Expected format: set-time_YYYY-MM-DD_HH:MM:SS
      // RPI will send this command to sync ESP32 time
      Serial.println("Time set via RPI command");
    } else if (command == "get-level") {
      long dist = readDistance();
      float level = calculateFillLevel(dist);
      float percentage = calculateFillPercentage(dist);
      Serial.print("Distance: ");
      Serial.print(dist);
      Serial.print(" cm, Filled: ");
      Serial.print(level);
      Serial.print(" cm, Percentage: ");
      Serial.print(percentage);
      Serial.println(" %");
    } else {
      Serial.println("Unknown command");
    }
  }
}