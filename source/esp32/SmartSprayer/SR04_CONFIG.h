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
// Container specs:
//   Total height        = 38 cm  (CONTAINER_EMPTY_DISTANCE = 38)
//   Sensor blind zone   = 22 cm  (CONTAINER_FULL_DISTANCE  = 22)
//                         Any reading < 22 cm is INVALID (below sensor minimum range)
//   Usable range        = 38 - 22 = 16 cm  (bottom 16 cm of container)
// Distance → percentage mapping:
//   < 22 cm   → INVALID (-1.0)  blind zone — do NOT treat as full
//   22 cm     → 100%   liquid at 16 cm (maximum measurable height)
//   22–38 cm  → proportional, based on 16 cm usable range
//   >= 38 cm  → 0%     container empty, liquid at 0 cm
// SMS alert thresholds (fired once per drop; re-armed when level recovers):
//   Critical : liquid height <= 7.6 cm  (= 20% of total 38 cm container)
//   Empty    : liquid height  = 0 cm    (distance >= 38 cm)

// Critical liquid-height threshold in cm (20% × 38 cm = 7.6 cm)
#define CRITICAL_LIQUID_HEIGHT_CM 7.6f

// Per-sensor SMS debounce flags  [index 0 unused; 1 = Tank 1, 2 = Tank 2]
static bool s_critical_sent[3] = {false, false, false};
static bool s_empty_sent[3]    = {false, false, false};

// sensorNum: 0 = no SMS alerts, 1 = Tank 1, 2 = Tank 2  (default 0)
float calculateFillPercentage(long distance, int sensorNum = 0) {
  // Hardware error / no echo
  if (distance <= 0) {
    return -1.0;
  }

  // Below sensor minimum range (blind zone) → INVALID.
  // Previously returned 100%, which caused Container 2 to always read 100%
  // when the sensor fired an echo shorter than 22 cm.
  if (distance < CONTAINER_FULL_DISTANCE) {
    return -1.0;
  }

  // Usable range = 16 cm  (22 cm full → 38 cm empty)
  float usableRange  = CONTAINER_EMPTY_DISTANCE - CONTAINER_FULL_DISTANCE; // 16 cm
  float liquidHeight = CONTAINER_EMPTY_DISTANCE - (float)distance;         // cm from bottom

  // At or beyond empty distance → 0%
  if (distance >= CONTAINER_EMPTY_DISTANCE) {
    liquidHeight = 0.0f;

    if (sensorNum > 0 && sensorNum <= 2) {
      if (!s_empty_sent[sensorNum]) {
        sendSMSToAll("Tank " + String(sensorNum) +
                     " alert: Empty container: 0% remaining.");
        s_empty_sent[sensorNum]    = true;
        s_critical_sent[sensorNum] = true; // suppress duplicate critical when already empty
      }
    }
    return 0.0;
  }

  // Interpolate percentage within the 16 cm usable range
  float percentage = (liquidHeight / usableRange) * 100.0f;
  if (percentage > 100.0f) percentage = 100.0f;
  if (percentage <   0.0f) percentage =   0.0f;

  if (sensorNum > 0 && sensorNum <= 2) {
    // Reset empty alert when level recovers above 0
    s_empty_sent[sensorNum] = false;

    // Critical alert: liquid height <= 7.6 cm (20% of 38 cm total container)
    if (liquidHeight <= CRITICAL_LIQUID_HEIGHT_CM) {
      if (!s_critical_sent[sensorNum]) {
        sendSMSToAll("Tank " + String(sensorNum) +
                     " alert: Critical level: 20% remaining.");
        s_critical_sent[sensorNum] = true;
      }
    } else {
      // Level recovered above critical threshold — re-arm for next drop
      s_critical_sent[sensorNum] = false;
    }
  }

  return percentage;
}

float calculateFillLevel(long distance) {
  // Return the liquid level in cm from the bottom of the container
  float level = CONTAINER_EMPTY_DISTANCE - (float)distance;
  if (level < 0.0f) level = 0.0f;
  if (level > (CONTAINER_EMPTY_DISTANCE - CONTAINER_FULL_DISTANCE)) {
    level = CONTAINER_EMPTY_DISTANCE - CONTAINER_FULL_DISTANCE; // cap at 16 cm
  }
  return level;
}

#endif