#ifndef BUTTON_CONFIG_H
#define BUTTON_CONFIG_H

#include "PINS_CONFIG.h"
#include <TimeLib.h>
#include <TimeAlarms.h>
#include "RELAY_CONFIG.h"
#include "WEATHER_CONFIG.h"
#include "GSM_CONFIG.h"
#include "BUZZER_CONFIG.h"
#include "LED_CONFIG.h"

// Button configuration
#define BUTTON_COUNT 4
#define DEBOUNCE_DELAY 50

// Button pin assignments
#define BUTTON_1 WIFI_RESET_BUTTON_PIN    // GPIO 23 - WiFi reset
#define BUTTON_2 MENU_UP_BUTTON_PIN       // GPIO 25 - Menu up
#define BUTTON_3 MENU_DOWN_BUTTON_PIN     // GPIO 26 - Menu down
#define BUTTON_4 MENU_SELECT_BUTTON_PIN   // GPIO 27 - Menu select/save

// Button state arrays
int inputState[BUTTON_COUNT];
int lastInputState[BUTTON_COUNT] = { LOW, LOW, LOW, LOW };
bool inputFlags[BUTTON_COUNT] = { LOW, LOW, LOW, LOW };
long lastDebounceTime[BUTTON_COUNT] = { 0, 0, 0, 0 };
const int inputPins[BUTTON_COUNT] = { BUTTON_1, BUTTON_2, BUTTON_3, BUTTON_4 };

// Menu and scheduling variables
extern AlarmId sprayAlarmId1;
extern AlarmId sprayAlarmId2;
extern bool schedulingMode;
extern int currentMenuItem;
extern int selectedHour;
extern int selectedMinute;
extern int selectedPump;  // 1 or 2

// Function declarations
void initBUTTONS();
void setInputFlags();
void resolveInputFlags();
void inputAction(int buttonIndex);
void enterSchedulingMode();
void exitSchedulingMode();
void scheduleSprayAlarm(int pump, int hour, int minute);
void cancelSprayAlarm(int pump);
void sendSMSWithRetry(String message);
bool checkAndReconnectNetwork();
void commercialAlertPattern();
void commercialSprayStartPattern();
void commercialSuccessPattern();

//-----------------------------------------------------------------
//FUNCTION FOR INITIALIZING BUTTONS---------------------------------
//-----------------------------------------------------------------
void initBUTTONS() {
  for (int i = 0; i < BUTTON_COUNT; i++) {
    pinMode(inputPins[i], INPUT_PULLUP);  // Use INPUT_PULLUP for ESP32
  }
  delay(1000);
  Serial.println("Push Buttons: Initialized!");

  // Initialize menu variables
  schedulingMode = false;
  currentMenuItem = 0;
  selectedHour = hour();
  selectedMinute = minute();
}

//-----------------------------------------------------------------
//FUNCTION FOR SETTING BUTTON STATE--------------------------------
//-----------------------------------------------------------------
void setInputFlags() {
  for (int i = 0; i < BUTTON_COUNT; i++) {    // loop until i is less than 4
    int reading = digitalRead(inputPins[i]);  // read pins
    if (reading != lastInputState[i]) {       // if reading is not equal to the lastInputState
      lastDebounceTime[i] = millis();         // set lastDebounceTime equal to arduino's running time
    }
    if (millis() - lastDebounceTime[i] > DEBOUNCE_DELAY) {  // if arduino's running time and lastDebounceTime difference is greater than debounceDelay
      if (reading != inputState[i]) {                       // if reading is not equal to inputState
        inputState[i] = reading;                            // then make inputState equals to reading
        if (inputState[i] == HIGH) {                        // if inputState is equal to high which is Pressed switch then
          inputFlags[i] = HIGH;                             // make inputFlag equal to high
        }
      }
    }
    lastInputState[i] = reading;  // set last Input state equal to reading of every switches
  }                               // loop end
}

//-----------------------------------------------------------------
//FUNCTION FOR READING BUTTON STATE--------------------------------
//-----------------------------------------------------------------
boolean first_time = true;
void resolveInputFlags() {
  for (int i = 0; i < BUTTON_COUNT; i++) {  // loop until i is less than 4
    if (inputFlags[i] == HIGH) {            //if inputFlags is HIGH then
      if (i == 3 && first_time) {
        first_time = false;
      } else {
        inputAction(i);  // do the function inputAction to handle button actions
      }
      inputFlags[i] = LOW;  // set all inputFlags to LOW after pressing the switches
    }
  }  // loop end
}

