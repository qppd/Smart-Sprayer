# LED_CONFIG.py
# LED configuration for Raspberry Pi version


LED_PINS = {
    'status': 23,  # Example GPIO pin
    'warning': 24
}

import RPi.GPIO as GPIO

def setup_leds():
    for pin in LED_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

def set_led(name, state):
    if name in LED_PINS:
        GPIO.output(LED_PINS[name], 1 if state else 0)
