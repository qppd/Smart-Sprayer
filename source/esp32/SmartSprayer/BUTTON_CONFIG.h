#ifndef BUTTON_CONFIG_H
#define BUTTON_CONFIG_H

#include "PINS_CONFIG.h"
#include <TimeLib.h>
#include <TimeAlarms.h>

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
extern AlarmId sprayAlarmId;
extern bool schedulingMode;
extern int currentMenuItem;
extern int selectedHour;
extern int selectedMinute;

// Function declarations
void initBUTTONS();
void setInputFlags();
void resolveInputFlags();
void inputAction(int buttonIndex);
void enterSchedulingMode();
void exitSchedulingMode();
void scheduleSprayAlarm(int hour, int minute);
void cancelSprayAlarm();

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
        currentMenuItem = (currentMenuItem - 1 + 3) % 3; // 3 menu items
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
        currentMenuItem = (currentMenuItem + 1) % 3; // 3 menu items
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
          scheduleSprayAlarm(selectedHour, selectedMinute);
          exitSchedulingMode();
        }
      } else {
        // Enter scheduling mode for the selected menu item
        if (currentMenuItem == 0) { // Schedule spray
          enterSchedulingMode();
        } else if (currentMenuItem == 1) { // Cancel schedule
          cancelSprayAlarm();
        } else if (currentMenuItem == 2) { // View current time
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

void scheduleSprayAlarm(int hour, int minute) {
  // Cancel existing alarm if any
  if (sprayAlarmId != dtINVALID_ALARM_ID) {
    Alarm.free(sprayAlarmId);
  }

  // Create new daily alarm
  sprayAlarmId = Alarm.alarmRepeat(hour, minute, 0, sprayAlarmCallback);

  Serial.print("Spray alarm scheduled for ");
  Serial.print(hour);
  Serial.print(":");
  Serial.println(minute);
}

void cancelSprayAlarm() {
  if (sprayAlarmId != dtINVALID_ALARM_ID) {
    Alarm.free(sprayAlarmId);
    sprayAlarmId = dtINVALID_ALARM_ID;
    Serial.println("Spray alarm cancelled");
  }
}

// Callback function for spray alarm
void sprayAlarmCallback() {
  Serial.println("Spray alarm triggered!");
  // Add your spray activation logic here
  // For example: operateRELAY(RELAY_1, true);
}

// Display functions (to be implemented with LCD)
void updateMainMenuDisplay() {
  // TODO: Implement LCD menu display
  Serial.print("Main Menu - Item: ");
  Serial.println(currentMenuItem);
}

void updateSchedulingDisplay() {
  // TODO: Implement LCD scheduling display
  Serial.print("Scheduling - Hour: ");
  Serial.print(selectedHour);
  Serial.print(", Minute: ");
  Serial.println(selectedMinute);
}

void displayCurrentTime() {
  // TODO: Implement LCD time display
  Serial.print("Current Time: ");
  Serial.print(hour());
  Serial.print(":");
  Serial.println(minute());
}

#endif // BUTTON_CONFIG_H