//-----------------------------------------------------------------
//FUNCTION FOR HANDLING BUTTON ACTIONS-----------------------------
//-----------------------------------------------------------------
void inputAction(int buttonIndex) {
  switch(buttonIndex) {
    case 0: // WiFi Reset Button (BUTTON_1) - handled separately in main loop
      // This is handled by checkWiFiResetTrigger() in the main loop
      break;

    case 1: // Menu Up Button (BUTTON_2)
      if (schedulingMode) {
        // In scheduling mode, increment selected time
        if (currentMenuItem == 0) { // Hour selection
          selectedHour = (selectedHour + 1) % 24;
        } else if (currentMenuItem == 1) { // Minute selection
          selectedMinute = (selectedMinute + 1) % 60;
        }
        updateSchedulingDisplay();
      } else {
        // In main menu, navigate up
        currentMenuItem = (currentMenuItem - 1 + 4) % 4; // 4 menu items
        updateMainMenuDisplay();
      }
      break;

    case 2: // Menu Down Button (BUTTON_3)
      if (schedulingMode) {
        // In scheduling mode, decrement selected time
        if (currentMenuItem == 0) { // Hour selection
          selectedHour = (selectedHour - 1 + 24) % 24;
        } else if (currentMenuItem == 1) { // Minute selection
          selectedMinute = (selectedMinute - 1 + 60) % 60;
        }
        updateSchedulingDisplay();
      } else {
        // In main menu, navigate down
        currentMenuItem = (currentMenuItem + 1) % 4; // 4 menu items
        updateMainMenuDisplay();
      }
      break;

    case 3: // Menu Select/Save Button (BUTTON_4)
      if (schedulingMode) {
        if (currentMenuItem < 2) {
          // Move to next scheduling item
          currentMenuItem++;
          updateSchedulingDisplay();
        } else {
          // Save the scheduled time and exit scheduling mode
          scheduleSprayAlarm(selectedPump, selectedHour, selectedMinute);
          exitSchedulingMode();
        }
      } else {
        // Enter scheduling mode for the selected menu item
        if (currentMenuItem == 0) { // Schedule pump 1
          selectedPump = 1;
          enterSchedulingMode();
        } else if (currentMenuItem == 1) { // Schedule pump 2
          selectedPump = 2;
          enterSchedulingMode();
        } else if (currentMenuItem == 2) { // Cancel all schedules
          cancelSprayAlarm(1);
          cancelSprayAlarm(2);
        } else if (currentMenuItem == 3) { // View current time
          displayCurrentTime();
        }
      }
      break;
  }
}

//-----------------------------------------------------------------
//MENU AND SCHEDULING FUNCTIONS------------------------------------
//-----------------------------------------------------------------
void enterSchedulingMode() {
  schedulingMode = true;
  currentMenuItem = 0; // Start with hour selection
  selectedHour = hour();
  selectedMinute = minute();
  updateSchedulingDisplay();
  Serial.println("Entered scheduling mode");
}

void exitSchedulingMode() {
  schedulingMode = false;
  currentMenuItem = 0;
  updateMainMenuDisplay();
  Serial.println("Exited scheduling mode");
}

void scheduleSprayAlarm(int pump, int hour, int minute) {
  AlarmId* alarmId = (pump == 1) ? &sprayAlarmId1 : &sprayAlarmId2;

  // Cancel existing alarm if any
  if (*alarmId != dtINVALID_ALARM_ID) {
    Alarm.free(*alarmId);
  }

  // Create new daily alarm
  *alarmId = Alarm.alarmRepeat(hour, minute, 0, (pump == 1) ? sprayAlarmCallback1 : sprayAlarmCallback2);

  Serial.print("Spray alarm for pump ");
  Serial.print(pump);
  Serial.print(" scheduled for ");
  Serial.print(hour);
  Serial.print(":");
  Serial.println(minute);
}

void cancelSprayAlarm(int pump) {
  AlarmId* alarmId = (pump == 1) ? &sprayAlarmId1 : &sprayAlarmId2;

  if (*alarmId != dtINVALID_ALARM_ID) {
    Alarm.free(*alarmId);
    *alarmId = dtINVALID_ALARM_ID;
    Serial.print("Spray alarm for pump ");
    Serial.print(pump);
    Serial.println(" cancelled");
  }
}

