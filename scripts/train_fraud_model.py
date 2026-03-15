import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


df = pd.read_csv("../data/creditcard.csv")
training_df = pd.DataFrame()
training_df["order_amount"] = df.Amount

np.random.seed(42)
is_fraud = df.Class == 1

training_df["orders_last_24h"] = np.where(
    is_fraud,
    np.random.poisson(lam=8, size=len(df)),
    np.random.poisson(lam=1.5, size=len(df)),
)
training_df.orders_last_24h = training_df.orders_last_24h.clip(0, 20)

training_df["address_mismatch"] = np.where(
    is_fraud,
    np.random.choice([0, 1], size=len(df), p=[0.6, 0.4]),
    np.random.choice([0, 1], size=len(df), p=[0.85, 0.15]),
)

training_df["country_mismatch"] = np.where(
    is_fraud,
    np.random.choice([0, 1], size=len(df), p=[0.3, 0.7]),
    np.random.choice([0, 1], size=len(df), p=[0.99, 0.01]),
)

training_df["account_age_min"] = np.where(
    is_fraud,
    np.where(
        np.random.rand(len(df)) < 0.9,
        np.random.randint(1, 1440, size=len(df)),
        np.random.randint(1440, 10000, size=len(df)),
    ),
    np.where(
        np.random.rand(len(df)) < 0.2,
        np.random.randint(1, 1440, size=len(df)),
        np.random.randint(1440, 525600, size=len(df)),
    ),
)

X = training_df
y = df.Class

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

sm = SMOTE(random_state=42, sampling_strategy=0.1)
X_train_res, y_train_res = sm.fit_resample(X_train, y_train)

scaler = StandardScaler()
X_train_res_scaled = scaler.fit_transform(X_train_res)

model = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
model.fit(X_train_res_scaled, y_train_res)

X_test_scaled = scaler.transform(X_test)
y_probs = model.predict_proba(X_test_scaled)[:, 1]
y_pred = (y_probs > 0.7).astype(int)

feat_imp = pd.Series(model.feature_importances_, index=X.columns)
print(f"FEATURE IMPORTANCES:\n{feat_imp.sort_values(ascending=False)}\n")
print(f"CLASSIFICATION REPORT:\n{classification_report(y_test, y_pred, target_names=["Legit", "Fraud"])}")

joblib.dump(model, "../app/ml_models/fraud_check_model/fraud_model.joblib")
joblib.dump(scaler, "../app/ml_models/fraud_check_model/scaler.joblib")