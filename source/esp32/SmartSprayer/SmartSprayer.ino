#include "LCD_CONFIG.h"
#include "GSM_CONFIG.h"
#include "RELAY_CONFIG.h"
#include "WIFI_CONFIG.h"
#include "FIREBASE_CONFIG.h"
#include "NTP_CONFIG.h"
#include "WEATHER_CONFIG.h"
#include "PINS_CONFIG.h"
#include "BUZZER_CONFIG.h"
#include "LED_CONFIG.h"
#include "BUTTON_CONFIG.h"
#include "RTC_CONFIG.h"

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
  initBUTTONS();
  initRTC();

  // Sync RTC with NTP once during initialization
  syncRTCWithNTP();
}

void loop() {
  // Handle button inputs
  setInputFlags();
  resolveInputFlags();

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
    } else if (command == "set-leds") {
      // Example: set-leds 1 0 (OK on, Error off)
      int ok_state = 1;
      int error_state = 0;
      setSystemLEDs(ok_state, error_state);
      Serial.println("System LEDs set manually");
    } else if (command == "check-weather") {
      bool willRain = checkWeatherForRain();
      if (willRain) {
        Serial.println("Weather check: Rain expected today - avoid spraying");
      } else {
        Serial.println("Weather check: No rain expected today - safe to spray");
      }
    } else if (command == "clear-lcd") {
      clearLCD();
      Serial.println("LCD cleared");
    } else if (command == "test-lcd") {
      setLCDText("Smart Sprayer", 0, 0);
      setLCDText("Test Message", 0, 1);
      setLCDText("System OK", 0, 2);
      Serial.println("LCD test display set");
    } else if (command == "get-time") {
      String timeStr = getFormattedDateTime();
      Serial.print("Current time: ");
      Serial.println(timeStr);
    } else if (command == "get-timestamp") {
      unsigned long ts = getNTPTimestamp();
      Serial.print("NTP Timestamp: ");
      Serial.println(ts);
    } else if (command == "get-timestamp-fallback") {
      unsigned long ts = getNTPTimestampWithFallback();
      Serial.print("NTP Timestamp (with fallback): ");
      Serial.println(ts);
    } else if (command == "get-log-prefix") {
      String prefix = getCurrentLogPrefix();
      Serial.print("Log prefix: ");
      Serial.println(prefix);
    } else if (command == "get-datetime-fallback") {
      String dt = getFormattedDateTimeWithFallback();
      Serial.print("DateTime (with fallback): ");
      Serial.println(dt);
    } else if (command == "check-ntp") {
      bool synced = isNTPSynced();
      Serial.print("NTP Synced: ");
      Serial.println(synced ? "Yes" : "No");
    } else if (command == "update-ntp") {
      getNTPDate();
      Serial.println("NTP date updated");
    } else if (command == "wifi-reset") {
      Serial.println("Resetting WiFi settings...");
      resetWiFiSettings();
    } else if (command == "button-status") {
      bool pressed = isButtonPressed();
      Serial.print("Button pressed: ");
      Serial.println(pressed ? "Yes" : "No");
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