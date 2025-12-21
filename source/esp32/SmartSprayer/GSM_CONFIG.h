#ifndef GSM_CONFIG_H
#define GSM_CONFIG_H

#include <SoftwareSerial.h>
#include "GSM_RECIPIENTS.h"
#include "PINS_CONFIG.h"

#define PWR_KEY_PIN 3

SoftwareSerial sim(GSM_RX_PIN, GSM_TX_PIN); // RX, TX

void initGSM() {
  pinMode(PWR_KEY_PIN, OUTPUT);
  digitalWrite(PWR_KEY_PIN, HIGH);
  // Power on SIM800L
  digitalWrite(PWR_KEY_PIN, LOW);
  delay(1000);
  digitalWrite(PWR_KEY_PIN, HIGH);
  delay(5000); // Wait for module to boot
  sim.begin(9600);
  delay(1000);
  sim.println("AT");
  delay(1000);
  // Assume OK
}

void sendSMS(String number, String message) {
  sim.println("AT+CMGF=1");
  delay(100);
  sim.println("AT+CMGS=\"" + number + "\"");
  delay(100);
  sim.println(message);
  delay(100);
  sim.write(26); // Ctrl+Z
  delay(3000); // Wait for response
}

bool sendSMSWithResponse(String number, String message) {
  sim.println("AT+CMGF=1");
  delay(100);
  
  // Clear any previous responses
  while (sim.available()) sim.read();
  
  sim.println("AT+CMGS=\"" + number + "\"");
  delay(100);
  sim.println(message);
  delay(100);
  sim.write(26); // Ctrl+Z
  
  // Wait for response
  unsigned long startTime = millis();
  String response = "";
  
  while (millis() - startTime < 10000) {  // 10 second timeout
    while (sim.available()) {
      char c = sim.read();
      response += c;
      if (response.indexOf("OK") >= 0) {
        return true;
      }
      if (response.indexOf("ERROR") >= 0) {
        return false;
      }
    }
    delay(10);
  }
  
  return false;  // Timeout or no valid response
}

void sendSMSToAll(String message) {
  bool allSent = true;
  for (int i = 0; i < numRecipients; i++) {
    if (recipients[i] != "") {  // Only send to non-empty numbers
      if (!sendSMSWithResponse(recipients[i], message)) {
        Serial.print("Failed to send SMS to: ");
        Serial.println(recipients[i]);
        allSent = false;
      } else {
        Serial.print("SMS sent to: ");
        Serial.println(recipients[i]);
      }
      delay(5000); // delay between sends
    }
  }
  
  if (!allSent) {
    Serial.println("Some SMS messages failed to send");
  } else {
    Serial.println("All SMS messages sent successfully");
  }
}

bool sendSMSToAllWithStatus(String message) {
  bool allSent = true;
  for (int i = 0; i < numRecipients; i++) {
    if (recipients[i] != "") {
      if (!sendSMSWithResponse(recipients[i], message)) {
        allSent = false;
      }
      delay(5000);
    }
  }
  return allSent;
}

void checkNetwork() {
  sim.println("AT+CREG?");
  delay(100);
  // Response would be read, but for now, print to Serial
  while (sim.available()) {
    Serial.write(sim.read());
  }
}

#endif