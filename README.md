🚨 Fraud Detection ML Model

This repository includes a machine learning–based fraud detection system trained on a clean synthetic dataset and exposed via a backend API.

🔹 Model Overview

Algorithm: Random Forest Classifier

Dataset Size: 10,000 transactions

Fraud Ratio: 20% (intentionally higher for better learning)

Output: Fraud / Normal classification

The model does not consume raw IPs or device names directly.
Instead, it uses risk-based features derived from backend logic.

🔹 Input Features (Model Contract)

Backend must send data in this exact format:

{
  "amount": 3000,
  "is_mal_ip": 1,
  "is_mal_device": 1,
  "odd_time": 1,
  "txn_count_24h": 5
}

Feature Meaning:

amount: Transaction amount

is_mal_ip: 1 if IP is suspicious (blacklist / reputation check)

is_mal_device: 1 if device was flagged previously

odd_time: 1 if transaction occurs at unusual hours (e.g., 12AM–5AM)

txn_count_24h: Number of transactions by user in last 24 hours

🔹 How Real Data Is Used

Raw data (IP, device ID, timestamp) is first processed by backend rules:

Example:

{
  "ip": "185.220.101.4",
  "device_id": "android_emulator",
  "timestamp": "2026-01-13 02:30",
  "amount": 8200
}


Converted into ML input:

{
  "amount": 8200,
  "is_mal_ip": 1,
  "is_mal_device": 1,
  "odd_time": 1,
  "txn_count_24h": 7
}


This is then passed to the ML model.

🔹 How to Run the Model (Backend)
1. Install dependencies
pip install -r requirements.txt

2. Start API server
python -m uvicorn app:app --reload


Server runs at:

http://127.0.0.1:8000


Swagger UI:

http://127.0.0.1:8000/docs

🔹 API Endpoint

POST /predict

Request body:

{
  "amount": 2000,
  "is_mal_ip": 0,
  "is_mal_device": 1,
  "odd_time": 1,
  "txn_count_24h": 4
}


Response:

{
  "prediction": "Fraud"
}

🔹 Model Training (Optional)

To retrain the model:

python train_model.py


This regenerates:

fraud_model.pkl



Another explanation or example of how to use the model 
🔹 Frontend / Backend Integration Logic (Real Data Flow)

The fraud detection model does not consume raw identifiers such as IP addresses or device names.
Instead, the system follows a two‑layer approach:

Rule / Risk Extraction Layer

Machine Learning Classification Layer

🔹 Step 1: Raw Transaction Data (Frontend → Backend)

Frontend sends raw (simulated) transaction data:

{
  "user_id": "user_123",
  "ip_address": "185.220.101.4",
  "device_id": "android_emulator_x86",
  "timestamp": "2026-01-13T02:30:00",
  "amount": 8200
}


This data is not directly sent to the ML model.

🔹 Step 2: Risk Feature Derivation (Backend Logic)

Backend processes raw data using simple rule‑based logic:

def preprocess_transaction(txn):
    return {
        "amount": txn["amount"],
        "is_mal_ip": 1 if txn["ip_address"] in MALICIOUS_IP_LIST else 0,
        "is_mal_device": 1 if txn["device_id"] in FLAGGED_DEVICES else 0,
        "odd_time": 1 if txn["timestamp"].hour < 5 else 0,
        "txn_count_24h": get_txn_count_last_24h(txn["user_id"])
    }


This step simulates:

IP reputation systems

Device trust history

Time‑based anomaly detection

Transaction velocity checks

🔹 Step 3: Model‑Ready Input

The derived features are passed to the ML model:

{
  "amount": 8200,
  "is_mal_ip": 1,
  "is_mal_device": 1,
  "odd_time": 1,
  "txn_count_24h": 7
}


This structure matches the model training schema exactly.

🔹 Step 4: Fraud Prediction

Backend calls the ML model:

prediction = model.predict(features)


Model output:

1 → Fraud

0 → Normal

Mapped to user‑friendly response:

{
  "prediction": "Fraud"
}

🔹 Why This Design Is Correct

Raw identifiers are high‑cardinality and unstable

Risk features are stable, explainable, and scalable

This architecture mirrors real financial fraud pipelines

ML remains decoupled from business logic

🔹 Important Notes for Team Usage

Feature names and order must not change

Backend owns data preprocessing

ML model only performs classification

Dataset is synthetic but logic is realistic
