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



Real-world performance may vary due to noisy data

Architecture matches real fraud detection pipelines
