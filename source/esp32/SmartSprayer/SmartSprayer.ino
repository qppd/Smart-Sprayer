#include "PINS_CONFIG.h"
#include "GSM_CONFIG.h"
#include "RELAY_CONFIG.h"
#include "BUZZER_CONFIG.h"
#include "RTC_CONFIG.h"
#include "SR04_CONFIG.h"

// ============================================
// FRAMED PROTOCOL FUNCTIONS
// ============================================

// Calculate XOR checksum for framed protocol
uint8_t calculateChecksum(const String& data) {
  uint8_t checksum = 0;
  for (unsigned int i = 0; i < data.length(); i++) {
    checksum ^= data[i];
  }
  return checksum;
}

// Send framed response with checksum
void sendFramedResponse(const String& command, const String& data) {
  String payload = command + ":" + data;
  uint8_t checksum = calculateChecksum(payload);
  
  Serial.print("<");
  Serial.print(payload);
  Serial.print(":");
  Serial.print(checksum, HEX);
  Serial.println(">");
}

// Check if command is a framed command (starts with <)
bool isFramedCommand(const String& cmd) {
  return cmd.startsWith("<") && cmd.endsWith(">");
}

// Parse framed command and validate checksum
bool parseFramedCommand(const String& frame, String& command, String& data) {
  // Remove < and >
  String content = frame.substring(1, frame.length() - 1);
  
  // Find last colon (before checksum)
  int lastColon = content.lastIndexOf(':');
  if (lastColon < 0) return false;
  
  // Extract checksum
  String checksumStr = content.substring(lastColon + 1);
  String payload = content.substring(0, lastColon);
  
  // Validate checksum
  uint8_t receivedChecksum = strtol(checksumStr.c_str(), NULL, 16);
  uint8_t calculatedChecksum = calculateChecksum(payload);
  
  if (receivedChecksum != calculatedChecksum) {
    Serial.println("[ERROR] Checksum mismatch");
    return false;
  }
  
  // Parse command and data
  int firstColon = payload.indexOf(':');
  if (firstColon < 0) {
    command = payload;
    data = "";
  } else {
    command = payload.substring(0, firstColon);
    data = payload.substring(firstColon + 1);
  }
  
  return true;
}

// ============================================
// NON-BLOCKING SPRAY STATE MACHINE GLOBALS
// ============================================

// Spray state — updated atomically from loop(), never from an ISR.
struct SprayState {
  bool          active     = false;
  int           relay      = 0;
  int           volume     = 0;
  String        spray_type = "";
  unsigned long end_ms     = 0;
};
static SprayState spray_state;

