# NTP_CONFIG.py
# NTP configuration for Raspberry Pi version


NTP_SERVER = "pool.ntp.org"
TIMEZONE = "UTC"

import ntplib
from time import ctime

def get_ntp_time():
	client = ntplib.NTPClient()
	response = client.request(NTP_SERVER, version=3)
	return ctime(response.tx_time)
