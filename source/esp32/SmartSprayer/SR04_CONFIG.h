#ifndef SR04_CONFIG_H
#define SR04_CONFIG_H

#include <Arduino.h>
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

// Reliable distance reading with filtering
long readDistanceReliable(int sensorNum = 1, int maxAttempts = 3) {
  long readings[5]; // Fixed size array for simplicity
  int validCount = 0;
  
  // Take multiple readings
  for (int i = 0; i < maxAttempts && validCount < 5; i++) {
    long distance = (sensorNum == 1) ? readDistance() : readDistance2();
    
    // Only consider valid readings (not 0 and within reasonable range)
    if (distance > 0 && distance <= CONTAINER_EMPTY_DISTANCE + 20) {
      readings[validCount] = distance;
      validCount++;
    }
    
    delay(50); // Small delay between readings
  }
  
  // If we have valid readings, return the median
  if (validCount > 0) {
    // Sort readings (simple bubble sort for small array)
    for (int i = 0; i < validCount - 1; i++) {
      for (int j = 0; j < validCount - 1 - i; j++) {
        if (readings[j] > readings[j + 1]) {
          long temp = readings[j];
          readings[j] = readings[j + 1];
          readings[j + 1] = temp;
        }
      }
    }
    
    // Return median value
    return readings[validCount / 2];
  }
  
  // If all readings were invalid, return 0 (will be filtered out)
  return 0;
}

// Container level calculation functions
// Distance 22cm = Full (100%, 16L), Distance 50cm = Empty (0%, 0L)
float calculateFillPercentage(long distance) {
  // Handle invalid readings (0cm or out of range)
  if (distance <= 0 || distance > CONTAINER_EMPTY_DISTANCE + 10) {
    return -1.0; // Invalid reading, will be filtered out
  }
  
  // If distance <= 22cm: tank is full (100%)
  if (distance <= CONTAINER_FULL_DISTANCE) {
    return 100.0;
  }
  
  // If distance >= 50cm: tank is empty (0%)
  if (distance >= CONTAINER_EMPTY_DISTANCE) {
    return 0.0;
  }
  
  // For distances between 22-50cm: interpolate percentage
  // 22cm = 100%, 50cm = 0%
  float usableRange = CONTAINER_EMPTY_DISTANCE - CONTAINER_FULL_DISTANCE;  // 50 - 22 = 28cm
  float currentLevel = CONTAINER_EMPTY_DISTANCE - distance;  // How much above empty
  
  float percentage = (currentLevel / usableRange) * 100.0;
  
  // Clamp to 0-100 (extra safety)
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