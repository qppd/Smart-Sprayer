#ifndef PINS_CONFIG_H
#define PINS_CONFIG_H

// Ultrasonic Sensor Pins
#define TRIG_PIN 32      // Sensor 1 Trigger
#define ECHO_PIN 33      // Sensor 1 Echo
#define TRIG2_PIN 25     // Sensor 2 Trigger
#define ECHO2_PIN 26     // Sensor 2 Echo

// Relay Module Pins
#define RELAY_1_PIN 22
#define RELAY_2_PIN 21

// GSM Module Pins
#define GSM_RX_PIN 16
#define GSM_TX_PIN 17

// Buzzer Pin
#define BUZZER_PIN 23

// DS1302 RTC Pins
#define RTC_CLK_PIN 18
#define RTC_DAT_PIN 5
#define RTC_RST_PIN 19  // CE/RST pin

// WiFi Manager Reset Button Pin
#define WIFI_RESET_BUTTON_PIN 13

// Container Level Configuration
// Sensor: Standard HC-SR04 (non-waterproof), min range ~2 cm
// Ultrasonic measures downward from sensor to liquid surface.
// Full tank (16 L) → sensor reads ~12–15 cm; nominal FULL distance = 13 cm
// Empty tank        → sensor reads ~38 cm
// Usable range      = 38 - 13 = 25 cm
// 13 cm  → 100%  (any reading ≤ 13 cm is clamped to 100%)
// 38 cm  → 0%
// 20% critical threshold:
//   liquid height = 25 × 0.20 = 5.0 cm → distance = 38 - 5 = 33 cm
#define CONTAINER_EMPTY_DISTANCE 38.0  // Distance when tank is empty (cm)
#define CONTAINER_FULL_DISTANCE  13.0  // Distance when tank is full / 100% (cm)
#define CONTAINER_CAPACITY_LITERS 16.0 // Tank capacity in liters

// Pump Configuration
#define PUMP_FLOW_RATE_ML_PER_MIN 5000.0  // 5 Liters per minute = 5000 mL/min

#endif // PINS_CONFIG_H