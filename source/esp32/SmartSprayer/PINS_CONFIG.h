#ifndef PINS_CONFIG_H
#define PINS_CONFIG_H

// Ultrasonic Sensor Pins
#define TRIG_PIN 12      // Sensor 1 Trigger
#define ECHO_PIN 13      // Sensor 1 Echo
#define TRIG2_PIN 14     // Sensor 2 Trigger
#define ECHO2_PIN 16     // Sensor 2 Echo

// Relay Module Pins
#define RELAY_1_PIN 4
#define RELAY_2_PIN 5

// GSM Module Pins
#define GSM_RX_PIN 10
#define GSM_TX_PIN 11

// LCD Display I2C Pins (ESP32 default)
#define LCD_SDA_PIN 21
#define LCD_SCL_PIN 22

// Buzzer Pin
#define BUZZER_PIN 17

// System Status LED Pins
#define SYSTEM_OK_LED 18
#define SYSTEM_ERROR_LED 19

// WiFi Manager Reset Button Pin
#define WIFI_RESET_BUTTON_PIN 23

#endif // PINS_CONFIG_H