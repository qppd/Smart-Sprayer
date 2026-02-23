#ifndef SR04_CONFIG_H
#define SR04_CONFIG_H

#include <Arduino.h>
#include "PINS_CONFIG.h"

const int trigPin = TRIG_PIN;
const int echoPin = ECHO_PIN;
const int trig2Pin = TRIG2_PIN;
const int echo2Pin = ECHO2_PIN;

// Moving average filter configuration
#define MOVING_AVG_WINDOW 5

// Moving average buffers for smooth readings
long sensor1Buffer[MOVING_AVG_WINDOW] = {0};
long sensor2Buffer[MOVING_AVG_WINDOW] = {0};
int sensor1Index = 0;
int sensor2Index = 0;
bool sensor1BufferFilled = false;
bool sensor2BufferFilled = false;

// Function prototypes
long calculateMovingAverage(int sensorNum);

void initSR04() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(trig2Pin, OUTPUT);
  pinMode(echo2Pin, INPUT);
  
  // Initialize buffers with invalid readings
  for (int i = 0; i < MOVING_AVG_WINDOW; i++) {
    sensor1Buffer[i] = 0;
    sensor2Buffer[i] = 0;
  }
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
    
    // Get median value
    long median = readings[validCount / 2];
    
    // Add to moving average buffer
    if (sensorNum == 1) {
      sensor1Buffer[sensor1Index] = median;
      sensor1Index = (sensor1Index + 1) % MOVING_AVG_WINDOW;
      if (sensor1Index == 0) sensor1BufferFilled = true;
    } else {
      sensor2Buffer[sensor2Index] = median;
      sensor2Index = (sensor2Index + 1) % MOVING_AVG_WINDOW;
      if (sensor2Index == 0) sensor2BufferFilled = true;
    }
    
    // Calculate moving average
    return calculateMovingAverage(sensorNum);
  }
  
  // If all readings were invalid, return 0 (will be filtered out)
  return 0;
}

// Calculate moving average from buffer
long calculateMovingAverage(int sensorNum) {
  long* buffer = (sensorNum == 1) ? sensor1Buffer : sensor2Buffer;
  bool bufferFilled = (sensorNum == 1) ? sensor1BufferFilled : sensor2BufferFilled;
  
  long sum = 0;
  int count = bufferFilled ? MOVING_AVG_WINDOW : 
              ((sensorNum == 1) ? sensor1Index : sensor2Index);
  
  // If no readings yet, return 0
  if (count == 0) return 0;
  
  // Sum valid readings in buffer
  int validCount = 0;
  for (int i = 0; i < count; i++) {
    if (buffer[i] > 0) {  // Skip invalid readings (0)
      sum += buffer[i];
      validCount++;
    }
  }
  
  // Return average of valid readings
  return (validCount > 0) ? (sum / validCount) : 0;
}

// Container level calculation functions
// Rules:
// - 0 cm = INVALID reading (sensor error)
// - 1-22 cm = FULL (100%, 16L)
// - 22-50 cm = Proportional (0-100%)
// - >50 cm = EMPTY (0%, 0L)
float calculateFillPercentage(long distance) {
  // Handle invalid readings (0cm = sensor error)
  if (distance <= 0) {
    return -1.0; // Invalid reading marker
  }
  
  // If distance 1-22cm: tank is full (100%)
  if (distance > 0 && distance <= CONTAINER_FULL_DISTANCE) {
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