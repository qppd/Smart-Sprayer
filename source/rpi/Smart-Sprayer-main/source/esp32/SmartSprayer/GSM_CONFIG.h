#ifndef GSM_CONFIG_H
#define GSM_CONFIG_H

// #include <SoftwareSerial.h>  // Commented out for HardwareSerial
#include "PINS_CONFIG.h"

#define MAX_RECIPIENTS 10

HardwareSerial sim(1); // UART1 for ESP32

// Dynamic recipients array (managed by RPI via serial commands)
String recipients[MAX_RECIPIENTS];
int numRecipients = 0;

void initGSM() {
  sim.begin(9600, SERIAL_8N1, GSM_RX_PIN, GSM_TX_PIN);
  delay(1000);
  sim.println("AT");
  delay(1000);
  // Assume OK
}

// Test GSM communication
void testGSMConnection() {
  Serial.println("[GSM] Sending AT command...");
  sim.println("AT");
}

// Add recipient via serial command
void addRecipient(String number) {
  if (numRecipients < MAX_RECIPIENTS) {
    recipients[numRecipients] = number;
    numRecipients++;
    Serial.print("Recipient added: ");
    Serial.println(number);
  } else {
    Serial.println("Max recipients reached");
  }
}

// Remove recipient via serial command
void removeRecipient(String number) {
  for (int i = 0; i < numRecipients; i++) {
    if (recipients[i] == number) {
      // Shift remaining recipients
      for (int j = i; j < numRecipients - 1; j++) {
        recipients[j] = recipients[j + 1];
      }
      recipients[numRecipients - 1] = "";
      numRecipients--;
      Serial.print("Recipient removed: ");
      Serial.println(number);
      return;
    }
  }
  Serial.println("Recipient not found");
}

// Clear all recipients
void clearRecipients() {
  for (int i = 0; i < MAX_RECIPIENTS; i++) {
    recipients[i] = "";
  }
  numRecipients = 0;
  Serial.println("All recipients cleared");
}

// List all recipients
void listRecipients() {
  Serial.print("Recipients (");
  Serial.print(numRecipients);
  Serial.println("):");
  for (int i = 0; i < numRecipients; i++) {
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.println(recipients[i]);
  }
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