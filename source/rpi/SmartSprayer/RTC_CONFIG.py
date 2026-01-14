# RTC_CONFIG.py
# RTC configuration for Raspberry Pi version


RTC_I2C_ADDRESS = 0x68  # Example I2C address for DS3231

import smbus2
import time

def bcd2dec(bcd):
	return (bcd & 0x0F) + ((bcd >> 4) * 10)

def dec2bcd(dec):
	return ((dec // 10) << 4) + (dec % 10)

def read_rtc_time():
	bus = smbus2.SMBus(1)
	data = bus.read_i2c_block_data(RTC_I2C_ADDRESS, 0x00, 7)
	sec = bcd2dec(data[0])
	minute = bcd2dec(data[1])
	hour = bcd2dec(data[2])
	day = bcd2dec(data[4])
	month = bcd2dec(data[5])
	year = bcd2dec(data[6]) + 2000
	return year, month, day, hour, minute, sec

def set_rtc_time(year, month, day, hour, minute, sec):
	bus = smbus2.SMBus(1)
	data = [dec2bcd(sec), dec2bcd(minute), dec2bcd(hour), 0, dec2bcd(day), dec2bcd(month), dec2bcd(year-2000)]
	bus.write_i2c_block_data(RTC_I2C_ADDRESS, 0x00, data)
