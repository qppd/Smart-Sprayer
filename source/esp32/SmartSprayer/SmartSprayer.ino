#include "LCD_CONFIG.h"
#include "GSM_CONFIG.h"
#include "RELAY_CONFIG.h"
#include "SR04_CONFIG.h"
#include "WIFI_CONFIG.h"
#include "FIREBASE_CONFIG.h"
#include "NTP_CONFIG.h"
#include "WEATHER_CONFIG.h"
#include "PINS_CONFIG.h"
#include "BUZZER_CONFIG.h"
#include "LED_CONFIG.h"

void setup() {
  Serial.begin(9600);
  initLCD();
  initGSM();
  initRELAY();
  initSR04();
  initWIFI();
  initFIREBASE();
  initNTP();
  initBuzzer();
  initLEDs();
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
    } else if (command == "led-ok") {
      setSystemOK();
      Serial.println("System OK LED ON");
    } else if (command == "led-error") {
      setSystemError();
      Serial.println("System Error LED ON");
    } else if (command == "led-warning") {
      setSystemWarning();
      Serial.println("System Warning LEDs ON");
    } else if (command == "led-clear") {
      clearSystemLEDs();
      Serial.println("System LEDs cleared");
    } else if (command == "check-weather") {
      bool willRain = checkWeatherForRain();
      if (willRain) {
        Serial.println("Weather check: Rain expected today - avoid spraying");
      } else {
        Serial.println("Weather check: No rain expected today - safe to spray");
      }
    } else {
      Serial.println("Unknown command");
    }
  }
}