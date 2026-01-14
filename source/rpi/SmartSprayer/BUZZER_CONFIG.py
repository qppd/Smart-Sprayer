# BUZZER_CONFIG.py
# Configuration for buzzer pin and logic for Raspberry Pi version


BUZZER_PIN = 18  # Example GPIO pin

import RPi.GPIO as GPIO
import time

def setup_buzzer():
	GPIO.setup(BUZZER_PIN, GPIO.OUT)
	GPIO.output(BUZZER_PIN, 0)

def buzzer_on():
	GPIO.output(BUZZER_PIN, 1)

def buzzer_off():
	GPIO.output(BUZZER_PIN, 0)

def buzzer_beep(duration=0.2):
	buzzer_on()
	time.sleep(duration)
	buzzer_off()
