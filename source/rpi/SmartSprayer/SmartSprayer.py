# SmartSprayer.py
# Main application logic for Raspberry Pi version

# Import all config modules
from BUTTON_CONFIG import BUTTON_PINS
from BUZZER_CONFIG import BUZZER_PIN
from FIREBASE_CONFIG import *
from GSM_CONFIG import GSM_PORT, GSM_BAUDRATE
from GSM_RECIPIENTS import RECIPIENTS
from LCD_CONFIG import *
from LED_CONFIG import LED_PINS
from NTP_CONFIG import NTP_SERVER, TIMEZONE
from PINS_CONFIG import *
from RELAY_CONFIG import RELAY_PIN, RELAY_ACTIVE_STATE
from RTC_CONFIG import RTC_I2C_ADDRESS
from SR04_CONFIG import TRIGGER_PIN, ECHO_PIN
from WEATHER_CONFIG import *
from WIFI_CONFIG import WIFI_SSID, WIFI_PASSWORD

# Add your main SmartSprayer logic here



import RPi.GPIO as GPIO
import time
import threading
import sys
from BUTTON_CONFIG import setup_buttons, read_buttons
from BUZZER_CONFIG import setup_buzzer, buzzer_on, buzzer_off, buzzer_beep
from RELAY_CONFIG import setup_relay, relay_on, relay_off
from LED_CONFIG import setup_leds, set_led
from SR04_CONFIG import setup_ultrasonic, read_distance
from RTC_CONFIG import read_rtc_time, set_rtc_time
from NTP_CONFIG import get_ntp_time
from WIFI_CONFIG import wifi_status, wifi_connect
from WEATHER_CONFIG import get_weather
from FIREBASE_CONFIG import firebase_set, firebase_get
from GSM_CONFIG import send_sms
from GSM_RECIPIENTS import RECIPIENTS

def setup():
    GPIO.setmode(GPIO.BCM)
    setup_buttons()
    setup_buzzer()
    setup_relay()
    setup_leds()
    setup_ultrasonic()
    # Add more hardware/component setup as needed
    print("All hardware initialized.")

def cleanup():
    GPIO.cleanup()

def handle_command(command):
    if command == "operate-relay1_on":
        relay_on()
        print("Relay 1 turned ON")
    elif command == "operate-relay1_off":
        relay_off()
        print("Relay 1 turned OFF")
    elif command == "send-sms":
        send_sms(RECIPIENTS[0], "Test SMS from Smart Sprayer")
        print("SMS sent")
    elif command == "send-sms-to-all":
        for r in RECIPIENTS:
            send_sms(r, "Test SMS to all from Smart Sprayer")
        print("SMS sent to all")
    elif command == "check-network":
        print(wifi_status())
    elif command == "get-distance1":
        dist = read_distance()
        print(f"Distance 1: {dist:.2f} cm")
    elif command == "buzzer-on":
        buzzer_on()
        print("Buzzer turned ON")
    elif command == "buzzer-off":
        buzzer_off()
        print("Buzzer turned OFF")
    elif command == "buzzer-beep":
        buzzer_beep()
        print("Buzzer beeped")
    elif command == "led-ok":
        set_led('status', 1)
        print("System OK LED ON")
    elif command == "led-error":
        set_led('warning', 1)
        print("System Error LED ON")
    elif command == "led-clear":
        set_led('status', 0)
        set_led('warning', 0)
        print("System LEDs cleared")
    elif command == "check-weather":
        weather = get_weather()
        if weather and 'rain' in weather.get('weather', [{}])[0].get('main', '').lower():
            print("Weather check: Rain expected today - avoid spraying")
        else:
            print("Weather check: No rain expected today - safe to spray")
    elif command == "get-time":
        print(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    elif command == "get-ntp-time":
        print(f"NTP Time: {get_ntp_time()}")
    elif command == "wifi-reset":
        print("Resetting WiFi settings... (not implemented)")
    elif command == "button-status":
        buttons = read_buttons()
        print(f"Button states: {buttons}")
    elif command == "get-level":
        dist = read_distance()
        print(f"Distance: {dist:.2f} cm")
    else:
        print("Unknown command")

def main():
    print("SmartSprayer system starting on Raspberry Pi...")
    setup()
    try:
        print("System initialized. Entering main loop.")
        while True:
            # Simulate ESP32 loop: handle buttons, alarms, and commands
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                command = sys.stdin.readline().strip()
                if command:
                    handle_command(command)
            # Button and scheduling logic can be added here
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
