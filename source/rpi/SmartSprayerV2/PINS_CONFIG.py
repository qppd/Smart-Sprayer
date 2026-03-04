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
# Total container height = 38 cm
# Sensor blind zone (minimum range) = 22 cm — readings below this are INVALID
# Usable measurable range = 38 - 22 = 16 cm (bottom 16 cm of container)
# 22 cm distance from sensor = FULL (100%, liquid at usable range top)
# 38 cm distance from sensor = EMPTY (0%, liquid at bottom)
CONTAINER_EMPTY_DISTANCE = 38.0  # cm - distance when tank is empty (equals total height)
CONTAINER_FULL_DISTANCE = 22.0   # cm - sensor minimum range / full level distance
CONTAINER_CAPACITY_LITERS = 16.0 # Tank capacity in liters

# For backward compatibility
CONTAINER_HEIGHT = CONTAINER_EMPTY_DISTANCE - CONTAINER_FULL_DISTANCE  # 16 cm of usable fill height

# Pump specifications
PUMP_FLOW_RATE_ML_PER_MIN = 5000.0  # 5 liters per minute
