# BUTTON_CONFIG.py
# Configuration for button pins and logic for Raspberry Pi version


BUTTON_PINS = {
    'schedule': 17,  # Example GPIO pin
    'manual': 27,
    'reset': 22
}

import RPi.GPIO as GPIO

def setup_buttons():
    for pin in BUTTON_PINS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_buttons():
    return {name: not GPIO.input(pin) for name, pin in BUTTON_PINS.items()}
