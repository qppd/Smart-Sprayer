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

#endif