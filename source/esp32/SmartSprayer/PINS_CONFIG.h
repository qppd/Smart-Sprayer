#ifndef PINS_CONFIG_H
#define PINS_CONFIG_H

// Ultrasonic Sensor Pins
#define TRIG_PIN 12      // Sensor 1 Trigger
#define ECHO_PIN 13      // Sensor 1 Echo
#define TRIG2_PIN 18     // Sensor 2 Trigger
#define ECHO2_PIN 19     // Sensor 2 Echo

// Relay Module Pins
#define RELAY_1_PIN 4
#define RELAY_2_PIN 5

// GSM Module Pins
#define GSM_RX_PIN 16
#define GSM_TX_PIN 17

// Buzzer Pin
#define BUZZER_PIN 0

// WiFi Manager Reset Button Pin
#define WIFI_RESET_BUTTON_PIN 23

// Container Level Configuration
#define CONTAINER_HEIGHT 100.0  // Container height in cm (adjust as needed)

#endif // PINS_CONFIG_H