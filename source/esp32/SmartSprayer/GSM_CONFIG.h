#ifndef GSM_CONFIG_H
#define GSM_CONFIG_H

// #include <SoftwareSerial.h>  // Commented out for HardwareSerial
#include "PINS_CONFIG.h"

#define MAX_RECIPIENTS 10

HardwareSerial sim(1); // UART1 for ESP32

// ── GSM Network State ─────────────────────────────────────────────────────
enum GSMNetworkState {
  NETWORK_DISCONNECTED,   // Not registered, not searching
  NETWORK_SEARCHING,      // Searching for a network
  NETWORK_CONNECTED,      // Registered (home or roaming)
  NETWORK_DENIED,         // Registration denied
  NETWORK_RECONNECTING    // Actively attempting reconnection
};

GSMNetworkState gsmNetworkState   = NETWORK_DISCONNECTED;
bool            smsInProgress     = false;   // Reconnect guard: skip while sending SMS
unsigned long   lastReconnectAttempt = 0;   // millis() timestamp of last reconnect cycle
int             csqValue          = 99;      // Last RSSI reading (99 = unknown)
String          cregResponse      = "";     // Last raw +CREG stat field (e.g. "0,1")

// Dynamic recipients array (managed by RPI via serial commands)
String recipients[MAX_RECIPIENTS];
int numRecipients = 0;

// ── GSM Helper / Monitoring Functions ──────────────────────────────────────

String getSignalLevelString(int rssi) {
  if (rssi == 99) return "UNKNOWN";
  if (rssi <= 9)  return "POOR";
  if (rssi <= 14) return "WEAK";
  if (rssi <= 19) return "GOOD";
  return "EXCELLENT";
}

String getNetworkStateString() {
  switch (gsmNetworkState) {
    case NETWORK_CONNECTED:    return "CONNECTED";
    case NETWORK_SEARCHING:    return "SEARCHING";
    case NETWORK_DISCONNECTED: return "FAILED TO CONNECT";
    case NETWORK_DENIED:       return "REGISTRATION DENIED";
    case NETWORK_RECONNECTING: return "RECONNECTING";
    default:                   return "UNKNOWN";
  }
}

void readSignalStrength() {
  while (sim.available()) sim.read(); // Flush stale bytes
  sim.println("AT+CSQ");
  unsigned long t = millis();
  String resp = "";
  while (millis() - t < 3000) {
    while (sim.available()) resp += (char)sim.read();
    if (resp.indexOf("OK") >= 0 || resp.indexOf("ERROR") >= 0) break;
    delay(10);
  }
  int csqIdx = resp.indexOf("+CSQ:");
  if (csqIdx >= 0) {
    int commaIdx = resp.indexOf(',', csqIdx);
    if (commaIdx > csqIdx) {
      String rssiStr = resp.substring(csqIdx + 5, commaIdx);
      rssiStr.trim();
      csqValue = rssiStr.toInt();
    }
  }
  Serial.print("[GSM] Signal level: ");
  Serial.print(getSignalLevelString(csqValue));
  Serial.print(" (CSQ=");
  Serial.print(csqValue);
  Serial.println(")");
}

void printGSMStatus() {
  Serial.println("GSM STATUS");
  Serial.println("----------");
  Serial.print("Network: ");
  Serial.println(getNetworkStateString());
  Serial.print("Signal: ");
  Serial.print(getSignalLevelString(csqValue));
  Serial.print(" (CSQ: ");
  Serial.print(csqValue);
  Serial.println(")");
  Serial.print("Registration: ");
  Serial.println(cregResponse.length() > 0 ? cregResponse : "UNKNOWN");
  Serial.print("Reconnect: ");
  Serial.println(gsmNetworkState == NETWORK_RECONNECTING ? "ACTIVE" : "IDLE");
}

