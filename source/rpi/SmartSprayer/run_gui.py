# run_gui.py
# Launcher script for Smart Sprayer GUI
# Run this file from PyCharm or command line: python run_gui.py

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Check for required packages
def check_dependencies():
    """Check if required packages are installed"""
    required = ['customtkinter', 'tkcalendar']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("=" * 60)
        print("MISSING DEPENDENCIES")
        print("=" * 60)
        print("\nThe following packages are required but not installed:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nPlease install them using:")
        print("  pip install -r requirements.txt")
        print("\nOr individually:")
        for pkg in missing:
            print(f"  pip install {pkg}")
        print("=" * 60)
        return False
    
    return True


def main():
    """Main entry point"""
    print("=" * 60)
    print("SMART SPRAYER CONTROL SYSTEM")
    print("=" * 60)
    print("\nInitializing...")
    
    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("✓ Dependencies check passed")
    print("✓ Running in PC mode (mock hardware)")
    print("\nStarting GUI...\n")
    
    # Import and run UI
    try:
        from ui.main_ui import main as ui_main
        ui_main()
    except Exception as e:
        print(f"\nERROR: Failed to start GUI")
        print(f"Error: {e}")
        print("\nPlease check:")
        print("1. All dependencies are installed")
        print("2. You're running from the correct directory")
        print("3. All project files are present")
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
