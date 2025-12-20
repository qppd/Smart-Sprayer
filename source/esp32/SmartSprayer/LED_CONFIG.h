#ifndef LED_CONFIG_H
#define LED_CONFIG_H

#include "PINS_CONFIG.h"

// LED States
#define LED_OFF 0
#define LED_ON 1

void initLEDs() {
  pinMode(SYSTEM_OK_LED, OUTPUT);
  pinMode(SYSTEM_ERROR_LED, OUTPUT);

  // Turn all off initially
  setSystemLEDs(LED_OFF, LED_OFF);
}

void setSystemLEDs(int ok_state, int error_state) {
  digitalWrite(SYSTEM_OK_LED, ok_state);
  digitalWrite(SYSTEM_ERROR_LED, error_state);
}

void setSystemOK() {
  setSystemLEDs(LED_ON, LED_OFF);
}

void setSystemError() {
  setSystemLEDs(LED_OFF, LED_ON);
}

void setSystemWarning() {
  setSystemLEDs(LED_ON, LED_ON); // Both on for warning
}

void clearSystemLEDs() {
  setSystemLEDs(LED_OFF, LED_OFF);
}

#endif // LED_CONFIG_H