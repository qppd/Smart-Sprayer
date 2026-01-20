# verify_installation.py
# Verify Smart Sprayer GUI installation and dependencies

import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_status(item, status, detail=""):
    """Print status line"""
    icon = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"
    reset = "\033[0m"
    
    status_text = f"{color}{icon}{reset} {item}"
    if detail:
        status_text += f" ({detail})"
    print(status_text)

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    is_ok = version.major >= 3 and version.minor >= 8
    print_status(
        f"Python {version_str}",
        is_ok,
        "Required: 3.8+" if is_ok else "ERROR: Need 3.8 or higher"
    )
    
    return is_ok

def check_dependencies():
    """Check required Python packages"""
    print_header("Dependency Check")
    
    dependencies = {
        'customtkinter': 'CustomTkinter GUI framework',
        'tkcalendar': 'Calendar widget',
        'requests': 'HTTP requests'
    }
    
    all_ok = True
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            print_status(f"{package}", True, description)
        except ImportError:
            print_status(f"{package}", False, f"MISSING - {description}")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Install missing packages with:")
        print("   pip install -r requirements.txt")
    
    return all_ok

def check_project_structure():
    """Check project file structure"""
    print_header("Project Structure Check")
    
    base_dir = Path(__file__).parent
    
    required_files = {
        'Main Files': [
            'run_gui.py',
            'sample_data_generator.py',
            'requirements.txt',
            'README_GUI.md',
            'QUICK_START.md'
        ],
        'Hardware Module': [
            'hardware/__init__.py',
            'hardware/hardware_interface.py',
            'hardware/mock_hardware.py'
        ],
        'Core Logic': [
            'core/__init__.py',
            'core/logger.py',
            'core/data_store.py',
            'core/scheduler.py',
            'core/reschedule_logic.py'
        ],
        'UI Components': [
            'ui/__init__.py',
            'ui/main_ui.py',
            'ui/dashboard.py',
            'ui/scheduling.py',
            'ui/previous_data.py',
            'ui/notifications.py',
            'ui/logs_viewer.py'
        ]
    }
    
    all_ok = True
    
    for category, files in required_files.items():
        print(f"\n{category}:")
        for file_path in files:
            full_path = base_dir / file_path
            exists = full_path.exists()
            print_status(f"  {file_path}", exists)
            if not exists:
                all_ok = False
    
    return all_ok

def check_directories():
    """Check required directories"""
    print_header("Directory Structure Check")
    
    base_dir = Path(__file__).parent
    
    directories = ['hardware', 'core', 'ui', 'data', 'logs']
    
    all_ok = True
    
    for dir_name in directories:
        dir_path = base_dir / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        print_status(f"{dir_name}/", exists)
        if not exists:
            all_ok = False
    
    return all_ok

def check_imports():
    """Check if project modules can be imported"""
    print_header("Module Import Check")
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    modules = [
        'hardware.hardware_interface',
        'hardware.mock_hardware',
        'core.logger',
        'core.data_store',
        'core.scheduler',
        'core.reschedule_logic'
    ]
    
    all_ok = True
    
    for module in modules:
        try:
            __import__(module)
            print_status(module, True)
        except Exception as e:
            print_status(module, False, str(e)[:50])
            all_ok = False
    
    return all_ok

def generate_system_info():
    """Generate system information"""
    print_header("System Information")
    
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Working directory: {os.getcwd()}")

def main():
    """Main verification routine"""
    print("\n" + "=" * 70)
    print("  SMART SPRAYER GUI - INSTALLATION VERIFICATION")
    print("=" * 70)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Project Structure", check_project_structure),
        ("Module Imports", check_imports)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n✗ Error during {check_name}: {e}")
            results[check_name] = False
    
    # System info
    generate_system_info()
    
    # Final summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        print_status(check_name, passed)
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\nYour Smart Sprayer GUI is ready to use!")
        print("\nNext steps:")
        print("  1. Generate sample data: python sample_data_generator.py")
        print("  2. Launch the GUI: python run_gui.py")
        print("  3. Read QUICK_START.md for usage guide")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the GUI.")
        print("\nCommon fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Ensure you're in the correct directory")
        print("  • Check that all files were created properly")
    
    print("=" * 70 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
