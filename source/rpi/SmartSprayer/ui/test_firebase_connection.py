#!/usr/bin/env python3
"""
Test Firebase Connection for Smart Sprayer
Tests pyrebase4 setup following RoboSort working pattern
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("FIREBASE CONNECTION TEST")
print("=" * 60)

# Test 1: Check if pyrebase is available
print("\n1. Testing pyrebase import...")
import pyrebase

# Test 2: Check if credentials are available
print("\n2. Testing credentials import...")
try:
    from firebase_credentials import FIREBASE_CONFIG, FIREBASE_USER
    print("   ✓ Firebase credentials imported")
    print(f"   API Key: {FIREBASE_CONFIG.get('apiKey', 'N/A')[:20]}...")
    print(f"   Database URL: {FIREBASE_CONFIG.get('databaseURL', 'N/A')}")
    print(f"   Auth Email: {FIREBASE_USER.get('email', 'N/A')}")
except ImportError as e:
    print(f"   ✗ Failed to import credentials: {e}")
    sys.exit(1)

# Test 3: Initialize Firebase
print("\n3. Testing Firebase initialization...")
try:
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    db = firebase.database()
    auth = firebase.auth()
    print("   ✓ Firebase app initialized")
    print("   ✓ Database reference obtained")
    print("   ✓ Auth reference obtained")
except Exception as e:
    print(f"   ✗ Firebase initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Authenticate
print("\n4. Testing Firebase authentication...")
try:
    user = auth.sign_in_with_email_and_password(
        FIREBASE_USER['email'],
        FIREBASE_USER['password']
    )
    print(f"   ✓ Authenticated as: {FIREBASE_USER['email']}")
    print(f"   User ID: {user.get('localId', 'N/A')[:20]}...")
except Exception as e:
    print(f"   ✗ Authentication failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Write test data
print("\n5. Testing Firebase write operation...")
try:
    from datetime import datetime
    test_data = {
        "test_timestamp": datetime.now().isoformat(),
        "test_message": "Firebase connection test successful",
        "pyrebase_version": pyrebase_version
    }
    
    db.child("devices").child("SmartSprayer_001").child("test").set(test_data)
    print("   ✓ Test data written to Firebase")
    print(f"   Path: /devices/SmartSprayer_001/test")
except Exception as e:
    print(f"   ✗ Write operation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Read test data
print("\n6. Testing Firebase read operation...")
try:
    result = db.child("devices").child("SmartSprayer_001").child("test").get()
    if result.val():
        print("   ✓ Test data read from Firebase")
        print(f"   Data: {result.val()}")
    else:
        print("   ⚠ No data returned (but read succeeded)")
except Exception as e:
    print(f"   ✗ Read operation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Test FirebaseService class
print("\n7. Testing FirebaseService class...")
try:
    from core.firebase_service import FirebaseService
    
    fs = FirebaseService(device_id="SmartSprayer_001")
    print(f"   ✓ FirebaseService instantiated")
    print(f"   Connected: {fs.connected}")
    print(f"   Device ID: {fs.device_id}")
    
    if fs.connected:
        print("   ✓ Firebase service is connected and ready")
        
        # Test uploading a test schedule
        test_schedule = {
            "id": "TEST_SCHEDULE_001",
            "date": "2026-02-08",
            "time": "08:00",
            "spray_type": "pesticide",
            "container": 1,
            "volume_ml": 1000,
            "status": "pending"
        }
        
        if fs.upload_schedule(test_schedule):
            print("   ✓ Test schedule uploaded successfully")
        else:
            print("   ⚠ Test schedule upload failed (but connection OK)")
    else:
        print("   ✗ Firebase service failed to connect")
        
except Exception as e:
    print(f"   ✗ FirebaseService test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("FIREBASE CONNECTION TEST COMPLETE")
print("=" * 60)
print("\nIf all tests passed, Firebase is working correctly!")
print("You can now use Firebase features in the Smart Sprayer app.")
print("\nTo view data in Firebase Console:")
print(f"https://console.firebase.google.com/project/smart-sprayer-154fa/database")
