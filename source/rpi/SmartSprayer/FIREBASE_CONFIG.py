# FIREBASE_CONFIG.py
# Firebase configuration for Raspberry Pi version


API_KEY = ""
DATABASE_URL = "https://smart-sprayer-default-rtdb.firebaseio.com"
FIREBASE_PROJECT_ID = "smart-sprayer"
FIREBASE_CLIENT_EMAIL = ""
PRIVATE_KEY = ""
USER_EMAIL = ""
USER_PASSWORD = ""
DEVICE_REGISTRATION_ID_TOKEN = ""

import requests

def firebase_set(path, data):
	url = f"{DATABASE_URL}/{path}.json"
	response = requests.put(url, json=data)
	return response.json()

def firebase_get(path):
	url = f"{DATABASE_URL}/{path}.json"
	response = requests.get(url)
	return response.json()
