import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

# Get project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load dataset
file_path = BASE_DIR / "core" / "diabetes.csv"
data = pd.read_csv(file_path)

# Prepare data
X = data.drop("Outcome", axis=1)
y = data["Outcome"]

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Prediction function
def predict_disease(input_data):
    result = model.predict([input_data])
    return "High Risk" if result[0] == 1 else "Low Risk"