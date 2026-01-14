
# PINS_CONFIG.py
# General GPIO pin assignments for Raspberry Pi version


# Ultrasonic Sensor Pins
TRIG_PIN = 6      # Sensor 1 Trigger
ECHO_PIN = 13     # Sensor 1 Echo
TRIG2_PIN = 19    # Sensor 2 Trigger
ECHO2_PIN = 26    # Sensor 2 Echo

# Relay Module Pins
RELAY_1_PIN = 4
RELAY_2_PIN = 5

# GSM Module Pins (for UART, use /dev/serial0 or similar on RPi)
GSM_RX_PIN = 16
GSM_TX_PIN = 17

# LCD Display I2C Pins (handled by I2C bus, but for reference)
LCD_SDA_PIN = 2   # GPIO2 (I2C SDA)
LCD_SCL_PIN = 3   # GPIO3 (I2C SCL)

# Buzzer Pin
BUZZER_PIN = 12

# System Status LED Pins
SYSTEM_OK_LED = 20
SYSTEM_ERROR_LED = 21

# WiFi Manager Reset Button Pin
WIFI_RESET_BUTTON_PIN = 18

# Menu Navigation Buttons
MENU_UP_BUTTON_PIN = 22
MENU_DOWN_BUTTON_PIN = 23
MENU_SELECT_BUTTON_PIN = 24

# Container Level Configuration
CONTAINER_HEIGHT = 100.0  # cm
