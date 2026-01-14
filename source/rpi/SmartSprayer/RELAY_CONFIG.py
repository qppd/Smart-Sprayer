# RELAY_CONFIG.py
# Relay configuration for Raspberry Pi version


RELAY_PIN = 5
RELAY_ACTIVE_STATE = 1  # 1 for HIGH, 0 for LOW

import RPi.GPIO as GPIO

def setup_relay():
	GPIO.setup(RELAY_PIN, GPIO.OUT)
	GPIO.output(RELAY_PIN, not RELAY_ACTIVE_STATE)

def relay_on():
	GPIO.output(RELAY_PIN, RELAY_ACTIVE_STATE)

def relay_off():
	GPIO.output(RELAY_PIN, not RELAY_ACTIVE_STATE)
