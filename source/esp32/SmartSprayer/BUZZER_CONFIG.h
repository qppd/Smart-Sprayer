#ifndef BUZZER_CONFIG_H
#define BUZZER_CONFIG_H

#include "PINS_CONFIG.h"

void initBuzzer() {
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW); // Off by default
}

void buzzerOn() {
  digitalWrite(BUZZER_PIN, HIGH);
}

void buzzerOff() {
  digitalWrite(BUZZER_PIN, LOW);
}

void buzzerBeep(int duration_ms = 500) {
  buzzerOn();
  delay(duration_ms);
  buzzerOff();
}

#endif // BUZZER_CONFIG_H