// Parse and print a +CDS delivery status report URC.
// Format (text mode): +CDS: <fo>,<mr>,[<ra>],[<tora>],<scts>,<dt>,<st>
// <st> == 0 => delivered; 32-63 => temporary error; 64+ => permanent error.
void handleDeliveryReport(const String& line) {
  // Extract message-reference (2nd comma-separated field after the colon)
  int colonIdx  = line.indexOf(':');
  int firstComma  = line.indexOf(',', colonIdx + 1);
  int secondComma = line.indexOf(',', firstComma + 1);
  String mr = "?";
  if (firstComma >= 0 && secondComma > firstComma) {
    mr = line.substring(firstComma + 1, secondComma);
    mr.trim();
  }

  // Extract delivery status (last field)
  int lastComma = line.lastIndexOf(',');
  String stStr  = (lastComma >= 0) ? line.substring(lastComma + 1) : "";
  stStr.trim();
  int st = stStr.toInt();

  Serial.print("[SMS DELIVERY] Msg-Ref=");
  Serial.print(mr);
  Serial.print("  Status=");
  if (st == 0) {
    Serial.println("DELIVERED");
  } else if (st >= 32 && st <= 63) {
    Serial.print("TEMPORARY ERROR (");
    Serial.print(st);
    Serial.println(") — SC still retrying");
  } else if (st >= 64) {
    Serial.print("PERMANENT FAILURE (");
    Serial.print(st);
    Serial.println(") — not delivered");
  } else {
    Serial.print("FORWARDED/PENDING (");
    Serial.print(st);
    Serial.println(")");
  }
}

void initGSM() {
  sim.begin(9600, SERIAL_8N1, GSM_RX_PIN, GSM_TX_PIN);
  delay(1000);
  sim.println("AT");
  delay(1000);
  // Set text mode — must be done before CNMI/CSMP so all URCs arrive as text
  sim.println("AT+CMGF=1");
  delay(500);
  // Route delivery status report URCs directly to the serial port (DS=2)
  sim.println("AT+CNMI=2,0,0,2,0");
  delay(500);
  // Enable SMS delivery reports: TP-SRR bit set, relative VP = 167 (~24 h)
  sim.println("AT+CSMP=49,167,0,0");
  delay(500);
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
  smsInProgress = true;
  sim.println("AT+CMGF=1");
  delay(100);
  sim.println("AT+CMGS=\"" + number + "\"");
  delay(100);
  sim.println(message);
  delay(100);
  sim.write(26); // Ctrl+Z
  delay(3000); // Wait for response
  smsInProgress = false;
}

bool sendSMSWithResponse(String number, String message) {
  // Step 1: Set text mode and wait for OK
  while (sim.available()) sim.read();  // flush stale bytes
  sim.println("AT+CMGF=1");
  unsigned long t0 = millis();
  String modeResp = "";
  while (millis() - t0 < 3000) {
    while (sim.available()) modeResp += (char)sim.read();
    if (modeResp.indexOf("OK") >= 0) break;
    delay(10);
  }
  if (modeResp.indexOf("OK") < 0) {
    Serial.println("[SMS] AT+CMGF=1 failed: " + modeResp);
    return false;
  }

  // Step 2: Send recipient and wait for ">" prompt
  while (sim.available()) sim.read();  // flush
  sim.println("AT+CMGS=\"" + number + "\"");
  unsigned long t1 = millis();
  String promptResp = "";
  while (millis() - t1 < 5000) {
    while (sim.available()) promptResp += (char)sim.read();
    if (promptResp.indexOf(">") >= 0) break;
    if (promptResp.indexOf("ERROR") >= 0) {
      Serial.println("[SMS] AT+CMGS error: " + promptResp);
      return false;
    }
    delay(10);
  }
  if (promptResp.indexOf(">") < 0) {
    Serial.println("[SMS] No '>' prompt received: " + promptResp);
    return false;
  }

  // Step 3: Send message body then Ctrl+Z
  sim.print(message);
  sim.write(26);  // Ctrl+Z

  // Step 4: Wait for +CMGS confirmation and OK
  unsigned long startTime = millis();
  String response = "";
  while (millis() - startTime < 10000) {
    while (sim.available()) {
      char c = sim.read();
      response += c;
      if (response.indexOf("OK") >= 0) {
        Serial.println("[SMS] Sent OK: " + response);
        return true;
      }
      if (response.indexOf("ERROR") >= 0) {
        Serial.println("[SMS] Send ERROR: " + response);
        return false;
      }
    }
    delay(10);
  }

  Serial.println("[SMS] Timeout waiting for OK. Response so far: " + response);
  return false;  // Timeout
}

