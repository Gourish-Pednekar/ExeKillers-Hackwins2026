from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import joblib
import pandas as pd
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import firebase_config
import os

app = FastAPI()
model = joblib.load("fraud_model.pkl")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase initialization
try:
    print("Loading Firebase config...")
    config = firebase_config.FIREBASE_CONFIG
    print(f"Project ID: {config.get('project_id', 'NOT SET')}")
    print(f"Client email: {config.get('client_email', 'NOT SET')}")
    
    cred = credentials.Certificate(config)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase initialized successfully!")
except Exception as e:
    print(f"❌ Firebase initialization error: {e}")
    print("Please check your .env file with Firebase credentials")
    print("Common issues:")
    print("- Private key not properly formatted with \\n")
    print("- Missing required fields")
    print("- Invalid service account credentials")
    db = None

# Pydantic models
class PaymentRequest(BaseModel):
    user_id: str
    amount: float
    device_fingerprint: str

class User(BaseModel):
    email: str
    last_ip: Optional[str] = None
    last_device: Optional[str] = None
    last_txn_time: Optional[str] = None
    txn_count_24h: int = 0

@app.post("/predict")
def predict(txn: dict):
    df = pd.DataFrame([txn])
    pred = model.predict(df)[0]
    return {"prediction": "Fraud" if pred == 1 else "Normal"}

@app.post("/verify-token")
async def verify_token(request: Request):
    """Verify Firebase ID token"""
    try:
        data = await request.json()
        id_token = data.get("idToken")
        
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        email = decoded_token.get("email", "")
        
        return {"uid": uid, "email": email}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/payment")
async def process_payment(payment: PaymentRequest, request: Request):
    """Process payment with fraud detection"""
    print(f"DEBUG: db is None? {db is None}")
    
    # Test mode - bypass Firebase for now
    if db is None:
        print("⚠️  Running in TEST MODE - Firebase not configured")
        
        # Get real data from request
        current_ip = request.client.host
        current_device = payment.device_fingerprint
        current_time = datetime.now()
        
        # Simulated user data for TEST MODE
        user_data = {
            "last_ip": None,
            "last_device": None,
            "ip_change_count": 0,
            "device_change_count": 0
        }

        # Detect changes
        ip_changed = current_ip != user_data["last_ip"]
        device_changed = current_device != user_data["last_device"]
        odd_time = current_time.hour < 5


        # Update counters
        ip_change_count = user_data.get("ip_change_count", 0)
        device_change_count = user_data.get("device_change_count", 0)

        if ip_changed and user_data.get("last_ip") is not None:
            ip_change_count += 1

        if device_changed and user_data.get("last_device") is not None:
            device_change_count += 1

        # ML binary flags (KEEP THESE)
        is_mal_ip = 1 if ip_changed else 0
        is_mal_device = 1 if device_changed else 0

        txn_count_24h = 1  # First transaction
        
        # Prepare ML input
        ml_input = {
            "amount": payment.amount,
            "is_mal_ip": is_mal_ip,
            "is_mal_device": is_mal_device,
            "odd_time": odd_time,
            "txn_count_24h": txn_count_24h
        }
        
        # Get ML prediction
        df = pd.DataFrame([ml_input])
        pred = model.predict(df)[0]
        prediction = "Fraud" if pred == 1 else "Normal"
        
        return {
        "prediction": prediction,
        "risk_factors": {
            "ip_change_count": 0,
            "device_change_count": 0,
            "odd_time": odd_time
        },
        "detected_data": {
            "ip": current_ip,
            "device": current_device,
            "time": current_time.isoformat()
        },
        "allowed": prediction == "Normal",
        "test_mode": True
}

    
    print("DEBUG: Using Firebase code path")
    # Original Firebase code (when configured)
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Get real data from request
    current_ip = request.client.host
    current_device = payment.device_fingerprint
    current_time = datetime.now()
    
    # Get user data from Firestore
    user_ref = db.collection("users").document(payment.user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user_doc.to_dict()
    ip_change_count = user_data.get("ip_change_count", 0)
    device_change_count = user_data.get("device_change_count", 0)

    if current_ip != user_data.get("last_ip") and user_data.get("last_ip") is not None:
        ip_change_count += 1

    if current_device != user_data.get("last_device") and user_data.get("last_device") is not None:
        device_change_count += 1

    # Calculate risk flags
    is_mal_ip = 1 if current_ip != user_data.get("last_ip") else 0
    is_mal_device = 1 if current_device != user_data.get("last_device") else 0
    odd_time = 1 if current_time.hour < 5 else 0  # 12AM-5AM
    
    # Calculate transaction count
    last_txn_time = user_data.get("last_txn_time")
    if last_txn_time:
        last_txn = datetime.fromisoformat(last_txn_time.replace("Z", "+00:00"))
        if current_time - last_txn < timedelta(hours=24):
            txn_count_24h = user_data.get("txn_count_24h", 0) + 1
        else:
            txn_count_24h = 1
    else:
        txn_count_24h = 1
    
    # Prepare ML input
    ml_input = {
        "amount": payment.amount,
        "is_mal_ip": is_mal_ip,
        "is_mal_device": is_mal_device,
        "odd_time": odd_time,
        "txn_count_24h": txn_count_24h
    }
    
    # Get ML prediction
    df = pd.DataFrame([ml_input])
    pred = model.predict(df)[0]
    prediction = "Fraud" if pred == 1 else "Normal"
    
    # Update Firestore with current session data
    user_ref.update({
        "last_ip": current_ip,
        "last_device": current_device,
        "last_txn_time": current_time.isoformat(),
        "txn_count_24h": txn_count_24h,
        "ip_change_count": ip_change_count,
        "device_change_count": device_change_count
    })
    
    return {
        "prediction": prediction,
        "risk_factors": {
            "ip_change_count": ip_change_count,
            "device_change_count": device_change_count,
            "odd_time": odd_time
        }

,
        "detected_data": {
            "ip": current_ip,
            "device": current_device,
            "time": current_time.isoformat()
        },
        "allowed": prediction == "Normal"
    }

@app.get("/user/{user_id}")
async def get_user_data(user_id: str):
    """Get user data for demo verification"""
    if db is None:
        # Test mode - return simulated data
        return {
            "email": "test@example.com",
            "last_ip": "127.0.0.1",
            "last_device": "Mozilla/5.0 (Test Browser)",
            "last_txn_time": datetime.now().isoformat(),
            "txn_count_24h": 1,
            "test_mode": True,
            "message": "Firebase not configured - showing test data"
        }
    
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_doc.to_dict()

@app.post("/register-user")
async def register_user(request: Request):
    """Register new user in Firestore"""
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        data = await request.json()
        uid = data.get("uid")
        email = data.get("email")
        
        if not uid or not email:
            raise HTTPException(status_code=400, detail="Missing uid or email")
        
        # Create user document
        user_ref = db.collection("users").document(uid)
        user_data = {
            "email": email,
            "last_ip": None,
            "last_device": None,
            "last_txn_time": None,
            "txn_count_24h": 0,
            "ip_change_count": 0,
            "device_change_count": 0
        }  
        user_ref.set(user_data)
        return {"success": True, "message": "User registered successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")
