import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# 1. Load dataset
data = pd.read_csv("fraud_transactions_clean.csv")

# 2. Separate features and label
X = data.drop("label", axis=1)
y = data["label"]

# 3. Train-test split (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)
import joblib

joblib.dump(model, "fraud_model.pkl")
print("Model saved as fraud_model.pkl")

# 5. Make predictions
y_pred = model.predict(X_test)

# 6. Evaluate model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
