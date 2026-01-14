# WIFI_CONFIG.py
# Wi-Fi configuration for Raspberry Pi version


WIFI_SSID = ""
WIFI_PASSWORD = ""

import subprocess

def wifi_status():
	result = subprocess.run(['iwgetid'], capture_output=True, text=True)
	return result.stdout.strip()

def wifi_connect(ssid, password):
	# This is a stub. On RPi OS, use nmcli or wpa_cli for real connection management.
	cmd = f'nmcli dev wifi connect "{ssid}" password "{password}"'
	result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
	return result.stdout.strip()
