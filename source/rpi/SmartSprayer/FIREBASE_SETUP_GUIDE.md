# Firebase Setup Guide

## Quick Setup - Your Firebase Project

Your Firebase project is already created: **smart-sprayer-154fa**

## Step 1: Get Your Web API Key

You need to get the `apiKey` for Pyrebase4 to work. Follow these steps:

### Option A: Via Firebase Console (Recommended)

1. **Go to Firebase Console**
   - Visit: https://console.firebase.google.com/
   - Login with: `quezon.province.pd@gmail.com`

2. **Select Your Project**
   - Click on: **smart-sprayer-154fa**

3. **Get API Key**
   - Click the **gear icon** (⚙️) next to "Project Overview"
   - Select **Project settings**
   - Scroll down to **"Your apps"** section
   
4. **Add Web App (if not exists)**
   - If you see a web app (</> icon), skip to step 5
   - If not, click **"Add app"** button
   - Select **Web** (</> icon)
   - Give it a nickname: "Smart Sprayer Web"
   - Click **Register app**

5. **Copy Configuration**
   - You'll see a config object like this:
   ```javascript
   const firebaseConfig = {
     apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
     authDomain: "smart-sprayer-154fa.firebaseapp.com",
     databaseURL: "https://smart-sprayer-154fa-default-rtdb.firebaseio.com",
     projectId: "smart-sprayer-154fa",
     storageBucket: "smart-sprayer-154fa.appspot.com",
     messagingSenderId: "XXXXXXXXXXXX",
     appId: "X:XXXXXXXXXXXX:web:XXXXXXXXXXXXXX"
   };
   ```

6. **Update firebase_credentials.py**
   - Copy the `apiKey` value
   - Open: `source/rpi/SmartSprayer/firebase_credentials.py`
   - Replace the placeholder with your actual apiKey:
   ```python
   FIREBASE_CONFIG = {
       "apiKey": "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXX",  # Paste here
       ...
   }
   ```

### Option B: Using Firebase CLI

If you have Firebase CLI installed:

```bash
firebase projects:list
firebase apps:list --project smart-sprayer-154fa
firebase apps:sdkconfig WEB
```

## Step 2: Verify Configuration

Your current configuration:

```python
FIREBASE_CONFIG = {
    "authDomain": "smart-sprayer-154fa.firebaseapp.com",
    "databaseURL": "https://smart-sprayer-154fa-default-rtdb.firebaseio.com",
    "storageBucket": "smart-sprayer-154fa.appspot.com",
    "apiKey": "GET_FROM_CONSOLE",  # ← Need this!
}

FIREBASE_USER = {
    "email": "quezon.province.pd@gmail.com",
    "password": "Admin1+"
}
```

## Step 3: Set Up Authentication

Make sure Email/Password authentication is enabled:

1. In Firebase Console, go to **Authentication**
2. Click **Get started** (if not set up yet)
3. Go to **Sign-in method** tab
4. Enable **Email/Password** provider
5. Verify user exists: `quezon.province.pd@gmail.com`
   - If not, add it in the **Users** tab

## Step 4: Configure Database Rules

For testing, set permissive rules (update later for production):

1. Go to **Realtime Database**
2. Click **Rules** tab
3. Use these rules:

```json
{
  "rules": {
    "devices": {
      "$deviceId": {
        ".read": "auth != null",
        ".write": "auth != null"
      }
    }
  }
}
```

4. Click **Publish**

## Step 5: Test Connection

Run this test script:

```python
cd source/rpi/SmartSprayer
python -c "from core.firebase_service import get_firebase_service; fb = get_firebase_service(); print('Connected!' if fb.connected else 'Connection failed')"
```

## Troubleshooting

### Error: "Invalid API key"
- Double-check the apiKey in firebase_credentials.py
- Make sure there are no extra spaces or quotes
- Verify it's the Web API key, not service account key

### Error: "Auth domain not found"
- Verify authDomain is: `smart-sprayer-154fa.firebaseapp.com`
- Check if Hosting is enabled in Firebase Console

### Error: "Permission denied"
- Check Database Rules allow authenticated access
- Verify user email/password is correct
- Make sure user exists in Authentication tab

### Error: "Module 'pyrebase' not found"
```bash
pip install Pyrebase4
```

## Files Created

✅ `firebase_credentials.py` - Your credentials (not in git)
✅ `serviceAccountKey.json` - Service account for admin operations (not in git)
✅ `.gitignore` - Updated to exclude credentials

## Security Notes

⚠️ **IMPORTANT**
- `firebase_credentials.py` is in .gitignore - DO NOT commit
- `serviceAccountKey.json` is in .gitignore - DO NOT commit
- Never share these files publicly
- Never commit to GitHub
- Keep credentials secure

## What's Next

Once you have the API key configured:

1. **Test Firebase connection**
   ```python
   from core.firebase_service import get_firebase_service
   fb = get_firebase_service()
   print(f"Connected: {fb.connected}")
   ```

2. **Enable auto-sync**
   ```python
   fb.enable_sync()
   ```

3. **Test schedule upload**
   ```python
   from core.data_store import get_data_store
   ds = get_data_store()
   
   schedule = ds.add_schedule({
       'date': '2026-02-02',
       'time': '08:00',
       'spray_type': 'Fertilizer',
       'container': 'Container 1',
       'volume_ml': 1000
   })
   
   print("Schedule created and synced to Firebase!")
   ```

4. **Check Firebase Console**
   - Go to Realtime Database
   - You should see: `devices/SmartSprayer_001/schedules/...`

## Support

If you encounter issues:
1. Check Firebase Console for error messages
2. Review logs in `source/rpi/SmartSprayer/logs/`
3. Verify all credentials are correct
4. Make sure Pyrebase4 is installed
5. Check internet connection on RPI

---

**Your Firebase Project:** smart-sprayer-154fa
**Database URL:** https://smart-sprayer-154fa-default-rtdb.firebaseio.com
**Auth Email:** quezon.province.pd@gmail.com
