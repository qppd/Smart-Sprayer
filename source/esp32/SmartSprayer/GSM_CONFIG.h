#ifndef GSM_CONFIG_H
#define GSM_CONFIG_H

#include <SoftwareSerial.h>
#include "GSM_RECIPIENTS.h"
#include "PINS_CONFIG.h"

SoftwareSerial sim(GSM_RX_PIN, GSM_TX_PIN); // RX, TX

void initGSM() {
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
}

void sendSMSToAll(String message) {
  for (int i = 0; i < numRecipients; i++) {
    if (recipients[i] != "") {  // Only send to non-empty numbers
      sendSMS(recipients[i], message);
      delay(5000); // delay between sends
    }
  }
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