// ============================================
// FIXED-SIZE SERIAL LINE BUFFER
// ============================================
// Replaces Serial.readStringUntil('\n') to avoid:
//   - Partial reads when bytes arrive across loop() iterations
//   - Heap fragmentation from dynamic String growth
//   - UART RX buffer overflow when ESP32 is "busy"
#define CMD_BUF_SIZE 256
static char cmd_buf[CMD_BUF_SIZE];
static int  cmd_len  = 0;
static bool cmd_ready = false;

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
  // Handle alarms (non-blocking 10 ms yield for TimeAlarms library)
  Alarm.delay(10);

  // ── NON-BLOCKING SPRAY TIMER ─────────────────────────────────────────────
  // Check if an active spray has reached its end time.
  // Uses signed cast to handle millis() rollover correctly.
  if (spray_state.active && (long)(millis() - spray_state.end_ms) >= 0) {
    // Turn relay OFF immediately.
    if (spray_state.relay == 1) {
      operateRELAY(RELAY_1, false);
    } else {
      operateRELAY(RELAY_2, false);
    }
    Serial.print("[SPRAY] Relay ");
    Serial.print(spray_state.relay);
    Serial.println(" OFF");

    // Send completion ACK to RPI BEFORE slow SMS so RPI can proceed.
    Serial.println("ACK:SPRAY_DONE");

    buzzerBeep(200);
    spray_state.active = false;
  }

  // ── GSM NETWORK RECONNECT CHECK ──────────────────────────────────────────
  // Rate-limited to once every 15 seconds. Skipped while an SMS is in progress.
  if (!smsInProgress && (long)(millis() - lastReconnectAttempt) >= 15000L) {
    lastReconnectAttempt = millis();
    checkNetwork();
    if (gsmNetworkState == NETWORK_DISCONNECTED ||
        gsmNetworkState == NETWORK_SEARCHING    ||
        gsmNetworkState == NETWORK_DENIED) {
      attemptReconnect();
    } else {
      readSignalStrength();
    }
  }

  // ── SIM800L unsolicited responses ────────────────────────────────────────
  if (sim.available() > 0) {
    String simResponse = sim.readStringUntil('\n');
    simResponse.trim();
    if (simResponse.length() > 0) {
      Serial.print("[SIM800L] ");
      Serial.println(simResponse);
      // Delivery status report from network
      if (simResponse.startsWith("+CDS:")) {
        handleDeliveryReport(simResponse);
      }
    }
  }

  // ── FIXED-SIZE SERIAL LINE BUFFER ────────────────────────────────────────
  // Read one byte at a time; assemble a complete line before processing.
  // This avoids partial reads and heap churn from readStringUntil().
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (cmd_len > 0) {
        cmd_buf[cmd_len] = '\0';
        cmd_ready = true;
        break;   // process one command per loop() iteration
      }
    } else if (cmd_len < CMD_BUF_SIZE - 1) {
      cmd_buf[cmd_len++] = c;
    }
    // Silently discard overflow bytes (command too long = malformed).
  }

  if (!cmd_ready) return;
  cmd_ready = false;

  // Build String from the static buffer for compatibility with existing
  // startsWith / indexOf processing below.
  String command = String(cmd_buf);
  cmd_len = 0;  // reset buffer for next command
  command.trim();    // remove any stray whitespace/CR
    
    // Check if this is a framed command
    if (isFramedCommand(command)) {
      String cmd, data;
      if (parseFramedCommand(command, cmd, data)) {
        // Handle framed commands
        if (cmd == "GET_LEVELS") {
          // Get both tank levels with moving average filtering
          long dist1 = readDistanceReliable(1, 3);
          long dist2 = readDistanceReliable(2, 3);
          
          float pct1 = (dist1 > 0) ? calculateFillPercentage(dist1, 1) : -1.0;
          float pct2 = (dist2 > 0) ? calculateFillPercentage(dist2, 2) : -1.0;
          
          // Build response data: dist1,pct1,dist2,pct2
          String responseData = String(dist1) + "," + String(pct1, 2) + "," + 
                               String(dist2) + "," + String(pct2, 2);
          
          sendFramedResponse("LEVELS", responseData);
        } else {
          Serial.print("[ERROR] Unknown framed command: ");
          Serial.println(cmd);
        }
      }
      return; // Don't process as regular command
    }
    
    // Regular (non-framed) command processing for backward compatibility
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
    } else if (command.startsWith("send-sms-to-all_")) {
      String customMsg = command.substring(16);
      Serial.println("[GSM] Sending custom SMS to all recipients...");
      sendSMSToAll(customMsg);
      Serial.println("[GSM] Broadcast complete");
    } else if (command == "test-gsm") {
      testGSMConnection();
    } else if (command == "check-network") {
      Serial.println("[GSM] Checking network status...");
      checkNetwork();
    } else if (command == "get-gsm-status") {
      readSignalStrength();
      printGSMStatus();
    } else if (command == "get-distance1") {
      Serial.print("[SR04] Reading Sensor 1... ");
      long dist = readDistanceReliable(1, 3);  // Use reliable reading with 3 attempts
      if (dist > 0) {
        Serial.print(dist);
        Serial.println(" cm");
      } else {
        Serial.println("Invalid reading (filtered out)");
      }
    } else if (command == "get-distance2") {
      Serial.print("[SR04] Reading Sensor 2... ");
      long dist = readDistanceReliable(2, 3);  // Use reliable reading with 3 attempts
      if (dist > 0) {
        Serial.print(dist);
        Serial.println(" cm");
      } else {
        Serial.println("Invalid reading (filtered out)");
      }
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
    } else if (command.startsWith("rtc-test_")) {
      // Test command to try different year values
      // Format: rtc-test_26
      int testYear = command.substring(9).toInt();
      Serial.print("[RTC] Testing year value: ");
      Serial.println(testYear);
      myRTC.setDS1302Time(0, 0, 0, 1, 1, 1, testYear);
      delay(200);
      myRTC.updateTime();
      Serial.print("[RTC] Result - year from RTC: ");
      Serial.println(myRTC.year);
    } else if (command.startsWith("sync-time_")) {
      // Format: sync-time_YY_MM_DD_HH_MM_SS
      // RPI syncs its time to ESP32 RTC
      String timeStr = command.substring(10);
      int values[6];
      int idx = 0;
      int lastPos = 0;
      for (int i = 0; i < timeStr.length() && idx < 6; i++) {
        if (timeStr.charAt(i) == '_') {
          values[idx++] = timeStr.substring(lastPos, i).toInt();
          lastPos = i + 1;
        }
      }
      if (idx == 5) {
        values[idx++] = timeStr.substring(lastPos).toInt();
      }
      
      if (idx == 6) {
        setRTCTimeManual(values[0], values[1], values[2], values[3], values[4], values[5]);
        Serial.println("[SYNC] Time synced from RPI");
      } else {
        Serial.println("[ERROR] Invalid time sync format");
      }
    } else if (command == "get-status") {
      // Return complete system status for RPI
      myRTC.updateTime();
      int year = myRTC.year;
      if (year > 2096) year = (year - 2096) + 2000;
      
      long dist1 = readDistanceReliable(1, 3);
      long dist2 = readDistanceReliable(2, 3);
      float pct1 = (dist1 > 0) ? calculateFillPercentage(dist1, 1) : -1.0;
      float pct2 = (dist2 > 0) ? calculateFillPercentage(dist2, 2) : -1.0;
      
      Serial.print("[STATUS] Time=");
      Serial.print(year);
      Serial.print("/");
      if (myRTC.month < 10) Serial.print("0");
      Serial.print(myRTC.month);
      Serial.print("/");
      if (myRTC.dayofmonth < 10) Serial.print("0");
      Serial.print(myRTC.dayofmonth);
      Serial.print(" ");
      if (myRTC.hours < 10) Serial.print("0");
      Serial.print(myRTC.hours);
      Serial.print(":");
      if (myRTC.minutes < 10) Serial.print("0");
      Serial.print(myRTC.minutes);
      Serial.print(":");
      if (myRTC.seconds < 10) Serial.print("0");
      Serial.print(myRTC.seconds);
      Serial.print(" Tank1=");
      if (pct1 >= 0) {
        Serial.print(pct1);
        Serial.print("%");
      } else {
        Serial.print("INVALID");
      }
      Serial.print(" Tank2=");
      if (pct2 >= 0) {
        Serial.print(pct2);
        Serial.print("%");
      } else {
        Serial.print("INVALID");
      }
      Serial.print(" Recipients=");
      Serial.println(numRecipients);
    } else if (command.startsWith("sync-recipients_")) {
      // Format: sync-recipients_NUM1,NUM2,NUM3
      // Clear existing and add all from RPI
      clearRecipients();
      String numbers = command.substring(16);
      
      if (numbers.length() > 0) {
        int lastPos = 0;
        for (int i = 0; i <= numbers.length(); i++) {
          if (i == numbers.length() || numbers.charAt(i) == ',') {
            String num = numbers.substring(lastPos, i);
            if (num.length() > 0) {
              addRecipient(num);
            }
            lastPos = i + 1;
          }
        }
      }
      Serial.print("[SYNC] Recipients synced: ");
      Serial.println(numRecipients);
    } else if (command == "get-level") {
      Serial.print("[SR04] Reading tank level... ");
      long dist = readDistanceReliable(1, 3);  // Use reliable reading with 3 attempts
      if (dist > 0) {
        float level = calculateFillLevel(dist);
        float percentage = calculateFillPercentage(dist, 1);  // sensorNum=1 so SMS alert fires
        if (percentage >= 0) {  // Valid percentage (not -1 for invalid readings)
          Serial.print("Dist=");
          Serial.print(dist);
          Serial.print("cm Fill=");
          Serial.print(level);
          Serial.print("cm (");
          Serial.print(percentage);
          Serial.println("%)");
        } else {
          Serial.println("Invalid reading (filtered out)");
        }
      } else {
        Serial.println("Invalid reading (filtered out)");
      }
    } else if (command == "get-levels") {
      // Get both tank levels for RPI
      Serial.print("[LEVELS] ");
      long dist1 = readDistanceReliable(1, 3);
      long dist2 = readDistanceReliable(2, 3);
      
      // Debug prints
      Serial.print("[DEBUG] Dist1=");
      Serial.print(dist1);
      Serial.print("cm Dist2=");
      Serial.print(dist2);
      Serial.print("cm ");
      
      float pct1 = (dist1 > 0) ? calculateFillPercentage(dist1, 1) : -1.0;
      float pct2 = (dist2 > 0) ? calculateFillPercentage(dist2, 2) : -1.0;
      
      // Debug prints
      Serial.print("Pct1=");
      Serial.print(pct1);
      Serial.print(" Pct2=");
      Serial.print(pct2);
      Serial.print(" ");
      
      // Only show valid readings
      if (pct1 >= 0) {
        Serial.print("Tank1=");
        Serial.print(pct1);
        Serial.print("% ");
      } else {
        Serial.print("Tank1=INVALID ");
      }
      
      if (pct2 >= 0) {
        Serial.print("Tank2=");
        Serial.print(pct2);
        Serial.println("%");
      } else {
        Serial.println("Tank2=INVALID");
      }
    } else if (command.startsWith("spray_")) {
      // Format: spray_RELAY_DURATION_VOLUME_SPRAYTYPE
      // Example: spray_1_60_5000_Pesticide  (Relay 1, 60 s, 5000 mL, Pesticide)
      // SPRAYTYPE is optional (defaults to "Unknown" for backward compatibility)
      //
      // NON-BLOCKING IMPLEMENTATION:
      //   1. Relay turns ON IMMEDIATELY after argument parsing.
      //   2. ACK:SPRAY_STARTED is sent to the RPI so it knows the relay is
      //      physically active.
      //   3. A millis() timer is set; the loop() state machine turns the relay
      //      OFF when the timer expires (spray timer check at top of loop).
      //   4. SMS and buzzer notifications fire AFTER relay OFF so they can
      //      never delay actual relay actuation.

      if (spray_state.active) {
        Serial.println("[SPRAY] Busy - another spray is in progress");
      } else {
        int idx1 = command.indexOf('_');
        int idx2 = command.indexOf('_', idx1 + 1);
        int idx3 = command.indexOf('_', idx2 + 1);
        int idx4 = command.indexOf('_', idx3 + 1);  // Optional spray type index

        if (idx3 > 0) {
          int    relay     = command.substring(idx1 + 1, idx2).toInt();
          int    duration  = command.substring(idx2 + 1, idx3).toInt();
          int    volume;
          String sprayType;

          if (idx4 > 0) {
            // New format: spray_RELAY_DURATION_VOLUME_SPRAYTYPE
            volume    = command.substring(idx3 + 1, idx4).toInt();
            sprayType = command.substring(idx4 + 1);
          } else {
            // Legacy format: spray_RELAY_DURATION_VOLUME
            volume    = command.substring(idx3 + 1).toInt();
            sprayType = "Unknown";
          }

          Serial.print("[SPRAY] Starting: Relay ");
          Serial.print(relay);
          Serial.print(", Duration ");
          Serial.print(duration);
          Serial.print("s, Volume ");
          Serial.print(volume);
          Serial.println("mL");

          // ── RELAY ON IMMEDIATELY ─────────────────────────────────────────
          // Relay activates before any SMS/buzzer blocking call.
          if (relay == 1) {
            operateRELAY(RELAY_1, true);
          } else {
            operateRELAY(RELAY_2, true);
          }
          Serial.print("[SPRAY] Relay ");
          Serial.print(relay);
          Serial.println(" ON");

          // Acknowledge to RPI: relay is physically ON right now.
          Serial.println("ACK:SPRAY_STARTED");

          // Arm the non-blocking timer.
          spray_state.active     = true;
          spray_state.relay      = relay;
          spray_state.volume     = volume;
          spray_state.spray_type = sprayType;
          spray_state.end_ms     = millis() + (unsigned long)duration * 1000UL;

          // Buzzer: short beep is acceptable (relay is already ON).
          buzzerBeep(200);
          // NOTE: Spray-started SMS is now sent from the Raspberry Pi
          // via Semaphore API (see hardware/esp32_hardware.py :: spray()).
        } else {
          Serial.println("[ERROR] Invalid spray format. Use: spray_RELAY_DURATION_VOLUME");
        }
      }
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