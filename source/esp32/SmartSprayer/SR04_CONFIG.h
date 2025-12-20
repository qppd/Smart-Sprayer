#ifndef SR04_CONFIG_H
#define SR04_CONFIG_H

const int trigPin = 12;
const int echoPin = 13;

void initSR04() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
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

#endif