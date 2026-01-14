# GSM_CONFIG.py
# GSM configuration for Raspberry Pi version


GSM_PORT = "/dev/ttyUSB0"  # Example serial port
GSM_BAUDRATE = 9600

import serial
import time

def send_sms(number, message):
	ser = serial.Serial(GSM_PORT, GSM_BAUDRATE, timeout=1)
	ser.write(b'AT\r')
	time.sleep(0.5)
	ser.write(b'AT+CMGF=1\r')
	time.sleep(0.5)
	ser.write(f'AT+CMGS="{number}"\r'.encode())
	time.sleep(0.5)
	ser.write(message.encode() + b"\x1A")
	time.sleep(2)
	ser.close()
