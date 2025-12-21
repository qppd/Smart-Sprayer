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

void buzzerTone(int frequency, int duration_ms) {
  // Simple tone generation using delay (not true PWM)
  int period = 1000000 / frequency;  // Period in microseconds
  int cycles = (frequency * duration_ms) / 1000;
  
  for (int i = 0; i < cycles; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delayMicroseconds(period / 2);
    digitalWrite(BUZZER_PIN, LOW);
    delayMicroseconds(period / 2);
  }
}

#endif // BUZZER_CONFIG_H