// Callback function for spray alarm pump 1
void sprayAlarmCallback1() {
  Serial.println("Spray alarm for pump 1 triggered!");
  
  // Check weather
  if (checkWeatherForRain()) {
    Serial.println("Rain detected, postponing pump 1 spray to tomorrow");
    
    // Send postponement SMS
    String message = "ALERT: Pump 1 spraying POSTPONED due to rain. Rescheduled for tomorrow at same time.";
    sendSMSWithRetry(message);
    
    // Professional feedback
    commercialAlertPattern();
    
    // Reschedule for tomorrow same time
    time_t now = time(nullptr);
    struct tm *timeinfo = localtime(&now);
    int hour = timeinfo->tm_hour;
    int min = timeinfo->tm_min;
    // Schedule for tomorrow
    AlarmId newAlarm = Alarm.alarmOnce(hour, min, 1, sprayAlarmCallback1);  // 1 day from now
    sprayAlarmId1 = newAlarm;
    return;
  }
  
  // Check network before spraying
  if (!checkAndReconnectNetwork()) {
    Serial.println("Network unavailable, postponing pump 1 spray");
    String message = "ALERT: Pump 1 spraying POSTPONED due to network issues.";
    sendSMSWithRetry(message);
    commercialAlertPattern();
    return;
  }
  
  // Activate pump 1
  Serial.println("Activating Pump 1...");
  operateRELAY(RELAY_1_PIN, true);
  
  // Professional activation feedback
  commercialSprayStartPattern();
  
  delay(5000);  // Spray for 5 seconds (adjust as needed)
  operateRELAY(RELAY_1_PIN, false);
  
  Serial.println("Pump 1 spray completed");
  
  // Send completion SMS
  String message = "SUCCESS: Pump 1 spraying COMPLETED successfully.";
  sendSMSWithRetry(message);
  
  // Professional completion feedback
  commercialSuccessPattern();
}

// Callback function for spray alarm pump 2
void sprayAlarmCallback2() {
  Serial.println("Spray alarm for pump 2 triggered!");
  
  // Check weather
  if (checkWeatherForRain()) {
    Serial.println("Rain detected, postponing pump 2 spray to tomorrow");
    
    // Send postponement SMS
    String message = "ALERT: Pump 2 spraying POSTPONED due to rain. Rescheduled for tomorrow at same time.";
    sendSMSWithRetry(message);
    
    // Professional feedback
    commercialAlertPattern();
    
    // Reschedule for tomorrow same time
    time_t now = time(nullptr);
    struct tm *timeinfo = localtime(&now);
    int hour = timeinfo->tm_hour;
    int min = timeinfo->tm_min;
    // Schedule for tomorrow
    AlarmId newAlarm = Alarm.alarmOnce(hour, min, 1, sprayAlarmCallback2);  // 1 day from now
    sprayAlarmId2 = newAlarm;
    return;
  }
  
  // Check network before spraying
  if (!checkAndReconnectNetwork()) {
    Serial.println("Network unavailable, postponing pump 2 spray");
    String message = "ALERT: Pump 2 spraying POSTPONED due to network issues.";
    sendSMSWithRetry(message);
    commercialAlertPattern();
    return;
  }
  
  // Activate pump 2
  Serial.println("Activating Pump 2...");
  operateRELAY(RELAY_2_PIN, true);
  
  // Professional activation feedback
  commercialSprayStartPattern();
  
  delay(5000);  // Spray for 5 seconds (adjust as needed)
  operateRELAY(RELAY_2_PIN, false);
  
  Serial.println("Pump 2 spray completed");
  
  // Send completion SMS
  String message = "SUCCESS: Pump 2 spraying COMPLETED successfully.";
  sendSMSWithRetry(message);
  
  // Professional completion feedback
  commercialSuccessPattern();
}

// Display functions (to be implemented with LCD)
void updateMainMenuDisplay() {
  // TODO: Implement LCD menu display
  Serial.print("Main Menu - Item: ");
  Serial.println(currentMenuItem);
  switch(currentMenuItem) {
    case 0: Serial.println("Schedule Pump 1"); break;
    case 1: Serial.println("Schedule Pump 2"); break;
    case 2: Serial.println("Cancel All Schedules"); break;
    case 3: Serial.println("View Current Time"); break;
  }
}

void updateSchedulingDisplay() {
  // TODO: Implement LCD scheduling display
  Serial.print("Scheduling Pump ");
  Serial.print(selectedPump);
  Serial.print(" - ");
  if (currentMenuItem == 0) {
    Serial.print("Hour: ");
    Serial.println(selectedHour);
  } else if (currentMenuItem == 1) {
    Serial.print("Minute: ");
    Serial.println(selectedMinute);
  } else {
    Serial.print("Confirm - ");
    Serial.print(selectedHour);
    Serial.print(":");
    Serial.println(selectedMinute);
  }
}

void displayCurrentTime() {
  // TODO: Implement LCD time display
  Serial.print("Current Time: ");
  Serial.print(hour());
  Serial.print(":");
  Serial.println(minute());
}

