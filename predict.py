import pandas as pd
import joblib

# Load saved model
model = joblib.load("fraud_model.pkl")

def predict_transaction(transaction):
    """
    transaction: dict
      Example:
      {
          "amount": 2000,
          "is_mal_ip": 0,
          "is_mal_device": 1,
          "odd_time": 0,
          "txn_count_24h": 3
      }
    """
    df = pd.DataFrame([transaction])
    pred = model.predict(df)[0]
    return "Fraud" if pred == 1 else "Normal"

if __name__ == "__main__":
    txn = {
        "amount": 2000,
        "is_mal_ip": 0,
        "is_mal_device": 1,
        "odd_time": 1,
        "txn_count_24h": 4
    }
    print("Prediction:", predict_transaction(txn))
