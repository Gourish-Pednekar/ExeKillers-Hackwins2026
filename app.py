from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI()
model = joblib.load("fraud_model.pkl")

@app.post("/predict")
def predict(txn: dict):
    df = pd.DataFrame([txn])
    pred = model.predict(df)[0]
    return {"prediction": "Fraud" if pred == 1 else "Normal"}
