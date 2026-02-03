#ifndef SR04_CONFIG_H
#define SR04_CONFIG_H

#include "PINS_CONFIG.h"

const int trigPin = TRIG_PIN;
const int echoPin = ECHO_PIN;
const int trig2Pin = TRIG2_PIN;
const int echo2Pin = ECHO2_PIN;

void initSR04() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(trig2Pin, OUTPUT);
  pinMode(echo2Pin, INPUT);
}

long readDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  long distance = duration * 0.034 / 2;
  return distance;
}

long readDistance2() {
  digitalWrite(trig2Pin, LOW);
  delayMicroseconds(2);
  digitalWrite(trig2Pin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig2Pin, LOW);
  long duration = pulseIn(echo2Pin, HIGH);
  long distance = duration * 0.034 / 2;
  return distance;
}

// Container level calculation functions
// Distance 25cm = Full (100%), Distance 50cm = Empty (0%)
float calculateFillPercentage(long distance) {
  // Invert the logic: smaller distance = more full
  // 25cm = 100%, 50cm = 0%
  float usableRange = CONTAINER_EMPTY_DISTANCE - CONTAINER_FULL_DISTANCE;  // 50 - 25 = 25cm
  float currentLevel = CONTAINER_EMPTY_DISTANCE - distance;  // How much above empty
  
  float percentage = (currentLevel / usableRange) * 100.0;
  
  // Clamp to 0-100
  if (percentage > 100.0) percentage = 100.0;
  if (percentage < 0.0) percentage = 0.0;
  
  return percentage;
}

float calculateFillLevel(long distance) {
  // Return the actual liquid level in cm from bottom
  float level = CONTAINER_EMPTY_DISTANCE - distance;
  if (level < 0) level = 0;
  return level;
}

#endif