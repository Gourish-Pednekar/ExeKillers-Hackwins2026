# Fraud Detection Payment System

A multi-user payment demo system with real-time fraud detection using machine learning.

## Features

- **Firebase Authentication**: Email/password login and registration
- **Real-time Risk Detection**: Automatically detects IP changes, device changes, and unusual transaction patterns
- **ML-powered Fraud Detection**: Uses trained Random Forest model for fraud prediction
- **User State Tracking**: Stores user session data in Firestore for pattern analysis
- **Demo Ready**: Easy to demonstrate multi-device/IP detection scenarios

## Architecture

```
Frontend (HTML/JS) → Firebase Auth → FastAPI Backend → Firestore → ML Model
```

## Setup Instructions

### 1. Firebase Setup

1. Create a new Firebase project at https://console.firebase.google.com
2. Enable Authentication (Email/Password) and Firestore Database
3. Go to Project Settings → Service Accounts → Generate Private Key
4. Download the JSON file and copy the credentials to `.env` file

### 2. Environment Configuration

Copy `.env.example` to `.env` and fill in your Firebase credentials:

```bash
cp .env.example .env
```

Update `.env` with your Firebase service account details:
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_PRIVATE_KEY_ID`: From service account JSON
- `FIREBASE_PRIVATE_KEY`: From service account JSON (include newlines)
- `FIREBASE_CLIENT_EMAIL`: From service account JSON
- `FIREBASE_CLIENT_ID`: From service account JSON

### 3. Frontend Firebase Config

Update the Firebase configuration in `static/index.html` (line ~140):

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

Get these values from Firebase Console → Project Settings → General → Your apps.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
uvicorn app:app --reload
```

Visit `http://localhost:8000` to access the application.

## Demo Scenarios

### 1. Normal Transaction
- Register and login from a single device/network
- Make a payment - should be approved

### 2. IP Change Detection
- Login from one network
- Make a payment (approved)
- Login from different network (different IP)
- Make another payment - flagged for IP change

### 3. Device Change Detection
- Login from one browser/device
- Make a payment (approved)
- Login from different browser/device
- Make another payment - flagged for device change

### 4. Transaction Pattern Detection
- Make multiple transactions within 24 hours
- Transaction count increases with each payment
- High transaction counts may trigger fraud detection

### 5. Time-based Risk
- Make transactions between 12AM-5AM
- System flags as "odd time" risk factor

## API Endpoints

- `POST /verify-token` - Verify Firebase ID token
- `POST /register-user` - Register user in Firestore
- `POST /payment` - Process payment with fraud detection
- `GET /user/{user_id}` - Get user data for verification
- `POST /predict` - Direct ML model prediction (existing)

## Risk Factors

The system automatically calculates these risk factors:

1. **is_mal_ip**: 1 if current IP ≠ last IP
2. **is_mal_device**: 1 if current device ≠ last device  
3. **odd_time**: 1 if transaction time is 12AM-5AM
4. **txn_count_24h**: Number of transactions in last 24 hours

## ML Model Input Format

```json
{
    "amount": 100.0,
    "is_mal_ip": 0,
    "is_mal_device": 0, 
    "odd_time": 0,
    "txn_count_24h": 1
}
```

## Firestore Schema

Collection: `users`
Document ID: Firebase UID
Fields:
```json
{
    "email": "user@example.com",
    "last_ip": "192.168.1.1",
    "last_device": "Mozilla/5.0...",
    "last_txn_time": "2023-01-01T12:00:00",
    "txn_count_24h": 3
}
```

## Verification

Use the `/user/{user_id}` endpoint or check Firestore directly to verify:
- IP changes between sessions
- Device fingerprint changes
- Transaction count patterns
- Timestamp tracking

## Security Notes

- Firebase ID tokens are verified server-side
- User data is stored securely in Firestore
- No sensitive data is exposed to frontend
- Real IP and device data are collected automatically
