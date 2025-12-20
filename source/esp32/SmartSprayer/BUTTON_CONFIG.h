#ifndef BUTTON_CONFIG_H
#define BUTTON_CONFIG_H

#include "PINS_CONFIG.h"

// Button configuration
#define BUTTON_DEBOUNCE_DELAY 50  // Debounce delay in milliseconds
#define WIFI_RESET_HOLD_TIME 3000 // Hold time for WiFi reset (3 seconds)

// Button states
#define BUTTON_PRESSED LOW   // Active LOW (pull-up resistor)
#define BUTTON_RELEASED HIGH

// Global variables for button state tracking
static unsigned long buttonPressStartTime = 0;
static bool buttonWasPressed = false;

// Function implementations
void initButton() {
  pinMode(WIFI_RESET_BUTTON_PIN, INPUT_PULLUP);
}

bool isButtonPressed() {
  return digitalRead(WIFI_RESET_BUTTON_PIN) == BUTTON_PRESSED;
}

bool checkWiFiResetTrigger() {
  bool currentState = isButtonPressed();
  
  if (currentState && !buttonWasPressed) {
    // Button just pressed
    buttonPressStartTime = millis();
    buttonWasPressed = true;
  } else if (!currentState && buttonWasPressed) {
    // Button just released
    buttonWasPressed = false;
    buttonPressStartTime = 0;
  } else if (currentState && buttonWasPressed) {
    // Button is being held
    unsigned long holdTime = millis() - buttonPressStartTime;
    if (holdTime >= WIFI_RESET_HOLD_TIME) {
      // Reset button state
      buttonWasPressed = false;
      buttonPressStartTime = 0;
      return true; // Trigger WiFi reset
    }
  }
  
  return false;
}

#endif // BUTTON_CONFIG_H