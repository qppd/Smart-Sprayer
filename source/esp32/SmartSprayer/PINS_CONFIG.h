#ifndef PINS_CONFIG_H
#define PINS_CONFIG_H

// Ultrasonic Sensor Pins
#define TRIG_PIN 12      // Sensor 1 Trigger
#define ECHO_PIN 13      // Sensor 1 Echo
#define TRIG2_PIN 15     // Sensor 2 Trigger (changed from 14 to avoid conflict with RTC)
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

// Menu Navigation Buttons (for LCD menu and scheduling)
#define MENU_UP_BUTTON_PIN 25      // GPIO 25 - Menu up/navigation
#define MENU_DOWN_BUTTON_PIN 26    // GPIO 26 - Menu down/navigation  
#define MENU_SELECT_BUTTON_PIN 27  // GPIO 27 - Menu select/save

// DS1302 RTC Pins
#define RTC_CE_PIN 32    // Chip Enable
#define RTC_IO_PIN 33    // Data I/O
#define RTC_CLK_PIN 14   // Serial Clock (Note: GPIO 14 was previously ultrasonic, but we'll reuse it)

// Container Level Configuration
#define CONTAINER_HEIGHT 100.0  // Container height in cm (adjust as needed)

#endif // PINS_CONFIG_H