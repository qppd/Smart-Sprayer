# SR04_CONFIG.py
# Ultrasonic sensor configuration for Raspberry Pi version


TRIGGER_PIN = 6
ECHO_PIN = 13

import RPi.GPIO as GPIO
import time

def setup_ultrasonic():
	GPIO.setup(TRIGGER_PIN, GPIO.OUT)
	GPIO.setup(ECHO_PIN, GPIO.IN)
	GPIO.output(TRIGGER_PIN, 0)

def read_distance():
	GPIO.output(TRIGGER_PIN, 1)
	time.sleep(0.00001)
	GPIO.output(TRIGGER_PIN, 0)
	start = time.time()
	stop = time.time()
	while GPIO.input(ECHO_PIN) == 0:
		start = time.time()
	while GPIO.input(ECHO_PIN) == 1:
		stop = time.time()
	elapsed = stop - start
	distance = (elapsed * 34300) / 2  # cm
	return distance
