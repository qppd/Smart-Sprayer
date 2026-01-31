#include "GSM_CONFIG.h"
#include "RELAY_CONFIG.h"
#include "PINS_CONFIG.h"
#include "BUZZER_CONFIG.h"
#include "RTC_CONFIG.h"
#include "SR04_CONFIG.h"

void setup() {
  Serial.begin(9600);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("    SMART SPRAYER ESP32 - STARTING");
  Serial.println("========================================");
  
  Serial.print("[INIT] GSM Module... ");
  initGSM();
  Serial.println("READY");
  
  Serial.print("[INIT] Relays... ");
  initRELAY();
  Serial.println("READY");
  
  Serial.print("[INIT] Ultrasonic Sensors... ");
  initSR04();
  Serial.println("READY");
  
  Serial.print("[INIT] Buzzer... ");
  initBuzzer();
  Serial.println("READY");
  
  Serial.print("[INIT] RTC... ");
  initRTC();
  Serial.println("READY");
  
  Serial.println("========================================");
  Serial.println(" ALL SYSTEMS INITIALIZED - WAITING CMD");
  Serial.println("========================================\n");
}

void loop() {
  // Handle alarms
  Alarm.delay(10);

  // Continuously check for SIM800L responses
  if (sim.available() > 0) {
    String simResponse = sim.readStringUntil('\n');
    simResponse.trim();
    if (simResponse.length() > 0) {
      Serial.print("[SIM800L] ");
      Serial.println(simResponse);
    }
  }

  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    Serial.print("[CMD] Received: ");
    Serial.println(command);
    
    if (command == "operate-relay1_on") {
      Serial.print("[RELAY] Turning Relay 1 ON... ");
      operateRELAY(RELAY_1, true);
      Serial.println("OK");
    } else if (command == "operate-relay1_off") {
      Serial.print("[RELAY] Turning Relay 1 OFF... ");
      operateRELAY(RELAY_1, false);
      Serial.println("OK");
    } else if (command == "operate-relay2_on") {
      Serial.print("[RELAY] Turning Relay 2 ON... ");
      operateRELAY(RELAY_2, true);
      Serial.println("OK");
    } else if (command == "operate-relay2_off") {
      Serial.print("[RELAY] Turning Relay 2 OFF... ");
      operateRELAY(RELAY_2, false);
      Serial.println("OK");
    } else if (command == "send-sms") {
      Serial.println("[GSM] Sending test SMS...");
      sendSMS("+1234567890", "Test SMS from Smart Sprayer");
      Serial.println("[GSM] Test SMS sent");
    } else if (command == "send-sms-to-all") {
      Serial.println("[GSM] Sending SMS to all recipients...");
      sendSMSToAll("Test SMS to all from Smart Sprayer");
      Serial.println("[GSM] Broadcast complete");
    } else if (command == "test-gsm") {
      testGSMConnection();
    } else if (command == "check-network") {
      Serial.println("[GSM] Checking network status...");
      checkNetwork();
    } else if (command == "get-distance1") {
      Serial.print("[SR04] Reading Sensor 1... ");
      long dist = readDistance();
      Serial.print(dist);
      Serial.println(" cm");
    } else if (command == "get-distance2") {
      Serial.print("[SR04] Reading Sensor 2... ");
      long dist = readDistance2();
      Serial.print(dist);
      Serial.println(" cm");
    } else if (command == "buzzer-on") {
      Serial.print("[BUZZER] Turning ON... ");
      buzzerOn();
      Serial.println("OK");
    } else if (command == "buzzer-off") {
      Serial.print("[BUZZER] Turning OFF... ");
      buzzerOff();
      Serial.println("OK");
    } else if (command == "buzzer-beep") {
      Serial.print("[BUZZER] Beeping... ");
      buzzerBeep();
      Serial.println("OK");
    } else if (command == "get-time") {
      Serial.print("[RTC] Reading time... ");
      String timeStr = getFormattedDateTime();
      Serial.println(timeStr);
    } else if (command.startsWith("set-rtc_")) {
      // Format: set-rtc_YY_MM_DD_HH_MM_SS
      // Example: set-rtc_26_02_01_14_30_00 (2026-02-01 14:30:00)
      String params = command.substring(8);
      int values[6];
      int idx = 0;
      int lastPos = 0;
      
      for (int i = 0; i < params.length() && idx < 6; i++) {
        if (params[i] == '_' || i == params.length() - 1) {
          int endPos = (i == params.length() - 1) ? i + 1 : i;
          values[idx++] = params.substring(lastPos, endPos).toInt();
          lastPos = i + 1;
        }
      }
      
      if (idx == 6) {
        setRTCTimeManual(values[0], values[1], values[2], values[3], values[4], values[5]);
      } else {
        Serial.println("[ERROR] Invalid format. Use: set-rtc_YY_MM_DD_HH_MM_SS");
      }
    } else if (command == "set-time") {
      Serial.println("[RTC] Time sync from RPI acknowledged");
    } else if (command == "get-level") {
      Serial.print("[SR04] Reading tank level... ");
      long dist = readDistance();
      float level = calculateFillLevel(dist);
      float percentage = calculateFillPercentage(dist);
      Serial.print("Dist=");
      Serial.print(dist);
      Serial.print("cm Fill=");
      Serial.print(level);
      Serial.print("cm (");
      Serial.print(percentage);
      Serial.println("%)");
    } else if (command.startsWith("add-recipient_")) {
      String number = command.substring(14);
      Serial.print("[GSM] Adding recipient... ");
      addRecipient(number);
    } else if (command.startsWith("remove-recipient_")) {
      String number = command.substring(17);
      Serial.print("[GSM] Removing recipient... ");
      removeRecipient(number);
    } else if (command == "clear-recipients") {
      Serial.print("[GSM] Clearing all recipients... ");
      clearRecipients();
    } else if (command == "list-recipients") {
      Serial.println("[GSM] Listing recipients:");
      listRecipients();
    } else if (command.startsWith("send-sms-custom_")) {
      int firstUnderscore = command.indexOf('_');
      int secondUnderscore = command.indexOf('_', firstUnderscore + 1);
      if (secondUnderscore > 0) {
        String number = command.substring(firstUnderscore + 1, secondUnderscore);
        String message = command.substring(secondUnderscore + 1);
        Serial.print("[GSM] Sending custom SMS to ");
        Serial.print(number);
        Serial.print("... ");
        sendSMS(number, message);
        Serial.println("OK");
      } else {
        Serial.println("[ERROR] Invalid SMS format");
      }
    } else {
      Serial.print("[ERROR] Unknown command: ");
      Serial.println(command);
    }
  }
}