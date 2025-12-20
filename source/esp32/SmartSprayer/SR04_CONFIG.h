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
float calculateFillLevel(long distance) {
  // Calculate filled height: container height - measured distance
  float filledHeight = CONTAINER_HEIGHT - distance;
  
  // Ensure filled height is not negative
  if (filledHeight < 0) {
    filledHeight = 0;
  }
  
  return filledHeight;
}

float calculateFillPercentage(long distance) {
  float filledHeight = calculateFillLevel(distance);
  
  // Calculate percentage: (filled height / total height) * 100
  float percentage = (filledHeight / CONTAINER_HEIGHT) * 100.0;
  
  // Ensure percentage is within 0-100 range
  if (percentage > 100.0) {
    percentage = 100.0;
  } else if (percentage < 0.0) {
    percentage = 0.0;
  }
  
  return percentage;
}

#endif