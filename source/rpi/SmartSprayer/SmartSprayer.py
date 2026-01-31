# SmartSprayer.py
# Main application logic for Raspberry Pi version
# NOTE: This file is deprecated in favor of the GUI application (run_gui.py)
# RPI now communicates with ESP32 via serial for all hardware operations

# Import only necessary config modules
from FIREBASE_CONFIG import *
from WEATHER_CONFIG import *
from WIFI_CONFIG import WIFI_SSID, WIFI_PASSWORD
from PINS_CONFIG import CONTAINER_HEIGHT

import time
import sys
import select

# NOTE: Hardware operations should now use hardware_interface
# from hardware.hardware_interface import get_hardware
# hardware = get_hardware()

def handle_command(command):
    """
    Command handler - deprecated
    For hardware operations, use the GUI (run_gui.py) which uses hardware_interface
    """
    print(f"Command received: {command}")
    print("NOTE: Use run_gui.py for full functionality with ESP32 communication")
    
    if command == "help":
        print("Available commands:")
        print("  help - Show this help message")
        print("  exit - Exit the program")
        print("\nFor full functionality, use: python run_gui.py")
    elif command == "exit":
        return False
    else:
        print("Unknown command. Type 'help' for available commands.")
    
    return True

def main():
    print("=" * 60)
    print("SmartSprayer - Command Line Interface")
    print("=" * 60)
    print("\nNOTE: This is a legacy CLI interface.")
    print("For full GUI functionality with ESP32, use:")
    print("  python run_gui.py")
    print("\nType 'help' for available commands or 'exit' to quit.")
    print("=" * 60)
    
    try:
        while True:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                command = sys.stdin.readline().strip()
                if command:
                    if not handle_command(command):
                        break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        print("Goodbye!")

if __name__ == "__main__":
    main()