void sendSMSToAll(String message) {
  if (numRecipients == 0) {
    Serial.println("[SMS] No recipients configured — SMS not sent.");
    return;
  }
  smsInProgress = true;
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
  smsInProgress = false;
}

bool sendSMSToAllWithStatus(String message) {
  if (numRecipients == 0) {
    Serial.println("[SMS] No recipients configured — SMS not sent.");
    return false;
  }
  smsInProgress = true;
  bool allSent = true;
  for (int i = 0; i < numRecipients; i++) {
    if (recipients[i] != "") {
      if (!sendSMSWithResponse(recipients[i], message)) {
        allSent = false;
      }
      delay(5000);
    }
  }
  smsInProgress = false;
  return allSent;
}

void checkNetwork() {
  while (sim.available()) sim.read(); // Flush stale bytes
  sim.println("AT+CREG?");
  unsigned long t = millis();
  String resp = "";
  while (millis() - t < 3000) {
    while (sim.available()) resp += (char)sim.read();
    if (resp.indexOf("OK") >= 0 || resp.indexOf("ERROR") >= 0) break;
    delay(10);
  }
  int cregIdx = resp.indexOf("+CREG:");
  if (cregIdx >= 0) {
    String cregPart = resp.substring(cregIdx + 6);
    cregPart.trim();
    int nlIdx = cregPart.indexOf('\n');
    if (nlIdx >= 0) cregPart = cregPart.substring(0, nlIdx);
    cregPart.trim();
    cregResponse = cregPart;

    // Extract stat: response may be "n,stat" (mode 1) or just "stat" (mode 0)
    int stat = -1;
    int commaIdx = cregPart.indexOf(',');
    if (commaIdx >= 0) {
      String statStr = cregPart.substring(commaIdx + 1);
      statStr.trim();
      stat = statStr.toInt();
    } else {
      stat = cregPart.toInt();
    }

    GSMNetworkState prevState = gsmNetworkState;
    switch (stat) {
      case 1:  gsmNetworkState = NETWORK_CONNECTED;    break; // Registered, home
      case 5:  gsmNetworkState = NETWORK_CONNECTED;    break; // Registered, roaming
      case 2:  gsmNetworkState = NETWORK_SEARCHING;    break; // Searching
      case 3:  gsmNetworkState = NETWORK_DENIED;       break; // Denied
      default: gsmNetworkState = NETWORK_DISCONNECTED; break; // 0 = not registered
    }

    if (prevState != NETWORK_CONNECTED && gsmNetworkState == NETWORK_CONNECTED) {
      Serial.println("[GSM] Network registered");
    } else if (prevState == NETWORK_CONNECTED && gsmNetworkState != NETWORK_CONNECTED) {
      Serial.println("[GSM] Network lost");
    }
  }
}

void attemptReconnect() {
  if (gsmNetworkState == NETWORK_CONNECTED) return;
  gsmNetworkState = NETWORK_RECONNECTING;
  Serial.println("[GSM] Attempting reconnection...");

  while (sim.available()) sim.read(); // Flush stale bytes

  // Force automatic operator selection to trigger fresh registration
  sim.println("AT+COPS=0");
  unsigned long t = millis();
  String resp = "";
  while (millis() - t < 3000) {
    while (sim.available()) resp += (char)sim.read();
    if (resp.indexOf("OK") >= 0 || resp.indexOf("ERROR") >= 0) break;
    delay(10);
  }

  // Give the module a moment to start searching before checking status
  delay(2000);
  checkNetwork();
}

#endif
