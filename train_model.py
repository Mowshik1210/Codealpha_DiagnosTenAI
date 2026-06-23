import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

os.makedirs("models", exist_ok=True)

datasets = [
    ("datasets/heart.csv", "target", "heart.pkl"),
    ("datasets/diabetes.csv", "Outcome", "diabetes.pkl"),
    ("datasets/breast cancer.csv", "diagnosis", "breast_cancer.pkl"),
    ("datasets/Parkinson's Disease.csv", "status", "parkinsons.pkl"),
    ("datasets/chronic kidney.csv", "classification", "kidney.pkl"),
    ("datasets/liver disease.csv", "Dataset", "liver.pkl"),
    ("datasets/lung cancer.csv", "LUNG_CANCER", "lung.pkl"),
    ("datasets/brain stroke.csv", "stroke", "stroke.pkl"),
    ("datasets/thyroid disease.csv", "Recurred", "thyroid.pkl"),
    ("datasets/Alzheimer's Disease.csv", "Diagnosis", "alzheimers.pkl"),
]

for csv_file, target_col, model_name in datasets:

    print(f"Training {model_name}")

    df = pd.read_csv(csv_file)

    # Clean text columns
    for col in df.columns:
        if df[col].dtype == "object":
           df[col] = df[col].astype(str).str.strip()

    # Remove non-predictive identifier columns
    for col in list(df.columns):
        if col.lower() in ["name", "id", "patient_id","patientid", "record_id","recordid","name", "date", "timestamp","doctorincharge","doctor_in_charge"]:
            df.drop(col, axis=1, inplace=True)

    # Remove unnamed columns
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # Remove ID column
    if "id" in df.columns:
        df.drop("id", axis=1, inplace=True)

    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    print(f"Dataset Shape: {df.shape}")

    df = df.ffill()

    # Remove completely empty rows
    df = df.dropna(how="all")

    if target_col not in df.columns:
        print(f"Target column missing in {csv_file}")
        continue

    X = df.drop(columns=[target_col])

    y = df[target_col].astype(str).str.strip()

    label_encoders = {}

    for col in X.columns:
        if X[col].dtype == "object":
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            label_encoders[col] = le

    if y.dtype == "object":
        le_target = LabelEncoder()
        y = le_target.fit_transform(y.astype(str))
    else:
        le_target = None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)

    print(f"Accuracy: {accuracy:.4f}")

    joblib.dump({
        "model": model,
        "columns": X.columns.tolist(),
        "encoders": label_encoders,
        "target_encoder": le_target
    }, f"models/{model_name}")

print("All models trained successfully.")