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
# Distance measurement: sensor at top of container
# 22 cm distance from sensor = FULL (liquid close to sensor, 16L)
# 80 cm distance from sensor = EMPTY (liquid far from sensor, 0L)
CONTAINER_EMPTY_DISTANCE = 80.0  # cm - distance when empty
CONTAINER_FULL_DISTANCE = 22.0   # cm - distance when full
CONTAINER_CAPACITY_LITERS = 16.0 # Tank capacity in liters

# For backward compatibility
CONTAINER_HEIGHT = CONTAINER_EMPTY_DISTANCE - CONTAINER_FULL_DISTANCE  # 58 cm of usable fill height

# Pump specifications
PUMP_FLOW_RATE_ML_PER_MIN = 5000.0  # 5 liters per minute
