# PINS_CONFIG.py
# General GPIO pin assignments for Raspberry Pi version
# NOTE: RPI now communicates with ESP32 via serial
# ESP32 handles all hardware components directly
# These pin definitions are kept for reference only

# Ultrasonic Sensor Pins (handled by ESP32)
TRIG_PIN = 6      # Sensor 1 Trigger
ECHO_PIN = 13     # Sensor 1 Echo
TRIG2_PIN = 19    # Sensor 2 Trigger
ECHO2_PIN = 26    # Sensor 2 Echo

# Relay Module Pins (handled by ESP32)
RELAY_1_PIN = 4
RELAY_2_PIN = 5

# Buzzer Pin (handled by ESP32)
BUZZER_PIN = 12

# Container Level Configuration
CONTAINER_HEIGHT = 100.0  # cm
