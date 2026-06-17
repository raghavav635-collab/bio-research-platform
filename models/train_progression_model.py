import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

df = pd.read_csv("data/patient_data.csv")

df = df[df["Progression to Alzheimer's Disease"].notna()].copy()

df["Progression"] = df["Progression to Alzheimer's Disease"].map({
    "Yes": 1,
    "No": 0
})

df["APOE4"] = df["APOE4"].map({
    "Yes": 1,
    "No": 0
})

features = [
    "Age",
    "MMSE",
    "CSF Amyloid (pg/mL)",
    "CSF Total tau (pg/mL)",
    "CSF Phosphorylated tau (pg/mL)",
    "APOE4"
]

X = df[features]
y = df["Progression"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print(classification_report(y_test, predictions))

joblib.dump(model, "models/progression_model.pkl")

print("Model saved successfully")