//-----------------------------------------------------------------
//SMS AND NETWORK FUNCTIONS---------------------------------------
//-----------------------------------------------------------------

// Send SMS with retry logic
void sendSMSWithRetry(String message) {
  const int maxRetries = 3;
  bool sent = false;
  
  for (int attempt = 1; attempt <= maxRetries && !sent; attempt++) {
    Serial.print("SMS attempt ");
    Serial.print(attempt);
    Serial.print("/");
    Serial.println(maxRetries);
    
    // Try to send SMS to all recipients
    sent = sendSMSToAllWithStatus(message);
    
    if (!sent && attempt < maxRetries) {
      Serial.println("SMS failed, retrying in 5 seconds...");
      delay(5000);
    }
  }
  
  if (sent) {
    Serial.println("SMS sent successfully");
  } else {
    Serial.println("SMS failed after all retries");
    commercialErrorPattern();
  }
}

// Check network and reconnect if needed
bool checkAndReconnectNetwork() {
  // Check GSM network registration
  sim.println("AT+CREG?");
  delay(1000);
  
  String response = "";
  while (sim.available()) {
    response += char(sim.read());
  }
  
  // Check if registered (contains ",1" or ",5")
  if (response.indexOf(",1") >= 0 || response.indexOf(",5") >= 0) {
    Serial.println("GSM network connected");
    return true;
  } else {
    Serial.println("GSM network disconnected, attempting reconnection...");
    
    // Try to reconnect
    sim.println("AT+CFUN=1,1");  // Reset GSM module
    delay(10000);  // Wait for reset
    
    // Reinitialize GSM
    sim.begin(9600);
    delay(1000);
    
    // Check again
    sim.println("AT+CREG?");
    delay(2000);
    
    response = "";
    while (sim.available()) {
      response += char(sim.read());
    }
    
    if (response.indexOf(",1") >= 0 || response.indexOf(",5") >= 0) {
      Serial.println("GSM network reconnected successfully");
      return true;
    } else {
      Serial.println("GSM network reconnection failed");
      return false;
    }
  }
}

//-----------------------------------------------------------------
//PROFESSIONAL COMMERCIAL FEEDBACK PATTERNS-----------------------
//-----------------------------------------------------------------

// Alert pattern for postponement/errors
void commercialAlertPattern() {
  // Aggressive red alert pattern
  for (int i = 0; i < 5; i++) {
    // Fast LED blinking
    setSystemError();  // Red LED on
    buzzerTone(1000, 200);  // High pitch beep
    delay(100);
    clearSystemLEDs();  // LEDs off
    delay(100);
  }
  
  // Escalating tone pattern
  for (int freq = 800; freq <= 1200; freq += 100) {
    buzzerTone(freq, 150);
    delay(50);
  }
  
  // Final warning flash
  setSystemError();
  buzzerTone(1500, 500);
  delay(200);
  clearSystemLEDs();
}

// Spray start pattern - industrial machine startup
void commercialSprayStartPattern() {
  // Power-up sequence
  setSystemOK();  // Green LED
  buzzerTone(600, 300);  // Low rumble
  delay(200);
  
  // Acceleration pattern
  for (int i = 0; i < 3; i++) {
    buzzerTone(800 + (i * 200), 150);
    delay(100);
  }
  
  // Steady operation indicator
  setSystemOK();
  buzzerTone(1000, 200);  // Steady tone
}

// Success completion pattern
void commercialSuccessPattern() {
  // Victory fanfare
  setSystemOK();  // Green LED
  
  // Ascending success tones
  int successTones[] = {523, 659, 784, 1047};  // C, E, G, C (musical notes)
  for (int i = 0; i < 4; i++) {
    buzzerTone(successTones[i], 200);
    delay(50);
  }
  
  // Double flash confirmation
  for (int i = 0; i < 2; i++) {
    clearSystemLEDs();
    delay(100);
    setSystemOK();
    delay(100);
  }
  
  clearSystemLEDs();
}

// Error pattern for failed operations
void commercialErrorPattern() {
  // Industrial error siren
  for (int cycle = 0; cycle < 2; cycle++) {
    // Rising tone
    for (int freq = 400; freq <= 800; freq += 50) {
      buzzerTone(freq, 50);
    }
    // Falling tone
    for (int freq = 800; freq >= 400; freq -= 50) {
      buzzerTone(freq, 50);
    }
  }
  
  // Red error flash
  setSystemError();
  delay(1000);
  clearSystemLEDs();
}

#endif // BUTTON_CONFIG_H