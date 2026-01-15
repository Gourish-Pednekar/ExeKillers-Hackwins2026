# Quick Firebase Setup Guide

## 1. Create Firebase Project
1. Go to https://console.firebase.google.com
2. Click "Add project" 
3. Enter project name (e.g., "fraud-detection-demo")
4. Enable Google Analytics (optional)
5. Click "Create project"

## 2. Enable Services
1. In the Firebase Console, go to "Authentication"
2. Click "Get Started"
3. Enable "Email/Password" sign-in method
4. Save changes

5. Go to "Firestore Database"
6. Click "Create database"
7. Choose "Start in test mode" (for demo)
8. Select a location
9. Click "Create"

## 3. Get Service Account Credentials
1. Go to Project Settings (gear icon)
2. Go to "Service accounts" tab
3. Click "Generate new private key"
4. Download the JSON file
5. Copy the values to your `.env` file

## 4. Get Frontend Config
1. In Project Settings, go to "General" tab
2. Scroll down to "Your apps" section
3. Click the web app icon (</>)
4. Copy the config values to `static/index.html`

## 5. Update Configuration Files

### Backend (.env file)
```bash
cp .env.example .env
```
Edit `.env` with your service account JSON values:
- FIREBASE_PROJECT_ID
- FIREBASE_PRIVATE_KEY_ID  
- FIREBASE_PRIVATE_KEY (include newlines)
- FIREBASE_CLIENT_EMAIL
- FIREBASE_CLIENT_ID

### Frontend (static/index.html)
Update the firebaseConfig object (around line 140):
```javascript
const firebaseConfig = {
    apiKey: "your-web-api-key",
    authDomain: "your-project.firebaseapp.com", 
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "your-sender-id",
    appId: "your-app-id"
};
```

## 6. Test the System
1. Restart the server: `uvicorn app:app --reload`
2. Visit http://localhost:8000
3. Register a new user
4. Make a payment
5. Try logging in from different device/network to see fraud detection

## Demo Scenarios
- **Normal**: Same device, same network
- **IP Change**: Same user, different WiFi/network
- **Device Change**: Same user, different browser/device  
- **Time Risk**: Transactions between 12AM-5AM
- **Pattern Risk**: Multiple transactions within 24 hours
